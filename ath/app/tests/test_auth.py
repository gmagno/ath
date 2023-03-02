from typing import Any, Optional

from app.core import security
from app.schemas.auth import Token, TokenPayload
from fastapi import status
from httpx import AsyncClient, Response


async def test_auth_generate_access_token(
    async_client: AsyncClient, client_key_secret: tuple[str, str]
) -> None:
    client_key, client_secret = client_key_secret
    response: Response = await async_client.post(
        "v1/auth/token",
        data={
            "grant_type": "client_credentials",
            "client_id": client_key,
            "client_secret": client_secret,
        },
    )
    response_data: Any = response.json()
    token: Token = Token(**response_data)

    token_payload: Optional[TokenPayload] = security.decode_token(token.access_token)

    assert response.status_code == status.HTTP_200_OK
    assert token_payload is not None
    assert token_payload.sub == client_key


async def test_auth_use_access_token(
    async_client: AsyncClient, valid_client_token_payload: TokenPayload
) -> None:
    jwt_token: str = security.encode_token(valid_client_token_payload)
    response: Response = await async_client.post(
        "v1/auth/test-token",
        headers={"Authorization": f"Bearer {jwt_token}"},
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
