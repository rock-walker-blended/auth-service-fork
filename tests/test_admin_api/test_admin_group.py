import json
import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import insert, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm import sessionmaker

from src.business_logic.services.jwt_token import JWTService
from src.data_access.postgresql.tables.persistent_grant import PersistentGrant
from src.data_access.postgresql.repositories.user import UserRepository
from src.data_access.postgresql.repositories.groups import GroupRepository
from src.data_access.postgresql.repositories.roles import RoleRepository
import logging
from src.data_access.postgresql.errors.user import DuplicationError
from typing import Any


logger = logging.getLogger(__name__)


@pytest.mark.asyncio
class TestAdminGroupEndpoint:
    async def setup_base(self, engine: AsyncEngine, user_id: int = 1000) -> None:
        self.access_token = await JWTService().encode_jwt(
            payload={"stand": "CrazyDiamond"}
        )
        self.group_repo = GroupRepository(engine)
        self.role_repo = RoleRepository(engine)

        self.user_repo = UserRepository(engine)
        try:
            if await self.user_repo.exists(user_id=user_id):
                await self.user_repo.delete(user_id=user_id)
            if await self.user_repo.get_user_by_username(username="DioBrando"):
                await self.user_repo.delete(
                    user_id=(
                        await self.user_repo.get_user_by_username(
                            username="DioBrando"
                        )
                    ).id
                )
        except:
            pass

        data = {
            "id": user_id,
            "username": "DioBrando",
            "email": "theworld@timestop.com",
            "email_confirmed": True,
            "phone_number": "+20-123-123-123",
            "phone_number_confirmed": False,
            #  "password_hash": "1",
            "two_factors_enabled": False,
        }
        await self.user_repo.create( 
            id=user_id,
            username="DioBrando",
            email = "theworld@timestop.com",
            email_confirmed = True,
            phone_number ="+20-123-123-123",
            phone_number_confirmed = False,
            two_factors_enabled = False,
        )
        await self.user_repo.change_password(
            user_id=user_id, password="WalkLikeAnEgiptian"
        )

    async def setup_groups_roles(self, engine: AsyncEngine) -> None:
        await self.setup_base(engine)
        group_repo = GroupRepository(engine)
        groups:list[dict[str, Any]] = [
            {"name": "Polnareff", "parent_group": None},
            {"name": "Giorno", "parent_group": None},
        ]
        for group in groups:
            try:
                name = group["name"]
                parent_group = group["parent_group"]
                if type(name) is str and (parent_group is None or type(parent_group) is int):
                    await group_repo.create(
                            name=name,
                            parent_group=parent_group,
                        )
            except DuplicationError:
                if group["name"]:
                    logger.info(group["name"] + " group already exists")

        groups = [
            {
                "name": "Gold",
                "parent_group": (
                    await group_repo.get_group_by_name(name="Giorno")
                ).id,
            },
            {
                "name": "Expirience",
                "parent_group": (
                    await group_repo.get_group_by_name(name="Giorno")
                ).id,
            },
            {
                "name": "Silver",
                "parent_group": (
                    await group_repo.get_group_by_name(name="Polnareff")
                ).id,
            },
            {
                "name": "Silver",
                "parent_group": (
                    await group_repo.get_group_by_name(name="Polnareff")
                ).id,
            },
        ]
        for group in groups:
            try:
                await group_repo.create(**group)
            except DuplicationError:
                logger.info(group["name"] + " group already exists")

        groups = [
            {
                "name": "Reqiuem",
                "parent_group": (
                    await group_repo.get_group_by_name(name="Expirience")
                ).id,
            }
        ]
        for group in groups:
            try:
                await group_repo.create(**group)
            except DuplicationError:
                if group["name"]:
                    logger.info(group["name"] + " group already exists")

        role_repo = RoleRepository(engine)
        role_repo.delete
        for role in ("Standuser", "French", "Italian", "Vampire"):
            try:
                await role_repo.create(name=role)
            except DuplicationError:
                logger.info(role + " role already exists")

    async def test_get_group(self, engine: AsyncEngine, client: AsyncClient) -> None:
        await self.setup_base(
            engine,
        )
        await self.setup_groups_roles(engine)

        headers = {
            "access-token": self.access_token,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        params = {
            "group_id": (
                await self.group_repo.get_group_by_name("Polnareff")
            ).id
        }

        response = await client.request(
            "GET",
            "/administration/group/get_group",
            headers=headers,
            params=params,
        )
        assert response.status_code == status.HTTP_200_OK
        response_content = json.loads(response.content.decode("utf-8"))
        logger.info(response_content)
        assert response_content["name"] == "Polnareff"

    async def test_get_all_group(self, engine: AsyncEngine, client: AsyncClient) -> None:
        await self.setup_base(
            engine,
        )
        await self.setup_groups_roles(engine)

        headers = {
            "access-token": self.access_token,
            "Content-Type": "application/x-www-form-urlencoded",
        }

        response = await client.request(
            "GET", "/administration/group/get_all_groups", headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        response_content = json.loads(response.content.decode("utf-8"))
        logger.info(response_content)
        assert len(response_content["all_groups"]) >= 6

    async def test_get_subgroups(self, engine: AsyncEngine, client: AsyncClient) -> None:
        await self.setup_base(
            engine,
        )
        await self.setup_groups_roles(engine)

        headers = {
            "access-token": self.access_token,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        params = {
            "group_id": (
                await self.group_repo.get_group_by_name(name="Giorno")
            ).id
        }

        response = await client.request(
            "GET",
            "/administration/group/get_subgroups",
            headers=headers,
            params=params,
        )
        assert response.status_code == status.HTTP_200_OK
        response_content = json.loads(response.content.decode("utf-8"))
        logger.info(response_content)
        for group in list(response_content.values())[0]:
            if group["subgroups"] is not None:
                break
        else:
            raise AssertionError

    async def test_delete_group(self, engine: AsyncEngine, client: AsyncClient) -> None:
        await self.setup_base(
            engine,
        )
        await self.setup_groups_roles(engine)

        headers = {
            "access-token": self.access_token,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        params = {
            "group_id": (
                await self.group_repo.get_group_by_name(name="Giorno")
            ).id
        }

        response = await client.request(
            "DELETE",
            "/administration/group/delete_group",
            headers=headers,
            data=params,
        )
        assert response.status_code == status.HTTP_200_OK
        headers = {"access-token": self.access_token}
        response = await client.request(
            "GET",
            "/administration/group/get_group",
            headers=headers,
            params=params,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_create_update_group(self, engine: AsyncEngine, client: AsyncClient) -> None:
        await self.setup_base(
            engine,
        )
        try:
            await self.group_repo.delete(
                (await self.group_repo.get_group_by_name("Diavolo")).id
            )
        except:
            pass
        headers = {
            "access-token": self.access_token,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        params = {"name": "Diavolo"}

        response = await client.request(
            "POST",
            "/administration/group/new_group",
            headers=headers,
            data=params,
        )
        assert response.status_code == status.HTTP_200_OK

        headers = {
            "access-token": self.access_token,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        params = {
            "group_id": (await self.group_repo.get_group_by_name("Diavolo")).id,
            "name": "Doppio",
        }

        response = await client.request(
            "PUT",
            "/administration/group/update_group",
            headers=headers,
            data=params,
        )
        assert response.status_code == status.HTTP_200_OK

        await self.group_repo.delete(
            (await self.group_repo.get_group_by_name("Doppio")).id
        )
