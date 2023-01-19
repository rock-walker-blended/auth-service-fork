import datetime
import logging
import time
import uuid
from typing import Union

from fastapi import status
from sqlalchemy import exists, insert, select, delete

from src.data_access.postgresql.repositories.base import BaseRepository
from src.data_access.postgresql.tables.persistent_grant import PersistentGrant
from src.data_access.postgresql.errors.persistent_grant import PersistentGrantNotFoundError

logger = logging.getLogger("is_app")


class PersistentGrantRepository(BaseRepository):
    async def create(
        self,
        client_id: str,
        data: str,
        user_id: int,
        grant_type: str = 'code',
        expiration_time: int = 600,
    ) -> None:
        unique_key = str(uuid.uuid4())
        persistent_grant = {
            "key": unique_key,
            "client_id": client_id,
            "data": data,
            "expiration": expiration_time,
            "subject_id": user_id,
            "type": grant_type,
        }
        await self.session.execute(
            insert(PersistentGrant).values(**persistent_grant)
        )
        await self.session.commit()

    async def exists(self, grant_type: str, data: str) -> bool:

        result = await self.session.execute(
            select(
                [
                    exists().where(
                        PersistentGrant.type == grant_type,
                        PersistentGrant.data == data,
                    )
                ]
            )
        )
        result = result.first()

        return result[0]

    async def get(self, grant_type: str, data: str):
        result = await self.session.execute(
            select(PersistentGrant).where(
                PersistentGrant.type == grant_type, PersistentGrant.data == data
            )
        )
        return result.first()[0]

    async def delete(self, data: str, grant_type: str) -> int:
        if await self.exists(grant_type=grant_type, data=data):
            grant_to_delete = await self.get(grant_type=grant_type, data=data)
            await self.session.delete(grant_to_delete)
            await self.session.commit()
            return status.HTTP_200_OK
        else:
            return status.HTTP_404_NOT_FOUND

    async def get_client_id_by_data(self, data):
        client_id = await self.session.execute(
            select(PersistentGrant.client_id).where(PersistentGrant.data == data)
        )
        client_id = client_id.first()

        if client_id is None:
            raise PersistentGrantNotFoundError(
                "Persistent grant you are looking for does not exist"
            )
        return client_id[0]

    async def delete_persistent_grant_by_client_and_user_id(
            self,
            client_id: str,
            user_id: int,
            grant_type: str,
            data: str
            ) -> None:
        if await self.exists(grant_type, data):
            await self.session.execute(
                delete(PersistentGrant).
                where(PersistentGrant.client_id == client_id).
                where(PersistentGrant.subject_id == user_id)
            )
            await self.session.commit()
            return None
        else:
            raise PersistentGrantNotFoundError("Persistent grant you are looking for does not exist")
