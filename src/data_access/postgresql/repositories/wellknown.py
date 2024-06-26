from typing import Any, Dict, Optional, Tuple, Union

from sqlalchemy import exists, insert, join, select, text, update
from sqlalchemy.engine.result import ChunkedIteratorResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from src.data_access.postgresql.errors.user import (
    ClaimsNotFoundError,
    NoPasswordError,
    UserNotFoundError,
)
from src.data_access.postgresql.repositories.base import BaseRepository
from src.data_access.postgresql.tables import (
    Role,
)
from ..tables import UserClaimType, PersistentGrantType


class WellKnownRepository(BaseRepository):
    async def get_user_claim_types(self) -> list[Optional[str]]:
        result = await self.session.execute(
            select(UserClaimType.type_of_claim)
            )
        if result:
            return [claim[0] for claim in result.all()]
        return [None]
        
    async def get_grant_types(self) -> list[str]:
        result = await self.session.execute(
            select(PersistentGrantType.type_of_grant)
            )
        if result:
            return [gr_type[0] for gr_type in result.all()]
        return [None]
