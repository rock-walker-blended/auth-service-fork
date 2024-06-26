from __future__ import annotations
import time
import uuid
from src.business_logic.get_tokens.dto import RequestTokenModel, ResponseTokenModel
from src.business_logic.jwt_manager.dto import (
    AccessTokenPayload,
    IdTokenPayload,
    RefreshTokenPayload
)
from src.dyna_config import DOMAIN_NAME
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from src.business_logic.common.interfaces import ValidatorProtocol
    from src.business_logic.jwt_manager.interfaces import JWTManagerProtocol
    from src.data_access.postgresql.repositories import PersistentGrantRepository


class DeviceCodeTokenService:
    def __init__(
            self,
            session: AsyncSession,
            device_code_validator: ValidatorProtocol,
            grant_exp_validator: ValidatorProtocol,
            client_validator: ValidatorProtocol,
            redirect_uri_validator: ValidatorProtocol,
            jwt_manager: JWTManagerProtocol,
            persistent_grant_repo: PersistentGrantRepository
    ) -> None:
        self._session = session
        self._device_code_validator = device_code_validator
        self._client_validator = client_validator
        self._redirect_uri_validator = redirect_uri_validator
        self._grant_expiration_validator = grant_exp_validator
        self._jwt_manager = jwt_manager
        self._persistent_grant_repo = persistent_grant_repo

    async def get_tokens(self, request_data: RequestTokenModel) -> ResponseTokenModel:
        await self._client_validator(request_data.client_id)
        await self._device_code_validator(request_data.device_code, request_data.client_id, request_data.grant_type)
        await self._redirect_uri_validator(request_data.redirect_uri, request_data.client_id)

        grant = await self._persistent_grant_repo.get_grant(
            grant_type=request_data.grant_type, 
            grant_data=request_data.device_code
        )

        await self._grant_expiration_validator(grant.expiration)

        user_id = grant.user_id
        current_unix_time = int(time.time())
        aud = grant.scope
        access_token = await self._get_access_token(request_data=request_data, user_id=user_id, unix_time=current_unix_time, aud=aud)
        refresh_token = await self._get_refresh_token(request_data=request_data)
        id_token = await self._get_id_token(request_data=request_data, user_id=user_id, unix_time=current_unix_time)

        await self._persistent_grant_repo.delete_grant(grant=grant)
        await self._persistent_grant_repo.create_grant(
            client_id=grant.client_id, 
            grant_data=refresh_token,
            user_id=user_id,
            grant_type_id=2,
            expiration_time=current_unix_time + 84700,
            scope=aud
        )
        await self._session.commit()

        return ResponseTokenModel(
            access_token=access_token,
            refresh_token=refresh_token,
            id_token=id_token,
            token_type='Bearer',
            expires_in=600,
            refresh_expires_in=1800
        )

    async def _get_access_token(self, request_data: RequestTokenModel, user_id: int, unix_time: int, aud:list[str]) -> str:
        payload = AccessTokenPayload(
            sub=user_id,
            iss=DOMAIN_NAME,
            client_id=request_data.client_id,
            iat=unix_time,
            exp=unix_time + 600,
            aud=aud,
            jti=str(uuid.uuid4()),
            acr=0,
        )
        return self._jwt_manager.encode(payload=payload, algorithm='RS256')

    async def _get_refresh_token(self, request_data: RequestTokenModel) -> str:
        payload = RefreshTokenPayload(
            jti=str(uuid.uuid4())
        )
        return self._jwt_manager.encode(payload=payload, algorithm='RS256') 

    async def _get_id_token(self, request_data: RequestTokenModel, user_id: int, unix_time: int) -> str:
        payload = IdTokenPayload(
            sub=user_id,
            iss=DOMAIN_NAME,
            client_id=request_data.client_id,
            iat=unix_time,
            exp=unix_time + 600,
            jti=str(uuid.uuid4()),
            acr=0,
        )
        return self._jwt_manager.encode(payload=payload, algorithm='RS256')
