import json
import logging
import secrets
from typing import Any, Dict, Optional

from httpx import AsyncClient

from src.data_access.postgresql.repositories import (
    ClientRepository,
    UserRepository,
    PersistentGrantRepository,
    ThirdPartyOIDCRepository,
)
from src.presentation.api.models import (
    ThirdPartyOIDCRequestModel,
    StateRequestModel,
)

logger = logging.getLogger(__name__)


class AuthThirdPartyOIDCService:
    def __init__(
        self,
        client_repo: ClientRepository,
        user_repo: UserRepository,
        persistent_grant_repo: PersistentGrantRepository,
        oidc_repo: ThirdPartyOIDCRepository,
        http_client: AsyncClient,
    ) -> None:
        self._request_model: Optional[ThirdPartyOIDCRequestModel] = None
        self._state_request_model: Optional[StateRequestModel] = None
        self.client_repo = client_repo
        self.user_repo = user_repo
        self.persistent_grant_repo = persistent_grant_repo
        self.oidc_repo = oidc_repo
        self.http_client = http_client

    async def get_github_redirect_uri(self) -> Optional[str]:
        github_links = await self.get_provider_external_links(name="github")
        access_token_url: str = ""
        user_data_url: str = ""
        if github_links is not None:
            access_token_url = github_links["token_endpoint_link"]
            user_data_url = github_links["userinfo_link"]
        if self.request_model is not None and self.request_model.state:
            if await self.oidc_repo.validate_state(
                state=self.request_model.state
            ):
                await self.oidc_repo.delete_state(
                    state=self.request_model.state
                )
                request_params = await self.get_provider_auth_request_data(
                    name="github"
                )

                # make request to access_token_url to get a request token
                access_token: str = ""
                if request_params is not None:
                    access_token = (
                        await self.make_post_request_for_access_token(
                            access_url=access_token_url, params=request_params
                        )
                    )

                # make request to user_data_url to get user information
                headers = {
                    "Authorization": "Bearer " + access_token,
                    "Content-Type": "application/x-www-form-urlencoded",
                }
                user_name = await self.make_get_request_for_user_data(
                    access_url=user_data_url, headers=headers
                )

                redirect_uri = self.request_model.state.split("!_!")[
                    -1
                ]  # this redirect uri we return

                if not await self.user_repo.validate_user_by_username(
                    username=user_name
                ):
                    # create new user
                    provider_id = await self.oidc_repo.get_provider_id_by_name(
                        name="github"
                    )
                    if provider_id is not None:
                        await self.create_new_user(
                            username=user_name, provider=provider_id
                        )

                # create new persistent grant
                secret_code = secrets.token_urlsafe(32)

                await self.create_new_persistent_grant(
                    username=user_name, secret_code=secret_code
                )
                ready_redirect_uri = (
                    await self._update_redirect_url_with_params(
                        redirect_uri=redirect_uri, secret_code=secret_code
                    )
                )
                return ready_redirect_uri

        return None

    async def make_post_request_for_access_token(
        self, access_url: str, params: Dict[str, Any]
    ) -> str:
        token_response = await self.http_client.request(
            "POST", access_url, params=params
        )
        token_response_content = token_response.content.decode("utf-8")
        parsed_response_content = self._parse_response_content(
            response_content=token_response_content
        )
        access_token = parsed_response_content["access_token"]
        return access_token

    async def make_get_request_for_user_data(
        self, access_url: str, headers: Dict[str, Any]
    ) -> str:
        user_response = await self.http_client.request(
            "GET", access_url, headers=headers
        )
        user_response_content = json.loads(
            user_response.content.decode("utf-8")
        )
        user_name = user_response_content["login"]
        return user_name

    async def get_provider_auth_request_data(
        self, name: str
    ) -> Optional[Dict[str, Any]]:
        if self.request_model is not None:
            provider_row_data = (
                await self.oidc_repo.get_row_provider_credentials_by_name(
                    name=name
                )
            )
            if provider_row_data is not None:
                request_params = {
                    "client_id": provider_row_data[0],
                    "client_secret": provider_row_data[1],
                    "code": self.request_model.code,
                }
                return request_params
        return None

    async def get_provider_external_links(
        self, name: str
    ) -> Optional[Dict[str, str]]:
        external_links = await self.oidc_repo.get_provider_external_links(
            name=name
        )
        if external_links is not None:
            provider_external_links = {
                "token_endpoint_link": external_links[0],
                "userinfo_link": external_links[1],
            }
            return provider_external_links
        return None

    async def create_new_user(self, username: str, provider: int) -> None:
        await self.user_repo.create(
            username=username, identity_provider_id=provider
        )
        return None

    async def create_new_persistent_grant(
        self, username: str, secret_code: str
    ) -> None:
        if self.request_model is not None:
            user = await self.user_repo.get_user_by_username(username=username)
            if not self.request_model.state:
                raise AttributeError
            grant_data = {
                "client_id": self.request_model.state.split("!_!")[1],
                "grant_data": secret_code,
                "user_id": user.id,
                "grant_type": "code",
            }
            await self.persistent_grant_repo.create(**grant_data)
        return None

    async def create_provider_state(self) -> None:
        if self.state_request_model is not None:
            await self.oidc_repo.create_state(
                state=self.state_request_model.state
            )
        return None

    async def _update_redirect_url_with_params(
        self, redirect_uri: str, secret_code: str
    ) -> Optional[str]:
        if self.request_model is not None:
            redirect_uri = f"{redirect_uri}?code={secret_code}"
            if self.request_model.state:
                redirect_uri += f"&state={self.request_model.state}"

            return redirect_uri
        return None

    @staticmethod
    def _parse_response_content(
        response_content: str,
    ) -> Dict[str, Any]:
        return {
            item.split("=")[0]: item.split("=")[1]
            for item in response_content.split("&")
            if len(item.split("=")) == 2
        }

    @property
    def request_model(self) -> Optional[ThirdPartyOIDCRequestModel]:
        return self._request_model

    @request_model.setter
    def request_model(self, request_model: ThirdPartyOIDCRequestModel) -> None:
        self._request_model = request_model

    @property
    def state_request_model(self) -> Optional[StateRequestModel]:
        return self._state_request_model

    @state_request_model.setter
    def state_request_model(
        self, state_request_model: StateRequestModel
    ) -> None:
        self._state_request_model = state_request_model
