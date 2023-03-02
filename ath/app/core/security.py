from datetime import datetime, timedelta
from typing import Any, Literal, Optional, Union

from jose import jwt
from passlib.context import CryptContext
from pydantic import ValidationError

from app.core.config import Settings, get_settings
from app.schemas.auth import TokenPayload

settings: Settings = get_settings()

pwd_context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM: Literal["HS256"] = "HS256"


def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    if expires_delta:
        expire: datetime = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt: str = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def encode_token(token_payload: TokenPayload) -> str:
    if token_payload.exp is None:
        token_payload.exp = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    token: str = jwt.encode(
        token_payload.dict(), settings.SECRET_KEY, algorithm=ALGORITHM
    )
    return token


def decode_token(token: str) -> Optional[TokenPayload]:
    try:
        payload: dict[str, Any] = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[ALGORITHM]
        )
        token_data: Optional[TokenPayload] = TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        token_data = None
    return token_data
