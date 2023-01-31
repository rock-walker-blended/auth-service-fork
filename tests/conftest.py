import mock
import os

mock.patch(
    "fastapi_cache.decorator.cache", lambda *args, **kwargs: lambda f: f
).start()

from typing import AsyncIterator

import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from pytest_postgresql import factories
from pytest_postgresql.janitor import DatabaseJanitor
import pytest
import asyncio

from src.main import get_application

from src.business_logic.services.authorization import AuthorizationService
from src.business_logic.services.endsession import EndSessionService
from src.business_logic.services.userinfo import UserInfoServices
from src.data_access.postgresql.repositories import (
    ClientRepository,
    UserRepository,
    PersistentGrantRepository,
)
from src.business_logic.services.password import PasswordHash
from src.business_logic.services.jwt_token import JWTService
from src.business_logic.services.introspection import IntrospectionServies
from src.business_logic.services.tokens import TokenService
from src.business_logic.services.login_form_service import LoginFormService

from src.di.providers import (
    provide_auth_service_stub,
    provide_endsession_service_stub,
    provide_introspection_service_stub,
    provide_token_service_stub,
    provide_userinfo_service_stub,
    provide_login_form_service_stub,
)

from tests.overrides.override_functions import (
    nodepends_provide_auth_service_override,
    nodepends_provide_endsession_servise_override,
    nodepends_provide_introspection_service_override,
    nodepends_provide_token_service_override,
    nodepends_provide_userinfo_service_override,
    nodepends_provide_login_form_service_override,
)

from src.di import Container


TEST_SQL_DIR = os.path.dirname(os.path.abspath(__file__)) + "/test_sql"

test_db = factories.postgresql_proc(
    port=5463,
    dbname="test_db",
    load=[
        TEST_SQL_DIR + "/table_clients.sql",
        TEST_SQL_DIR + "/table_users.sql",
        TEST_SQL_DIR + "/table_user_logins.sql",
        TEST_SQL_DIR + "/table_client_id_restrictions.sql",
        TEST_SQL_DIR + "/table_client_claims.sql",
        TEST_SQL_DIR + "/table_client_redirect_uris.sql",
        TEST_SQL_DIR + "/table_client_scopes.sql",
        TEST_SQL_DIR + "/table_client_cors_origins.sql",
        TEST_SQL_DIR + "/table_user_claims.sql",
        TEST_SQL_DIR + "/table_identity_resources.sql",
        TEST_SQL_DIR + "/table_roles.sql",
        TEST_SQL_DIR + "/table_groups.sql",
        TEST_SQL_DIR + "/table_api_resources.sql",
        TEST_SQL_DIR + "/table_api_scopes.sql",
        TEST_SQL_DIR + "/table_api_claims.sql",
        TEST_SQL_DIR + "/table_api_scope_claims.sql",
        TEST_SQL_DIR + "/table_client_grant_types.sql",
        TEST_SQL_DIR + "/table_api_secrets.sql",
        TEST_SQL_DIR + "/table_persistent_grants.sql",
        TEST_SQL_DIR + "/table_identity_claims.sql",
        TEST_SQL_DIR + "/table_client_secrets.sql",
        TEST_SQL_DIR + "/table_client_post_logout_redirect_uris.sql",
        TEST_SQL_DIR + "/table_permissions.sql",
        TEST_SQL_DIR + "/table_permissions_groups.sql",
        TEST_SQL_DIR + "/table_permissions_roles.sql",
        TEST_SQL_DIR + "/table_users_groups.sql",
        TEST_SQL_DIR + "/table_users_roles.sql",
    ],
)


@pytest_asyncio.fixture(scope="session")
async def engine(test_db):
    pg_host = test_db.host
    pg_port = test_db.port
    pg_user = test_db.user
    pg_password = test_db.password
    pg_db = test_db.dbname

    with DatabaseJanitor(
        pg_user, pg_host, pg_port, pg_db, test_db.version, pg_password
    ):
        db_uri = f"postgresql+asyncpg://{pg_user}:@{pg_host}:{pg_port}/{pg_db}"
        engine = create_async_engine(db_uri)
        yield engine


@pytest_asyncio.fixture(scope="session")
async def connection(engine):
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture
async def app() -> FastAPI:
    app = get_application()

    # override stubs to use test db_uri
    app.dependency_overrides[
        provide_auth_service_stub
    ] = nodepends_provide_auth_service_override
    app.dependency_overrides[
        provide_endsession_service_stub
    ] = nodepends_provide_endsession_servise_override
    app.dependency_overrides[
        provide_introspection_service_stub
    ] = nodepends_provide_introspection_service_override
    app.dependency_overrides[
        provide_token_service_stub
    ] = nodepends_provide_token_service_override
    app.dependency_overrides[
        provide_userinfo_service_stub
    ] = nodepends_provide_userinfo_service_override
    app.dependency_overrides[
        provide_login_form_service_stub
    ] = nodepends_provide_login_form_service_override

    return app


@pytest_asyncio.fixture
async def client(app: FastAPI, connection) -> AsyncIterator[AsyncClient]:
    async with AsyncClient(
        app=app,
        base_url="http://testserver",
        headers={"Content-Type": "application/json"},
    ) as client:
        yield client


@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def authorization_service(engine) -> AuthorizationService:
    auth_service = AuthorizationService(
        client_repo=ClientRepository(engine),
        user_repo=UserRepository(engine),
        persistent_grant_repo=PersistentGrantRepository(engine),
        password_service=PasswordHash(),
    )
    return auth_service


@pytest_asyncio.fixture
async def end_session_service(engine) -> EndSessionService:
    end_sess_service = EndSessionService(
        client_repo=ClientRepository(engine),
        persistent_grant_repo=PersistentGrantRepository(engine),
        jwt_service=JWTService(),
    )
    return end_sess_service


@pytest_asyncio.fixture
async def introspection_service(engine) -> IntrospectionServies:
    intro_service = IntrospectionServies(
        client_repo=ClientRepository(engine),
        persistent_grant_repo=PersistentGrantRepository(engine),
        user_repo=UserRepository(engine),
        jwt=JWTService(),
    )
    return intro_service


@pytest_asyncio.fixture
async def user_info_service(engine) -> UserInfoServices:
    user_info = UserInfoServices(
        jwt=JWTService(),
        client_repo=ClientRepository(engine),
        persistent_grant_repo=PersistentGrantRepository(engine),
        user_repo=UserRepository(engine),
    )
    return user_info


@pytest_asyncio.fixture
async def token_service(engine) -> TokenService:
    tk_service = TokenService(
        client_repo=ClientRepository(engine),
        persistent_grant_repo=PersistentGrantRepository(engine),
        user_repo=UserRepository(engine),
        jwt_service=JWTService(),
    )
    return tk_service


@pytest_asyncio.fixture
async def login_form_service(engine) -> LoginFormService:
    login_service = LoginFormService(
        client_repo=ClientRepository(engine),
    )
    return login_service
