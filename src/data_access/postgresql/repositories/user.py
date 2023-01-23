from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from src.data_access.postgresql.errors.user import (
    ClaimsNotFoundError,
    UserNotFoundError,
)
from src.data_access.postgresql.repositories.base import BaseRepository
from src.data_access.postgresql.tables import User, UserClaim


class UserRepository(BaseRepository):
    async def get_user_by_id(self, user_id: int) -> User:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            user = await session.execute(
                select(User).where(User.id == user_id)
            )
            user = user.first()

            return user[0]

    async def get_hash_password(self, user_name: str) -> tuple:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            user = await session.execute(
                select(User).where(User.username == user_name)
            )
            user = user.first()

            if user is None:
                raise UserNotFoundError("User you are looking for does not exist")

            user = user[0]
            return user.password_hash, user.id

    async def get_claims(self, id: int) -> dict:
        claims_of_user = await self.request_DB_for_claims(id)
        result = {}

        for claim in claims_of_user:
            result[dict(claim)["UserClaim"].claim_type.code] = dict(claim)[
                "UserClaim"
            ].claim_value

        if not result:
            raise ClaimsNotFoundError(
                "Claims for user you are looking for does not exist"
            )

        return result

    async def request_DB_for_claims(self, id):
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            return await session.execute(
                select(UserClaim).where(UserClaim.user_id == id)
            )

    async def get_username_by_id(self, id: int) -> str:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            users = await session.execute(select(User).where(User.id == id))
            result = []
            result = dict(next(users))["User"].username

            return result

    def __repr__(self) -> str:
        return "User repository"
