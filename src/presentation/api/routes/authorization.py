from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Optional, Union

from fastapi import APIRouter, Cookie, Depends, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.templating import _TemplateResponse

from src.business_logic.authorization import AuthServiceFactory
from src.business_logic.authorization.dto import AuthRequestModel
from src.business_logic.services import LoginFormService
from src.data_access.postgresql.errors import (
    ClientNotFoundError,
    ClientRedirectUriError,
    ClientScopesError,
    UserNotFoundError,
    WrongPasswordError,
    WrongResponseTypeError,
)
from src.di.providers import (
    provide_auth_service_factory_stub,
    provide_login_form_service_stub,
)
from src.dyna_config import DOMAIN_NAME
from src.presentation.api.models import RequestModel

if TYPE_CHECKING:
    from src.business_logic.authorization import AuthServiceProtocol

AuthorizePostEndpointResponse = Union[RedirectResponse, JSONResponse]
AuthorizeGetEndpointResponse = Union[JSONResponse, _TemplateResponse]

logger = logging.getLogger(__name__)

templates = Jinja2Templates(directory="src/presentation/api/templates/")

auth_router = APIRouter(prefix="/authorize", tags=["Authorization"])


@auth_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
async def get_authorize(
    request: Request,
    request_model: RequestModel = Depends(),
    auth_class: LoginFormService = Depends(provide_login_form_service_stub),
) -> AuthorizeGetEndpointResponse:
    try:
        auth_class.request_model = request_model
        return_form = await auth_class.get_html_form()
        external_logins: Optional[dict[str, dict[str, Any]]] = {}
        if request_model.response_type == "code":
            external_logins = await auth_class.form_providers_data_for_auth()

        if return_form:
            return templates.TemplateResponse(
                "login_form.html",
                {
                    "request": request,
                    "request_model": request_model,
                    "external_logins": external_logins,
                    "base_url": DOMAIN_NAME,
                },
                status_code=200,
            )
        raise ValueError

    except ClientNotFoundError as exception:
        logger.exception(exception)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Client not found"},
        )
    except ClientRedirectUriError as exception:
        logger.exception(exception)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Redirect Uri not found"},
        )
    except WrongResponseTypeError as exception:
        logger.exception(exception)
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"message": "Bad response type"},
        )


@auth_router.post("/", status_code=status.HTTP_302_FOUND)
async def post_authorize(
    request_body: AuthRequestModel = Depends(AuthRequestModel.as_form),
    auth_service_factory: AuthServiceFactory = Depends(
        provide_auth_service_factory_stub
    ),
    user_code: Optional[str] = Cookie(None),
) -> AuthorizePostEndpointResponse:
    try:
        setattr(request_body, "user_code", user_code)
        auth_service: AuthServiceProtocol = (
            auth_service_factory.get_service_impl(request_body.response_type)
        )
        result = await auth_service.get_redirect_url(request_body)
        return RedirectResponse(result, status_code=status.HTTP_302_FOUND)

    except ClientNotFoundError as exception:
        logger.exception(exception)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Client not found"},
        )
    except UserNotFoundError as exception:
        logger.exception(exception)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "User not found"},
        )
    except WrongPasswordError as exception:
        logger.exception(exception)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Bad password"},
        )
    except ClientRedirectUriError as exception:
        logger.exception(exception)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Redirect Uri not found"},
        )
    except ClientScopesError as e:
        logger.exception(e)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Invalid scope"},
        )