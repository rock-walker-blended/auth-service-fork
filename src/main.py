import logging
from logging.config import dictConfig

from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi.staticfiles import StaticFiles
from redis import asyncio as aioredis
from starlette.middleware.cors import CORSMiddleware
from pathlib import Path

from src.presentation.api.middleware.authorization_validation import AuthorizationMiddleware
from src.presentation.api.middleware.access_token_validation import AccessTokenMiddleware

from src.config import LogConfig
from src.presentation.api import router
from src.di.providers import (
    provide_config,
    provide_db,
    provide_auth_service,
    provide_auth_service_stub,
    provide_password_service,
    provide_endsession_service,
    provide_endsession_service_stub,
    provide_client_repo,
    provide_user_repo,
    provide_group_repo,
    provide_role_repo,
    provide_persistent_grant_repo,
    provide_jwt_service,
    provide_introspection_service_stub,
    provide_introspection_service,
    provide_token_service_stub,
    provide_token_service,
    provide_userinfo_service_stub,
    provide_userinfo_service,
    provide_login_form_service_stub,
    provide_login_form_service,
    provide_admin_user_service_stub,
    provide_admin_user_service,
    provide_admin_group_service,
    provide_admin_group_service_stub,
    provide_admin_role_service_stub,
    provide_admin_role_service,
)
from src.di import Container


logger = logging.getLogger("is_app")


def get_application(test=False) -> FastAPI:
    # configure logging
    dictConfig(LogConfig().to_dict)

    application = FastAPI()
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.add_middleware(AuthorizationMiddleware)
    # application.add_middleware(AccessTokenMiddleware)

    setup_di(application)
    container = Container()
    container.db()
    application.container = container
    
    application.include_router(router)
    application.mount(
        "/static",
        StaticFiles(directory="src/presentation/api/templates/static"),
        name="static")

    return application


def setup_di(app: FastAPI) -> None:
    config = provide_config()

    db_engine = provide_db(
        database_url=config.database_url,
        max_connection_count=config.max_connection_count
    )

    nodepends_provide_auth_service = lambda: provide_auth_service(
        client_repo=provide_client_repo(db_engine),
        user_repo=provide_user_repo(db_engine),
        persistent_grant_repo=provide_persistent_grant_repo(db_engine),
        password_service=provide_password_service(),
        jwt_service=provide_jwt_service()
    )
    logger.info(f'{nodepends_provide_auth_service}')

    app.dependency_overrides[
        provide_auth_service_stub
    ] = nodepends_provide_auth_service

    nodepends_provide_endsession_servise = lambda: provide_endsession_service(
        client_repo=provide_client_repo(db_engine),
        persistent_grant_repo=provide_persistent_grant_repo(db_engine),
        jwt_service=provide_jwt_service()
    )

    app.dependency_overrides[
        provide_endsession_service_stub
    ] = nodepends_provide_endsession_servise

    nodepends_provide_introspection_service = lambda: provide_introspection_service(
        jwt=provide_jwt_service(),
        # token_service=provide_token_service(),
        user_repo=provide_user_repo(db_engine),
        client_repo=provide_client_repo(db_engine),
        persistent_grant_repo=provide_persistent_grant_repo(db_engine)
    )

    app.dependency_overrides[
        provide_introspection_service_stub
    ] = nodepends_provide_introspection_service

    nodepends_provide_token_service = lambda: provide_token_service(
        jwt_service=provide_jwt_service(),
        user_repo=provide_user_repo(db_engine),
        client_repo=provide_client_repo(db_engine),
        persistent_grant_repo=provide_persistent_grant_repo(db_engine),
    )

    app.dependency_overrides[
        provide_token_service_stub
    ] = nodepends_provide_token_service

    nodepends_provide_userinfo_service = lambda: provide_userinfo_service(
        jwt=provide_jwt_service(),
        user_repo=provide_user_repo(db_engine),
        client_repo=provide_client_repo(db_engine),
        persistent_grant_repo=provide_persistent_grant_repo(db_engine),
    )

    app.dependency_overrides[
        provide_userinfo_service_stub
    ] = nodepends_provide_userinfo_service

    nodepends_provide_login_form_service = lambda: provide_login_form_service(
        client_repo=provide_client_repo(db_engine)
    )

    app.dependency_overrides[
        provide_login_form_service_stub
    ] = nodepends_provide_login_form_service

    nodepends_provide_admin_user_service = lambda: provide_admin_user_service(
        user_repo=provide_user_repo(db_engine),
    )

    app.dependency_overrides[
        provide_admin_user_service_stub
    ] = nodepends_provide_admin_user_service
    
    nodepends_provide_admin_group_service = lambda: provide_admin_group_service(
        group_repo=provide_group_repo(db_engine),
    )

    app.dependency_overrides[
        provide_admin_group_service_stub
    ] = nodepends_provide_admin_group_service
    
    nodepends_provide_admin_role_service = lambda: provide_admin_role_service(
        role_repo=provide_role_repo(db_engine),
    )
    app.dependency_overrides[
        provide_admin_role_service_stub
    ] = nodepends_provide_admin_role_service


app = get_application()


LOCAL_REDIS_URL = "redis://127.0.0.1:6379"  # move to .env file


# Redis activation
@app.on_event("startup")
async def startup():
    logger.info("Creating Redis connection with DataBase.")
    redis = aioredis.from_url(
        LOCAL_REDIS_URL, encoding="utf8", decode_responses=True
    )
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    logger.info("Created Redis connection with DataBase.")
