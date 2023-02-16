import logging
from logging.config import dictConfig

from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi.staticfiles import StaticFiles
from redis import asyncio as aioredis
from starlette.middleware.cors import CORSMiddleware
from pathlib import Path
from sqladmin import Admin

from src.presentation.api.middleware.authorization_validation import (
    AuthorizationMiddleware,
)
from src.presentation.api.middleware.access_token_validation import (
    AccessTokenMiddleware,
)

from src.presentation.api import router
from src.di import Container
from src.dyna_config import DB_MAX_CONNECTION_COUNT, DB_URL, REDIS_URL
from src.presentation.admin_ui.controllers import (
    SeparationLine,
    AdminAuthController,
    ClientAdminController,
    UserAdminController,
    PersistentGrantAdminController,
    RoleAdminController,
    UserClaimAdminController,
    TypesUserClaimAdminController,
    PersistentGrantTypeAdminController,
    AccessTokenTypeAdminController,
    ProtocolTypeController,
    RefreshTokenUsageTypeController,
    RefreshTokenExpirationTypeController,
    ApiResourceAdminController,
    ApiSecretAdminController,
    ApiSecretTypeAdminController,
    ApiClaimAdminController,
    ApiClaimTypeAdminController,
    ApiScopeAdminController,
    ApiScopeClaimAdminController,
    ApiScopeClaimTypeAdminController,
    IdentityResourceAdminController, 
    IdentityClaimAdminController,
    PermissionAdminController, 
    GroupAdminController,
    ClientSecretController,
    ClientGrantTypeController,
    ClientRedirectUriController,
    ClientCorsOriginController,
    ClientPostLogoutRedirectUriController,
    ClientClaimController,
    ClientIdRestrictionController,
    DeviceAdminController,
)
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
    provide_device_repo,
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
    provide_admin_auth_service,
    provide_admin_auth_service,
    provide_device_service_stub,
    provide_device_service
)

import logging
from src.log import LOGGING_CONFIG


logger = logging.getLogger(__name__)


def get_application(test=False) -> FastAPI:
    # configure logging
    dictConfig(LOGGING_CONFIG)

    application = FastAPI()
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.add_middleware(AuthorizationMiddleware)
    application.add_middleware(AccessTokenMiddleware)

    setup_di(application)
    container = Container()
    container.db()
    application.container = container

    application.include_router(router)
    application.mount(
        "/static",
        StaticFiles(directory="src/presentation/api/templates/static"),
        name="static",
    )

    return application


# TODO: move the creation of RSA keys here.
def setup_di(app: FastAPI) -> None:
    db_engine = provide_db(
        database_url=DB_URL, max_connection_count=DB_MAX_CONNECTION_COUNT
    )

    # Register admin-ui controllers on application start-up.
    admin = Admin(
        app,
        db_engine,
        authentication_backend=AdminAuthController(
            secret_key="1234",
            auth_service=provide_admin_auth_service(
                user_repo=provide_user_repo(db_engine),
                password_service=provide_password_service(),
                jwt_service=provide_jwt_service(),
            ),
        ),
    )
    # Client 
    admin.add_view(ClientAdminController)
    admin.add_view(AccessTokenTypeAdminController)
    admin.add_view(ProtocolTypeController)
    admin.add_view(RefreshTokenUsageTypeController)
    admin.add_view(RefreshTokenExpirationTypeController)
    admin.add_view(ClientSecretController)
    admin.add_view(ClientGrantTypeController)
    admin.add_view(ClientRedirectUriController)
    admin.add_view(ClientCorsOriginController)
    admin.add_view(ClientPostLogoutRedirectUriController)
    admin.add_view(ClientClaimController)
    admin.add_view(ClientIdRestrictionController)
    admin.add_view(DeviceAdminController)
    admin.add_view(SeparationLine)

    # User/UserClaim
    admin.add_view(UserAdminController)
    admin.add_view(UserClaimAdminController)
    admin.add_view(TypesUserClaimAdminController)
    admin.add_view(SeparationLine)
    
    # Other
    admin.add_view(RoleAdminController)
    admin.add_view(GroupAdminController)
    admin.add_view(PermissionAdminController)
    admin.add_view(SeparationLine)

    #Grants
    admin.add_view(PersistentGrantAdminController)
    admin.add_view(PersistentGrantTypeAdminController)
    admin.add_view(SeparationLine)

    #ApiResourses
    admin.add_view(ApiResourceAdminController)
    admin.add_view(ApiSecretAdminController)
    admin.add_view(ApiSecretTypeAdminController)
    admin.add_view(ApiClaimAdminController)
    admin.add_view(ApiClaimTypeAdminController)
    admin.add_view(ApiScopeAdminController)
    admin.add_view(ApiScopeClaimAdminController)
    admin.add_view(ApiScopeClaimTypeAdminController)
    admin.add_view(SeparationLine)
    
    #Identity Resourses
    admin.add_view(IdentityResourceAdminController)
    admin.add_view(IdentityClaimAdminController)
    admin.add_view(SeparationLine)
    
    


    nodepends_provide_auth_service = lambda: provide_auth_service(
        client_repo=provide_client_repo(db_engine),
        user_repo=provide_user_repo(db_engine),
        persistent_grant_repo=provide_persistent_grant_repo(db_engine),
        device_repo=provide_device_repo(db_engine),
        password_service=provide_password_service(),
        jwt_service=provide_jwt_service(),
    )
    app.dependency_overrides[
        provide_auth_service_stub
    ] = nodepends_provide_auth_service

    nodepends_provide_endsession_servise = lambda: provide_endsession_service(
        client_repo=provide_client_repo(db_engine),
        persistent_grant_repo=provide_persistent_grant_repo(db_engine),
        jwt_service=provide_jwt_service(),
    )
    app.dependency_overrides[
        provide_endsession_service_stub
    ] = nodepends_provide_endsession_servise

    nodepends_provide_introspection_service = (
        lambda: provide_introspection_service(
            jwt=provide_jwt_service(),
            user_repo=provide_user_repo(db_engine),
            client_repo=provide_client_repo(db_engine),
            persistent_grant_repo=provide_persistent_grant_repo(db_engine),
        )
    )
    app.dependency_overrides[
        provide_introspection_service_stub
    ] = nodepends_provide_introspection_service

    nodepends_provide_token_service = lambda: provide_token_service(
        jwt_service=provide_jwt_service(),
        user_repo=provide_user_repo(db_engine),
        client_repo=provide_client_repo(db_engine),
        persistent_grant_repo=provide_persistent_grant_repo(db_engine),
        device_repo=provide_device_repo(db_engine)
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

    nodepends_provide_device_service = lambda: provide_device_service(
        client_repo=provide_client_repo(db_engine),
        device_repo=provide_device_repo(db_engine)
    )
    app.dependency_overrides[
        provide_device_service_stub
    ] = nodepends_provide_device_service


app = get_application()


# TODO: Move this code to setup_di() function.
LOCAL_REDIS_URL = "redis://127.0.0.1:6379"  # move to .env file


# Redis activation
@app.on_event("startup")
async def startup():
    logger.info("Creating Redis connection with DataBase.")
    redis = aioredis.from_url(REDIS_URL, encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    logger.info("Created Redis connection with DataBase.")
