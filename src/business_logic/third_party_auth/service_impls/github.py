from __future__ import annotations

import secrets
from typing import TYPE_CHECKING

from src.business_logic.third_party_auth.service_impls.mixins import (
    ThirdPartyAuthMixin,
)
from src.business_logic.third_party_auth.constants import (
    AuthProviderName,
    StateData,
)

if TYPE_CHECKING:
    from httpx import AsyncClient

    from src.business_logic.common.interfaces import ValidatorProtocol
    from src.business_logic.third_party_auth.dto import (
        ThirdPartyAccessTokenRequestModel,
    )
    from src.data_access.postgresql.repositories import (
        ClientRepository,
        PersistentGrantRepository,
        ThirdPartyOIDCRepository,
        UserRepository,
    )


class GithubAuthService(ThirdPartyAuthMixin):
    """
    Service class for handling authentication with GitHub as a third-party provider.

    Inherits:
        ThirdPartyAuthMixin: A mixin class providing common methods for third-party authentication.

    This class implements the necessary methods and functionality to authenticate users
    using GitHub's OAuth 2.0 flow.
    """

    def __init__(
        self,
        state_validator: ValidatorProtocol,
        client_repo: ClientRepository,
        user_repo: UserRepository,
        persistent_grant_repo: PersistentGrantRepository,
        oidc_repo: ThirdPartyOIDCRepository,
        async_http_client: AsyncClient,
    ) -> None:
        """
        Initializes a new instance of the GithubAuthService.

        Args:
            state_validator (ValidatorProtocol): The validator for the state parameter.
            client_repo (ClientRepository): The repository for client-related operations.
            user_repo (UserRepository): The repository for user-related operations.
            persistent_grant_repo (PersistentGrantRepository): The repository for persistent grant-related operations.
            oidc_repo (ThirdPartyOIDCRepository): The repository for OpenID Connect-related operations.
            async_http_client (AsyncClient): The asynchronous HTTP client for making HTTP requests.
        """
        self._state_validator = state_validator
        self._client_repo = client_repo
        self._user_repo = user_repo
        self._persistent_grant_repo = persistent_grant_repo
        self._oidc_repo = oidc_repo
        self._async_http_client = async_http_client
        self._secret_code = secrets.token_urlsafe(32)

    async def get_redirect_url(
        self, request_data: ThirdPartyAccessTokenRequestModel
    ) -> str:
        """
        Retrieves the redirect URL for the GitHub authentication flow.

        This method performs the necessary validation, grant creation, and redirect URL generation
        for the GitHub authentication flow.

        Args:
            request_data (ThirdPartyAccessTokenRequestModel): The request data containing the access token request details.

        Returns:
            str: The redirect URL for the GitHub authentication flow.

        Raises:
            ThirdPartyAuthInvalidStateError: If the requested scope is invalid.
            ThirdPartyAuthProviderInvalidRequestDataError: If the request to Github returns an error response.
        """
        await self._state_validator(request_data.state)
        await self._create_grant(
            request_data,
            username_type="login",
            provider_name=AuthProviderName.GITHUB.value,
        )
        redirect_url = f"{request_data.state.split('!_!')[StateData.REDIRECT_URL.value]}?code={self._secret_code}"
        return await self._update_redirect_url(request_data, redirect_url)
