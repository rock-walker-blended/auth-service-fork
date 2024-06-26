import logging
import uuid

from fastapi import status
from sqlalchemy import delete, exists, insert, select, extract, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import Optional
from src.data_access.postgresql.errors.persistent_grant import (
    PersistentGrantNotFoundError,
)
from datetime import datetime, timedelta
from src.data_access.postgresql.repositories.base import BaseRepository
from src.data_access.postgresql.tables import (
    PersistentGrant,
    PersistentGrantType,
    Client,
)
from sqlalchemy.engine.result import ChunkedIteratorResult

logger = logging.getLogger(__name__)


class PersistentGrantRepository(BaseRepository):
   
    async def create(
        self,
        client_id: str,
        grant_data: str,
        user_id: int,
        scope: Optional[str] = None,
        grant_type: str = "authorization_code",
        expiration_time: int = 600,
    ) -> None:
        grant_type_id = await self.get_type_id(grant_type)
        client_id_int = await self.get_client_id_int(client_id=client_id)
        unique_key = str(uuid.uuid4())
        persistent_grant = {
            "key": unique_key,
            "client_id": client_id_int,
            "grant_data": grant_data,
            "expiration": expiration_time,
            "user_id": user_id,
            "persistent_grant_type_id": grant_type_id,
            "scope": scope
        }

        await self.session.execute(
            insert(PersistentGrant).values(**persistent_grant)
        )

    async def get_type_id(self, type_of_grant: str) -> PersistentGrant:
        result = await self.session.execute(
            select(PersistentGrantType).where(
                PersistentGrantType.type_of_grant == type_of_grant,
            )
        )
        result = result.first()[0].id
        return result

    async def exists(self, grant_data: str, grant_type: str) -> bool:
        result = await self.session.execute(
            select(PersistentGrant)
            .join(
                PersistentGrantType,
                PersistentGrantType.id
                == PersistentGrant.persistent_grant_type_id,
            )
            .where(
                PersistentGrantType.type_of_grant == grant_type,
                PersistentGrant.grant_data == grant_data,
            )
        )

        result = result.first()
        return bool(result)

    async def get(self, grant_type: str, grant_data: str) -> PersistentGrant:
        grant_type_id = await self.get_type_id(type_of_grant=grant_type)
        result = await self.session.execute(
            select(PersistentGrant)
            .join(Client, PersistentGrant.client_id == Client.id)
            .where(
                PersistentGrant.persistent_grant_type_id == grant_type_id,
                PersistentGrant.grant_data == grant_data,
            )
        )
        result = result.first()[0]
        return result

    async def get_all(self) -> list[PersistentGrant]:
        grants = await self.session.execute(
            select(PersistentGrant)
        )
        result = [grant[0] for grant in grants.all()]
        return result

    async def delete(self, grant_type: str, grant_data: str) -> int:
        #TODO: no http errors must be in the data_access layer.
        if await self.exists(grant_data=grant_data, grant_type=grant_type):
            grant_to_delete = await self.get(
                grant_data=grant_data, grant_type=grant_type
            )
            await self.session.delete(grant_to_delete)
            return status.HTTP_200_OK
        else:
            return status.HTTP_404_NOT_FOUND

    async def delete_persistent_grant_by_client_and_user_id(
        self, client_id: str, user_id: int
    ) -> None:
        await self.check_grant_by_client_and_user_ids(
            client_id=client_id, user_id=user_id
        )
        client_id_int = await self.get_client_id_int(client_id=client_id)
        await self.session.execute(
            delete(PersistentGrant).where(
                PersistentGrant.client_id == client_id_int,
                PersistentGrant.user_id == user_id,
            )
        )
        return None

    async def check_grant_by_client_and_user_ids(
        self, client_id: str, user_id: int
    ) -> bool:
        client_id_int = await self.get_client_id_int(client_id=client_id)
        grant = await self.session.execute(
            select(
                exists().where(
                    PersistentGrant.client_id == client_id_int,
                    PersistentGrant.user_id == user_id,
                )
            )
        )
        grant = grant.first()
        if not grant[0]:
            raise PersistentGrantNotFoundError(
                "Persistent grant you are looking for does not exist"
            )
        return grant[0]

    async def get_client_id_by_data(self, grant_data: str) -> int:
        client_id = await self.session.execute(
            select(PersistentGrant.client_id).where(
                PersistentGrant.grant_data == grant_data
            )
        )
        client_id = client_id.first()

        if client_id is None:
            raise PersistentGrantNotFoundError(
                "Persistent grant you are looking for does not exist"
            )
        else:
            client_id = client_id[0]

        client_id_str = await self.session.execute(
            select(Client.client_id).where(
                Client.id == client_id,
            )
        )
        client_id_str = client_id_str.first()

        if client_id_str is None:
            raise PersistentGrantNotFoundError
        else:
            return client_id_str[0]

    async def get_client_id_int(
        self, client_id: str,
    ) -> int:
        client_id_int = await self.session.execute(
            select(Client.id).where(
                Client.client_id == client_id,
            )
        )
        client_id_int = client_id_int.first()

        if client_id_int is None:
            raise PersistentGrantNotFoundError
        else:
            return client_id_int[0]

    async def get_all_types(self) -> ChunkedIteratorResult:
        types = await self.session.execute(
            select(PersistentGrantType.type_of_grant)
        )
        return types.all()
    
    async def exists_grant_for_client(self, authorization_code: str, client_id: str, grant_type: str) -> bool:
        query = (select(PersistentGrant)
                 .join(Client, PersistentGrant.client_id == Client.id)
                 .join(PersistentGrantType, PersistentGrant.persistent_grant_type_id == PersistentGrantType.id)
                 .where(PersistentGrant.grant_data == authorization_code,
                        Client.client_id == client_id,
                        PersistentGrantType.type_of_grant == grant_type)
                .exists().select()
                )
        result = await self.session.execute(query)
        return result.scalar()

    async def create_grant(
            self,
            client_id: int,
            grant_data: str,
            user_id: int,
            grant_type_id: int,
            expiration_time: int,
            scope:str,
    ) -> None:
        await self.session.execute(
            insert(PersistentGrant).values(
                key=str(uuid.uuid4()),
                client_id=client_id,
                grant_data=grant_data,
                expiration=expiration_time,
                user_id=user_id,
                persistent_grant_type_id=grant_type_id,
                scope=scope
            )
        )

    async def delete_grant(self, grant: PersistentGrant) -> None:
        await self.session.delete(grant)

    async def get_grant(self, grant_data: str, grant_type: str) -> PersistentGrant:
        result = await self.session.execute(
            select(PersistentGrant)
            .join(PersistentGrantType, PersistentGrant.persistent_grant_type_id == PersistentGrantType.id)
            .where(PersistentGrant.grant_data == grant_data, PersistentGrantType.type_of_grant == grant_type)
        )
        return result.scalar()
 
    async def delete_expired(self) -> None:
        grants_to_delete = await self.session.execute(
            select(PersistentGrant)
            .where(func.trunc(extract('epoch', datetime.utcnow()) - extract('epoch', PersistentGrant.created_at) )  >= PersistentGrant.expiration)
            )
        
        grants_to_delete_list = grants_to_delete.all()
        logger.info(f"Deleted {len(grants_to_delete_list)} expired tokens")
        for grant in grants_to_delete_list:
            await self.session.delete(grant[0])

    async def get_next_cleaning_time(self) -> float:
        if self.check_not_empty():
            query = select(func.min(extract('epoch', PersistentGrant.created_at) ) + PersistentGrant.expiration)
            result = await self.session.execute(query)
            min_value = result.scalar()
            return min_value - datetime.utcnow().timestamp()
        else:
            result = await self.session.execute(select(func.min(Client.absolute_refresh_token_lifetime)))
            min_value = result.scalar()
            return min_value
    
    async def check_not_empty(self):
        query = select(exists().where(PersistentGrant))
        result = await self.session.execute(query)
        return result.scalar()