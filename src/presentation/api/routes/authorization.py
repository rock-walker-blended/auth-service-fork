import logging

from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from src.business_logic.services import AuthorizationService, LoginFormService
from src.data_access.postgresql.errors import (
    ClientNotFoundError,
    UserNotFoundError,
    WrongPasswordError,
    ClientRedirectUriError
)
from src.presentation.api.models import DataRequestModel, RequestModel
from src.di.providers import provide_auth_service_stub, provide_login_form_service_stub


logger = logging.getLogger("is_app")

templates = Jinja2Templates(directory="src/presentation/api/templates/")

auth_router = APIRouter(
    prefix="/authorize",
)


@auth_router.get("/", status_code=status.HTTP_200_OK, tags=["Authorization"], response_class=HTMLResponse)
async def get_authorize(
    request: Request,
    request_model: RequestModel = Depends(),
    auth_class: LoginFormService = Depends(provide_login_form_service_stub),
):
    try:
        print('1111111111111111111111111111111111111111111')

        auth_class = auth_class
        auth_class.request_model = request_model
        return_form = await auth_class.get_html_form()
        if return_form:
            return templates.TemplateResponse(
                "login_form.html",
                {"request": request, "request_model": request_model},
                status_code=200
            )

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
    except WrongPasswordError as exception:
        logger.exception(exception)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Bad password"},
        )


@auth_router.post(
    "/", status_code=status.HTTP_302_FOUND, tags=["Authorization"]
)
async def post_authorize(
    request_body: DataRequestModel = Depends(),
    auth_class: AuthorizationService = Depends(provide_auth_service_stub),
):
    try:
        request_model = RequestModel(**request_body.__dict__)
        auth_class = auth_class
        auth_class.request_model = request_model
        firmed_redirect_uri = await auth_class.get_redirect_url()
        response = RedirectResponse(
            firmed_redirect_uri, status_code=status.HTTP_302_FOUND
        )

        return response
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
    except KeyError as exception:
        message = (
            f"KeyError: key {exception} does not exist is not in the scope"
        )
        logger.exception(message)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message": "The scope is missing a password, or a username"
            },
        )
    except IndexError as exception:
        message = f"IndexError: {exception} - Impossible to parse the scope"
        logger.exception(message)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Impossible to parse the scope"},
        )
