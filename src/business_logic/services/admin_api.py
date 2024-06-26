# https://docs.google.com/spreadsheets/d/1zJAcCxaGz2CV9zKlqeBhRE8xfiqyJMy5-XPRH1I8HPg/edit#gid=0
from typing import Optional, Any
from src.data_access.postgresql.repositories import RoleRepository, UserRepository, PersistentGrantRepository, GroupRepository
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from src.business_logic.services.jwt_token import JWTService
from src.business_logic.services.password import PasswordHash
from src.data_access.postgresql.tables import Group, Role, User


class AdminService():
    def __init__(
        self,
        jwt_service: JWTService,
    ) -> None:
        self.jwt_service = jwt_service


class AdminTokenService():
    def __init__(
            self,
            grant_repo: PersistentGrantRepository
        ) -> None:
        self.grant_repo= grant_repo


class AdminRoleService():
    def __init__(
            self,
            session: AsyncSession,
            role_repo: RoleRepository
        ) -> None:
        self.session = session
        self.role_repo= role_repo
        
    async def get_role(self, role_id:int) -> Role:
        return await self.role_repo.get_role_by_id(role_id=role_id)

    async def get_roles(self, role_ids:str) -> list[Role]:
        role_ids_int = [int(number) for number in role_ids.split(",")]
        return [await self.role_repo.get_role_by_id(role_id=role_id) for role_id in role_ids_int]

    async def get_all_roles(self) -> list[Role]:
        return await self.role_repo.get_all_roles()

    async def create_role(self, **kwargs:Any) -> None:
        await self.role_repo.create(**kwargs)

    async def update_role(self, role_id:int, **kwargs:Any) -> None:
        await self.role_repo.update(role_id=role_id, **kwargs)

    async def delete_role(self, role_id:int) -> None:
        await self.role_repo.delete(role_id=role_id)


class AdminGroupService():
    def __init__(
            self,
            session: AsyncSession,
            group_repo: GroupRepository
        ) -> None:
        self.session = session
        self.group_repo= group_repo



    async def get_all_groups(self) -> list[Role]:
        return await self.group_repo.get_all_groups()


    async def get_groups(self, group_ids:list[int]) -> list[Group]:
        result = []
        for group_id in group_ids:
            result.append(await self.group_repo.get_by_id(group_id=group_id))
        return result

    async def get_subgroups(self, group_id:int) -> dict[str, Any]:
        group = await self.group_repo.get_by_id(group_id=group_id)
        result = await self.group_repo.get_all_subgroups(main_group=group)
        return result

    async def update_group(self, group_id: int, **kwargs:Any) -> None:
        await self.group_repo.update(group_id=group_id, **kwargs)

    async def get_group(self, group_id:int) -> Group:
        return await self.group_repo.get_by_id(group_id=group_id)

    async def create_group(self, **kwargs: Any) -> None:
        await self.group_repo.create(**kwargs)

    async def delete_group(self, group_id: int) -> None:
        await self.group_repo.delete(group_id=group_id)


class AdminUserService():
    
    def __init__(
            self,
            user_repo: UserRepository,
            session: AsyncSession
        ) -> None:
        self.user_repo=user_repo
        self.session = session

    async def get_all_users(self, group_id: Optional[int] = None, role_id:Optional[int] = None) -> list[User]:
        users=await self.user_repo.get_all_users(group_id= group_id, role_id = role_id)
        return users
    
    async def add_user_roles(self, user_id:int ,role_ids: str) -> None:
        role_ids_int = [int(number) for number in role_ids.split(",")]
        for role_id in role_ids_int:
            await self.user_repo.add_role(user_id=user_id, role_id=role_id)

    async def remove_user_roles(self, user_id:int ,role_ids: str) -> None:
        await self.user_repo.remove_user_roles(user_id=user_id, role_ids=role_ids)

    async def get_user_roles(self, user_id:int) -> list[Role]:
        return await self.user_repo.get_roles(user_id=user_id)
    
    async def add_user_groups(self, user_id:int, group_ids:str) -> None:
        group_ids_int = [int(number) for number in group_ids.split(",")]
        for group_id in group_ids_int: 
            await self.user_repo.add_group(user_id = user_id, group_id=group_id)

    async def get_user_groups(self, user_id:int) -> list[Group]:
        return await self.user_repo.get_groups(user_id=user_id)

    async def remove_user_groups(self, user_id:int, group_ids:str) -> None:
        await self.user_repo.remove_user_groups(user_id=user_id, group_ids=group_ids)

    async def create_user(self, kwargs:Any) -> None:
        kwargs = kwargs | {
            "email_confirmed": False,
            "phone_number_confirmed": False,
            "access_failed_count":0,
            }
        await self.user_repo.create(**kwargs)
        
    async def change_password(self, user_id:int, new_password:str) -> None:
        new_password = PasswordHash.hash_password(password=new_password)
        await self.user_repo.change_password(user_id=user_id, password = new_password)
    

    async def get_user(self, user_id:int) -> User:
        return await self.user_repo.get_user_by_id(user_id=user_id)

    async def update_user(self, user_id:int, kwargs: Any) -> None:
        await self.user_repo.update(user_id=user_id, **kwargs)
        
    async def delete_user(self, user_id:int) -> None:
        await self.user_repo.delete(user_id=user_id)
        
    async def get_all_users(self, group_id: Optional[int] = None, role_id:Optional[int] = None) -> list[User]:
        return await self.user_repo.get_all_users(group_id= group_id, role_id = role_id)
    
    async def registration(self, kwargs:dict)->None:
        password = kwargs['password']
        email = kwargs['email']
        del kwargs['password']
        kwargs = kwargs | {
            "email_confirmed": False,
            "phone_number_confirmed": False,
            "access_failed_count":0,
            }
        await self.user_repo.create(
            username = kwargs['username'],
            email = kwargs['email'],
            phone_number = kwargs['phone_number'],
            )
        
        user_id = (await self.user_repo.get_user_by_email(email=email)).id
        password_hashed = PasswordHash.hash_password(password=password)
        await self.user_repo.change_password(user_id=user_id, password=password_hashed)
        #if len([v for v in kwargs.values() if v is not None])>6:
        kwargs["birthdate"] = str(kwargs['birthdate'])
        types = await self.user_repo.get_all_claim_types()
        claims = []
        for key in kwargs:
            if key in types.keys() and kwargs[key]:
                claims.append({"user_id":user_id,"claim_type_id":types[key], "claim_value":kwargs[key]})
        if claims:
            await self.user_repo.add_claims(claims=claims)

    async def validate_password(self, email:str, password:str):
        user:User = await self.user_repo.get_user_by_email(email=email)
        return PasswordHash.validate_password(str_password=password,hash_password=user.password_hash.value), user
    
    def user_to_dict(self, user:User)->dict[str, str]:
        user_data = user.__dict__
        for claim in user.claims:
            user_data[claim.claim_type.type_of_claim] = claim.claim_value
        return user_data

    async def add_user_info(self, username:str, data:dict):
        user_id = (await self.user_repo.get_user_by_username(username=username)).id
        types = await self.user_repo.get_all_claim_types()
        claims = []
        for key in data:
            if key in types.keys() and data[key]:
                claims.append({"user_id":user_id,"claim_type_id":types[key], "claim_value":data[key]})
        
        await self.user_repo.add_claims(claims=claims)
