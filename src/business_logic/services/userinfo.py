from typing import Any, Optional

from jwt.exceptions import PyJWTError

from src.business_logic.services.jwt_token import JWTService
from src.data_access.postgresql.repositories.client import ClientRepository
from src.data_access.postgresql.repositories.persistent_grant import (
    PersistentGrantRepository,
)
from src.data_access.postgresql.repositories.user import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession


class UserInfoService:
    def __init__(
        self,
        session: AsyncSession,
        user_repo: UserRepository,
        client_repo: ClientRepository,
        persistent_grant_repo: PersistentGrantRepository,
        jwt: JWTService = JWTService(),
    ) -> None:
        self.jwt = jwt
        self.authorization: Optional[str] = None
        self.user_repo = user_repo
        self.client_repo = client_repo
        self.persistent_grant_repo = persistent_grant_repo
        self.session = session

    async def get_user_info(
        self,
    ) -> dict[str, Any]:
        token = self.authorization
        decoded_token = await self.jwt.decode_token_no_aud_iss_check(token=token)
        try:
            sub = int(decoded_token["sub"])
        except KeyError:
            raise KeyError("No parameter 'sub' in token")

        claims_dict = await self.user_repo.get_claims(id=sub)
        if not claims_dict.get("sub", False):
            claims_dict["sub"] = str(sub)

        response = {}
        if (
            not decoded_token.get("scope", False)
            or "openid" in decoded_token["scope"]
        ):
            response = {
                "sub": claims_dict.get("sub", None),
                "aud": claims_dict.get("aud", None),
                "exp": claims_dict.get("exp", None),
                "iss": claims_dict.get("iss", None),
                "iat": claims_dict.get("iat", None),
            }
            if not decoded_token.get("scope", False):
                return response

        if "profile" in decoded_token["scope"]:
            response = response | {
                "name": claims_dict.get("name", None),
                "given_name": claims_dict.get("given_name", None),
                "family_name": claims_dict.get("family_name", None),
                "middle_name": claims_dict.get("middle_name", None),
                "nickname": claims_dict.get("nickname", None),
                "preferred_username": claims_dict.get(
                    "preferred_username", None
                ),
                "profile": claims_dict.get("profile", None),
                "picture": claims_dict.get("picture", None),
                "website": claims_dict.get("website", None),
                "gender": claims_dict.get("gender", None),
                "birthdate": claims_dict.get("birthdate", None),
                "zoneinfo": claims_dict.get("zoneinfo", None),
                "locale": claims_dict.get("locale", None),
                "phone_number": claims_dict.get("phone_number", None),
                "phone_number_verified": claims_dict.get(
                    "phone_number_verified", None
                ),
                "address": claims_dict.get("address", None),
                "updated_at": claims_dict.get("updated_at", None),
            }
        if "email" in decoded_token["scope"]:
            response = response | {
                "email": claims_dict.get("email", None),
                "email_verified": claims_dict.get("email_verified", None),
            }

        return response

    async def get_user_info_jwt(self) -> str:
        result = await self.get_user_info()
        token = await self.jwt.encode_jwt(payload=result)
        return token
