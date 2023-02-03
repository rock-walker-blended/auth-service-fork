from sqlalchemy import select, exists, update, insert, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from src.data_access.postgresql.tables.group import Group
from src.data_access.postgresql.errors.user import (
    ClaimsNotFoundError,
    UserNotFoundError,
)
from src.data_access.postgresql.repositories.base import BaseRepository
from src.data_access.postgresql.tables import User, UserClaim, Role
from src.data_access.postgresql.tables.users import users_roles, users_groups
from src.data_access.postgresql.errors.user import DuplicationError
from typing import Union

def params_to_dict(**kwargs):
    result = {}
    for key in kwargs:
        if kwargs[key] is not None:
            result[key] = kwargs[key]
    return result


class UserRepository(BaseRepository):
    async def exists(self, user_id: int) -> bool:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess

            result = await session.execute(
                select(exists().where(User.id == user_id))
            )
            result = result.first()
            return result[0]

    async def delete(self, user_id: int):
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_factory() as sess:
            session = sess
            if await self.exists(user_id=user_id):
                user_to_delete = await self.get_user_by_id(user_id=user_id)
                await session.delete(user_to_delete)
                await session.commit()
            else:
                raise ValueError

    async def get_user_by_id(self, user_id: int) -> User:
        try:
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
        except:
            raise ValueError

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
                raise UserNotFoundError(
                    "User you are looking for does not exist")

            user = user[0]
            return user.password_hash, user.id

    async def get_claims(self, id: int) -> dict:
        claims_of_user = await self.request_DB_for_claims(id)
        result = {}

        for claim in claims_of_user:
            result[claim[0].claim_type.code] = claim[0].claim_value

        if not result:
            raise ClaimsNotFoundError(
                "Claims for user you are looking for does not exist"
            )

        return result

    async def request_DB_for_claims(self, id: int):
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
            result = users.first()
            result = result[0].username
            return result

    async def get_user_by_username(self, username:str) -> User:
        try:
            session_factory = sessionmaker(
                self.engine, expire_on_commit=False, class_=AsyncSession
            )
            async with session_factory() as sess:
                session = sess
                user = await session.execute(
                    select(User).where(User.username == username)
                )
                user = user.first()

                return user[0]
        except:
            raise ValueError

    async def get_all_users(self, group_id: int = None, role_id: int = None) -> list[User]:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        try:
            async with session_factory() as sess:
                session = sess
                if group_id is None and role_id is None:
                    query = await session.execute(
                        select(User)
                    )
                    query = query.all()
                    return [user[0] for user in query]
                elif group_id is None and role_id is not None:
                    iterator = await session.execute(
                        select(User)
                        .join(
                            Role,
                            User.roles
                        )
                        .where(Role.id == role_id)
                    )
                    return [user[0] for user in iterator.all()]
                elif group_id is not None and role_id is None:
                    iterator = await session.execute(
                        select(User)
                        .join(
                            Group,
                            User.groups
                        )
                        .where(Group.id == group_id)
                    )
                    return [user[0] for user in iterator.all()]
                else:
                    iterator = await session.execute(
                        select(User)
                        .join(Group, User.groups)
                        .join(Role, User.roles)
                        .where(
                            Group.id == group_id,
                            Role.id == role_id
                        )
                    )
                    return [user[0] for user in iterator.all()]
        except:
            raise ValueError

    async def update(
            self, 
            user_id: int,
            id: Union[None, str] = None,
            username: Union[None, str] = None,
            security_stamp: Union[None, str] = None,
            email: Union[None, str] = None,
            email_confirmed: Union[None, bool] = None,
            phone_number: Union[None, str] = None,
            phone_number_confirmed: Union[None, bool] = None,
            two_factors_enabled: Union[None, bool] = None,
            lockout_end_date_utc: Union[None, str] = None,
            password_hash: Union[None, str] = None,
            lockout_enabled: Union[None, bool] = False,
            access_failed_count: Union[None, int] = None,
        ):
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        try:
            kwargs = params_to_dict(id = id, 
                                username = username, 
                                security_stamp = security_stamp,
                                email = email, 
                                email_confirmed = email_confirmed, 
                                phone_number = phone_number, 
                                phone_number_confirmed = phone_number_confirmed, 
                                two_factors_enabled = two_factors_enabled, 
                                lockout_end_date_utc = lockout_end_date_utc, 
                                lockout_enabled = lockout_enabled,
                                password_hash = password_hash,
                                access_failed_count = access_failed_count)
            async with session_factory() as sess:
                session = sess
                if await self.exists(user_id=user_id):
                    updates = update(User).values(
                        **kwargs).where(User.id == user_id)
                    await session.execute(updates)
                    await session.commit()
                else:
                    raise ValueError
        except:
            raise DuplicationError

    async def create(
        self,
        id: Union[None, str] = None,
        username: Union[None, str] = None,
        security_stamp: Union[None, str] = None,
        email: Union[None, str] = None,
        email_confirmed: Union[None, bool] = None,
        phone_number: Union[None, str] = None,
        phone_number_confirmed: Union[None, bool] = None,
        two_factors_enabled: Union[None, bool] = None,
        lockout_end_date_utc: Union[None, str] = None,
        password_hash: Union[None, str] = None,
        lockout_enabled: Union[None, bool] = False,
        access_failed_count: Union[None, int] = 0,
        ) -> bool:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        try:
            kwargs = params_to_dict(id = id, 
                                    username = username, 
                                    security_stamp = security_stamp,
                                    email = email, 
                                    email_confirmed = email_confirmed, 
                                    phone_number = phone_number, 
                                    phone_number_confirmed = phone_number_confirmed, 
                                    two_factors_enabled = two_factors_enabled, 
                                    lockout_end_date_utc = lockout_end_date_utc, 
                                    lockout_enabled = lockout_enabled,
                                    password_hash = password_hash,
                                    access_failed_count = access_failed_count)
            async with session_factory() as sess:
                session = sess

                await session.execute(
                    insert(User).values(**kwargs)
                )
                await session.commit()
        except:
            raise DuplicationError

    async def add_group(self, user_id:int, group_id:int):
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        try:
                async with session_factory() as sess:
                    session = sess
                    flag_one = (await session.execute(select(exists().where(Group.id == group_id)))).first()[0]
                    flag_two = (await session.execute(select(exists().where(User.id == user_id)))).first()[0]
                    if flag_one and flag_two:
                        await session.execute(insert(users_groups).values(user_id = user_id, group_id = group_id))
                        await session.commit()
                    elif not flag_two or not flag_one:
                        raise ValueError
        except ValueError:
            raise ValueError
        except:
            raise DuplicationError

    async def add_role(self, user_id: int, role_id: int) -> bool:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        try: 
            async with session_factory() as sess:
                session = sess
                await session.execute(
                    insert(users_roles).values(user_id=user_id, role_id=role_id)
                    )
                await session.commit()
                return True
        except:
            raise DuplicationError

    async def remove_user_groups(self, user_id: int, group_ids: list) -> bool:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        try: 
            async with session_factory() as sess:
                session = sess
                sql = f"DELETE FROM users_groups WHERE user_id = {user_id} AND group_id IN ({group_ids})"
                await session.execute(text(sql))
                await session.commit()
        except:
            raise ValueError

    async def remove_user_roles(self, user_id:int, role_ids:str) -> bool:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        try: 
            async with session_factory() as sess:
                session = sess
                sql = f"DELETE FROM users_roles WHERE user_id = {user_id} AND role_id IN ({role_ids})"
                await session.execute(text(sql))
                await session.commit()
            return True
        except:
            return False

    async def get_roles(self, user_id: int) -> list[Role]:
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        try:
            async with session_factory() as sess:
                session = sess
                iterator = await session.execute(
                        select(Role)
                        .join(
                            User,
                            Role.users
                        )
                        .where(User.id == user_id)
                    )
                return [role[0] for role in iterator.all()]
        except:
            raise ValueError

    async def get_groups(self, user_id: int):
        session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        try:
            async with session_factory() as sess:
                session = sess
                iterator = await session.execute(
                        select(Group)
                        .join(
                            User,
                            Group.users
                        )
                        .where(User.id == user_id)
                    )
                return [group[0] for group in iterator.all()]
        except:
            raise ValueError

    def __repr__(self) -> str:
        return "User repository"
