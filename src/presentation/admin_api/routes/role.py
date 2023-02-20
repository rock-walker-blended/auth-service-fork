import logging
from functools import wraps

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status

from src.business_logic.services.admin_api import AdminRoleService
from src.data_access.postgresql.errors.user import DuplicationError
from src.di.providers.services import provide_admin_role_service_stub
from src.presentation.admin_api.models.role import *

logger = logging.getLogger(__name__)

admin_role_router = APIRouter(prefix="/roles")


def exceptions_wrapper(func):
    @wraps(func)
    async def inner(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Not found"
            )
        except DuplicationError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Duplication"
            )
        except:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="INTERNAL_SERVER_ERROR",
            )

    return inner


@admin_role_router.get(
    "/{role_id}", response_model=dict, tags=["Administration Role"], description="Get the Role"
)
@exceptions_wrapper
async def get_role(
    request: Request,
    role_id:int,
    access_token: str = Header(description="Access token"),
    role_class: AdminRoleService = Depends(provide_admin_role_service_stub),
):

    role_class = role_class

    result = await role_class.get_role(role_id=role_id)
    return {"role": result}


@admin_role_router.get(
    "", response_model=dict, tags=["Administration Role"], description="Get All Roles"
)
@exceptions_wrapper
async def get_all_roles(
    request: Request,
    access_token: str = Header(description="Access token"),
    role_class: AdminRoleService = Depends(provide_admin_role_service_stub),
):
    role_class = role_class
    return {"all_roles": await role_class.get_all_roles()}


@admin_role_router.post(
    "", status_code=status.HTTP_200_OK, tags=["Administration Role"], description="Create a New Role"
)
@exceptions_wrapper
async def create_role(
    request: Request,
    access_token: str = Header(description="Access token"),
    request_model: RequestNewRoleModel = Depends(),
    role_class: AdminRoleService = Depends(provide_admin_role_service_stub),
):
    role_class = role_class
    await role_class.create_role(name=request_model.name)


@admin_role_router.put(
    "/{role_id}", status_code=status.HTTP_200_OK, tags=["Administration Role"], description="Update the Role"
)
@exceptions_wrapper
async def update_role(
    request: Request,
    role_id:int,
    access_token: str = Header(description="Access token"),
    request_model: RequestUpdateRoleModel = Depends(),
    role_class: AdminRoleService = Depends(provide_admin_role_service_stub),
):
    role_class = role_class
    await role_class.update_role(
        role_id=role_id, name=request_model.name
    )


@admin_role_router.delete(
    "/{role_id}", status_code=status.HTTP_200_OK, tags=["Administration Role"], description="Delete the Role"
)
@exceptions_wrapper
async def delete_group(
    request: Request,
    role_id:int,
    access_token: str = Header(description="Access token"),
    role_class: AdminRoleService = Depends(provide_admin_role_service_stub),
):
    role_class = role_class
    await role_class.delete_role(role_id=role_id)
