import logging
from fastapi import APIRouter, Depends, HTTPException, Header, Request

from fastapi_cache.decorator import cache
from src.business_logic.cache.key_builders import builder_with_parametr
from fastapi_cache.coder import JsonCoder
from src.config.settings.cache_time import CacheTimeSettings
from fastapi_cache.key_builder import default_key_builder

from src.business_logic.services.userinfo import UserInfoServies

from src.data_access.postgresql.errors.user import ClaimsNotFoundError
from src.presentation.api.models.userinfo import ResponseUserInfoModel
import time
from fastapi.security.api_key import APIKeyHeader
from fastapi.security import HTTPBearer

security = HTTPBearer()


logger = logging.getLogger("is_app")

userinfo_router = APIRouter(
    prefix="/userinfo",
)


@userinfo_router.get(
    "/", response_model=ResponseUserInfoModel, tags=["UserInfo"]
)
@cache(
    expire=CacheTimeSettings.USERINFO,
    coder=JsonCoder,
    key_builder=builder_with_parametr,
)
async def get_userinfo(
    request: Request,
    auth_swagger: str | None = Header(default=None, description="Authorization"),
    userinfo_class: UserInfoServies = Depends(),
):
    try:
        time.sleep(3)
        userinfo_class = userinfo_class
        token = request.headers.get('authorization')

        if token != None:
            userinfo_class.authorization = token
        elif auth_swagger != None:
            userinfo_class.authorization = auth_swagger
        else:
            raise Exception

        logger.info("Collecting Claims from DataBase.")
        return await userinfo_class.get_user_info()

    except ClaimsNotFoundError:
        raise HTTPException(
            status_code=422,
            detail="Claims for user you are looking for does not exist",
        )

    except:
        raise HTTPException(status_code=403, detail="Incorrect Token")


@userinfo_router.get("/jwt", response_model=str, tags=["UserInfo"])
@cache(
    expire=CacheTimeSettings.USERINFO_JWT,
    coder=JsonCoder,
    key_builder=builder_with_parametr,
)
async def get_userinfo_jwt(
    auth: str = Header(default=..., description="Authorization"),
    userinfo_class: UserInfoServies = Depends(),
):
    try:
        userinfo_class = userinfo_class
        userinfo_class.authorization = auth
        result = await userinfo_class.get_user_info_jwt()
        return result

    except ClaimsNotFoundError:
        raise HTTPException(
            status_code=422,
            detail="Claims for user you are looking for does not exist",
        )

    except:
        raise HTTPException(status_code=403, detail="Incorrect Token")


@userinfo_router.get(
    "/get_default_token", response_model=str, tags=["UserInfo"]
)
async def get_default_token():
    try:
        uis = UserInfoServies()
        uis.jwt.set_expire_time(expire_hours=1)
        return uis.jwt.encode_jwt(payload={"sub": "1"})
    except:
        raise HTTPException(status_code=500)


@userinfo_router.get("/decode_token", response_model=dict, tags=["UserInfo"])
async def get_decode_token(token: str):
    try:
        uis = UserInfoServies()
        return uis.jwt.decode_token(token)
    except:
        raise HTTPException(status_code=500)
