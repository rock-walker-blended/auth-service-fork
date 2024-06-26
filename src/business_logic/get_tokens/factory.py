from __future__ import annotations
from typing import TYPE_CHECKING
from src.business_logic.services.scope import ScopeService
from src.business_logic.get_tokens.service_impls import (
    AuthorizationCodeTokenService,
    RefreshTokenGrantService,
    ClientCredentialsTokenService,
    DeviceCodeTokenService,
)
from src.business_logic.get_tokens.validators import (
    ValidatePersistentGrant, 
    ValidateRedirectUri, 
    ValidateGrantByClient,
    ValidateGrantExpired,
    ValidateClientCredentials,
    ValidatePKCECode
)
from src.business_logic.get_tokens.errors import UnsupportedGrantTypeError
from src.business_logic.common.validators import ClientIdValidator, ScopeValidator
from src.data_access.postgresql.repositories import ResourcesRepository
if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from .interfaces import TokenServiceProtocol
    from src.data_access.postgresql.repositories import (
        BlacklistedTokenRepository,
        ClientRepository,
        DeviceRepository,
        PersistentGrantRepository,
        UserRepository,
        CodeChallengeRepository,

    )
    from src.business_logic.jwt_manager.interfaces import JWTManagerProtocol


class TokenServiceFactory:
    def __init__(
            self,
            session: AsyncSession,
            client_repo: ClientRepository,
            persistent_grant_repo: PersistentGrantRepository,
            user_repo: UserRepository,
            device_repo: DeviceRepository,
            jwt_manager: JWTManagerProtocol,
            blacklisted_repo: BlacklistedTokenRepository,
            code_challenge_repo: CodeChallengeRepository,
            scope_service: ScopeService
    ) -> None:
        self._session = session
        self._client_repo = client_repo
        self._persistent_grant_repo = persistent_grant_repo
        self._user_repo = user_repo
        self._device_repo = device_repo
        self._jwt_manager = jwt_manager
        self._blacklisted_repo = blacklisted_repo
        self._code_challenge_repo = code_challenge_repo
        self._scope_service = scope_service

    def get_service_impl(self, grant_type: str) -> TokenServiceProtocol:
        if grant_type == 'authorization_code':
            return AuthorizationCodeTokenService(
                session=self._session,
                grant_validator=ValidatePersistentGrant(persistent_grant_repo=self._persistent_grant_repo),
                redirect_uri_validator=ValidateRedirectUri(client_repo=self._client_repo),
                client_validator=ClientIdValidator(client_repo=self._client_repo),
                code_validator=ValidateGrantByClient(persistent_grant_repo=self._persistent_grant_repo),
                grant_exp_validator=ValidateGrantExpired(),
                pkce_code_validator=ValidatePKCECode(code_challenge_repo=self._code_challenge_repo),
                jwt_manager=self._jwt_manager,
                persistent_grant_repo=self._persistent_grant_repo
            )
        elif grant_type == 'refresh_token':
            return RefreshTokenGrantService(
                session=self._session,
                grant_validator=ValidatePersistentGrant(persistent_grant_repo=self._persistent_grant_repo),
                client_validator=ClientIdValidator(client_repo=self._client_repo),
                refresh_token_validator=ValidateGrantByClient(persistent_grant_repo=self._persistent_grant_repo),
                grant_exp_validator=ValidateGrantExpired(),
                jwt_manager=self._jwt_manager,
                persistent_grant_repo=self._persistent_grant_repo
            )
        elif grant_type == 'client_credentials':
            return ClientCredentialsTokenService(
                session=self._session,
                client_credentials_validator=ValidateClientCredentials(client_repo=self._client_repo),
                scope_validator=ScopeValidator(client_repo=self._client_repo),
                jwt_manager=self._jwt_manager,
                persistent_grant_repo=self._persistent_grant_repo,
                scope_service=ScopeService(
                    resource_repo=ResourcesRepository(session=self._session),
                    session=self._session,
                )
            )
        elif grant_type == 'urn:ietf:params:oauth:grant-type:device_code':
            return DeviceCodeTokenService(
                session=self._session,
                device_code_validator=ValidateGrantByClient(persistent_grant_repo=self._persistent_grant_repo),
                grant_exp_validator=ValidateGrantExpired(),
                client_validator=ClientIdValidator(client_repo=self._client_repo),
                redirect_uri_validator=ValidateRedirectUri(client_repo=self._client_repo),
                jwt_manager=self._jwt_manager,
                persistent_grant_repo=self._persistent_grant_repo,
            )
        else:
            raise UnsupportedGrantTypeError
