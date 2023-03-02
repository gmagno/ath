import asyncio
import logging
import uuid
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.expression import func
from sqlmodel import delete

from app.schemas.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

logger: logging.Logger = logging.getLogger(__name__)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, id: uuid.UUID) -> Optional[ModelType]:
        stmt = select(self.model).where(self.model.id == id)
        result = await db.execute(stmt)
        entry = result.scalar_one_or_none()
        return entry

    async def get_multi(
        self,
        db: AsyncSession,
        skip: Optional[int] = 0,
        limit: Optional[int] = None,
    ) -> List[ModelType]:
        stmt = select(self.model).offset(skip)
        if limit:
            stmt = stmt.limit(limit)
        result = await db.execute(stmt)
        entries = result.scalars()
        return list(entries)

    async def create(
        self,
        db: AsyncSession,
        obj_in: CreateSchemaType,
        flush: bool = True,
        commit: bool = False,
    ) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        if flush:
            await db.flush()
        if commit:
            await db.commit()
        return db_obj

    async def create_multi(
        self,
        db: AsyncSession,
        objs_in: list[CreateSchemaType],
        flush: bool = True,
        commit: bool = False,
    ) -> List[ModelType]:
        futs = [self.create(db=db, obj_in=obj_in, flush=False) for obj_in in objs_in]
        db_objs = await asyncio.gather(*futs)
        if flush:
            await db.flush()
        if commit:
            await db.commit()
        return db_objs

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
        flush: bool = True,
        commit: bool = False
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        if flush:
            await db.flush()
        if commit:
            await db.commit()
        return db_obj

    async def delete(self, db: AsyncSession, *, id: uuid.UUID) -> Optional[ModelType]:
        obj = await db.get(self.model, id)
        if obj is not None:
            await db.delete(obj)
        return obj

    async def delete_all(self, db: AsyncSession) -> List[ModelType]:
        statement = delete(self.model)
        result = await db.execute(statement)
        entries = result.scalars().all()
        return entries

    async def get_random(self, db: AsyncSession) -> Optional[ModelType]:
        stmt = select(self.model).order_by(func.random()).limit(1)
        result = await db.execute(stmt)
        entry = result.scalar_one_or_none()
        return entry
