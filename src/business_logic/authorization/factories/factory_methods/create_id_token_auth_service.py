from __future__ import annotations

from typing import TYPE_CHECKING, Any

from src.business_logic.authorization.service_impls import IdTokenAuthService
from src.business_logic.authorization.validators import (
    ScopeValidator,
    UserCredentialsValidator,
)
from src.business_logic.common.validators import (
    ClientValidator,
    RedirectUriValidator,
)

if TYPE_CHECKING:
    from src.business_logic.authorization.interfaces import AuthServiceProtocol
    from src.business_logic.services import PasswordHash
    from src.business_logic.jwt_manager.interfaces import JWTManagerProtocol

    from src.data_access.postgresql.repositories import (
        ClientRepository,
        UserRepository,
    )


def _create_id_token_auth_service(
    *,
    client_repo: ClientRepository,
    user_repo: UserRepository,
    password_service: PasswordHash,
    jwt_service: JWTService,
    scope_service,
    **kwargs: Any,
) -> AuthServiceProtocol:
    """
    Factory method for creating an instance of IdTokenAuthService, which is used for
    an implicit flow.

    Reference: https://openid.net/specs/openid-connect-core-1_0.html#ImplicitFlowAuth.

    Args:
        client_repo: The repository for accessing client-related data.
        user_repo: The repository for accessing user-related data.
        password_service: The service for password hashing and verification.
        jwt_service: The service for JWT generation and verification.
        **kwargs: Additional keyword arguments.

    Returns:
        An instance of IdTokenAuthService.
    """
    return IdTokenAuthService(
        client_validator=ClientValidator(client_repo),
        redirect_uri_validator=RedirectUriValidator(client_repo),
        scope_validator=ScopeValidator(
            client_repo=client_repo,
            scope_service=scope_service
        ),
        user_credentials_validator=UserCredentialsValidator(
            user_repo=user_repo,
            password_service=password_service,
        ),
        user_repo=user_repo,
        jwt_manager=jwt_manager,
    )
