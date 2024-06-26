from datetime import datetime

from sqlalchemy import delete, exists, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from src.data_access.postgresql.errors import UserCodeNotFoundError
from src.data_access.postgresql.repositories.base import BaseRepository
from src.data_access.postgresql.tables.device import Device

from .client import Client


class DeviceRepository(BaseRepository):
    async def create(
        self,
        client_id: str,
        device_code: str,
        user_code: str,
        verification_uri: str,
        verification_uri_complete: str,
        expires_in: int = 600,
        interval: int = 5,
    ) -> None:
        client_id_int = await self.get_client_id_int(client_id=client_id)
        device_data = {
            "client_id": client_id_int,
            "device_code": device_code,
            "user_code": user_code,
            "verification_uri": verification_uri,
            "verification_uri_complete": verification_uri_complete,
            "expires_in": expires_in,
            "interval": interval,
        }
        await self.session.execute(insert(Device).values(**device_data))

    async def delete_by_user_code(self, user_code: str) -> None:
        if await self.validate_user_code(user_code=user_code):
            await self.session.execute(
                delete(Device).where(Device.user_code == user_code)
            )

    async def delete_by_device_code(self, device_code: str) -> None:
        if await self.validate_device_code(device_code=device_code):
            await self.session.execute(
                delete(Device).where(Device.device_code == device_code)
            )

    async def validate_user_code(self, user_code: str) -> bool:
        result = await self.session.execute(
            select(exists().where(Device.user_code == user_code))
        )
        result = result.first()
        if not result[0]:
            raise UserCodeNotFoundError("Wrong User Code")
        return result[0]

    async def validate_device_code(self, device_code: str) -> bool:
        result = await self.session.execute(
            select(exists().where(Device.device_code == device_code))
        )
        result = result.first()
        return result[0]

    async def get_device_by_user_code(self, user_code: str) -> Device:
        if await self.validate_user_code(user_code=user_code):
            device = await self.session.execute(
                select(Device)
                .join(Client, Device.client_id == Client.id)
                .where(Device.user_code == user_code)
            )
            return device.first()[0]
        else:
            raise UserCodeNotFoundError

    async def get_expiration_time(self, device_code: str) -> int:
        device = await self.session.execute(
            select(Device).where(Device.device_code == device_code)
        )
        device = device.first()[0]
        created_at = device.created_at
        expires_in = device.expires_in
        time = datetime.timestamp(created_at) + expires_in

        return time

    async def get_client_id_int(self, client_id: str) -> int:
        client_id_int = await self.session.execute(
            select(Client).where(
                Client.client_id == client_id,
            )
        )
        client_id_int = client_id_int.first()

        if client_id_int is None:
            raise ValueError
        else:
            return client_id_int[0].id

    async def get_device_code_by_user_code(self, user_code: str) -> str:
        result = await self.session.execute(
            select(Device.device_code).where(Device.user_code == user_code)
        )
        return result.scalar()

    async def exists(self, user_code: str) -> bool:
        result = await self.session.execute(
            select(Device)
            .where(Device.user_code == user_code)
            .exists()
            .select()
        )
        return result.scalar()

    async def get_expiration_time_by_user_code(self, user_code: str):
        result = await self.session.execute(
            select(Device.expires_in).where(Device.user_code == user_code)
        )
        return result.scalar()
