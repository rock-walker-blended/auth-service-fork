from fastapi import Depends


from src.presentation.api.models.endsession import RequestEndSessionModel
from src.data_access.postgresql.repositories.client import ClientPostLogoutRedirectUriRepository
from src.data_access.postgresql.repositories.persistent_grant import PersistentGrantRepository
from src.business_logic.dependencies.database import get_repository
from src.business_logic.services.jwt_token import JWTService


class EndSessionService:

    def __init__(
            self,
            client_logout_repo: ClientPostLogoutRedirectUriRepository = Depends(get_repository(
                ClientPostLogoutRedirectUriRepository
            )),
            persistent_grant_repo: PersistentGrantRepository = Depends(get_repository(
                PersistentGrantRepository
            )),
    ) -> None:
        self.client_logout_repo = client_logout_repo
        self.persistent_grant_repo = persistent_grant_repo
        self.jwt_service = JWTService()
        self._request_model = None

    async def end_session(self) -> (str, None):
        decoded_id_token_hint = await self._decode_id_token_hint(id_token_hint=self.request_model.id_token_hint)
        await self._logout(
            client_id=decoded_id_token_hint['client_id'],
            user_id=decoded_id_token_hint['user_id'],
            data=decoded_id_token_hint['data'],
            grant_type=decoded_id_token_hint['type']
        )
        if self.request_model.post_logout_redirect_uri:
            if await self._validate_logout_redirect_uri(
                logout_redirect_uri=self.request_model.post_logout_redirect_uri,
                client_id=decoded_id_token_hint["client_id"]
            ):
                logout_redirect_uri = self.request_model.post_logout_redirect_uri
                if self.request_model.state:
                    logout_redirect_uri += f"&state={self.request_model.state}"
                return logout_redirect_uri
        return None

    async def _decode_id_token_hint(self, id_token_hint: str) -> dict:
        decoded_data = await self.jwt_service.decode_token(id_token_hint)
        return decoded_data

    async def _logout(self, client_id: str, user_id: int, data: str, grant_type: str) -> None:
        await self.persistent_grant_repo.delete_persistent_grant_by_client_and_user_id(
            client_id=client_id,
            user_id=user_id,
            data=data,
            grant_type=grant_type
        )
        return

    async def _validate_logout_redirect_uri(self, client_id: str, logout_redirect_uri: str) -> bool:
        result = await self.client_logout_repo.validate_post_logout_redirect_uri(client_id, logout_redirect_uri)
        return result

    @property
    def request_model(self) -> (RequestEndSessionModel, None):
        return self._request_model

    @request_model.setter
    def request_model(self, request_model: RequestEndSessionModel) -> None:
        self._request_model = request_model
