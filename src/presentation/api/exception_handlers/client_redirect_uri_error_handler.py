import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_404_NOT_FOUND

from src.data_access.postgresql.errors import ClientRedirectUriError

logger = logging.getLogger(__name__)


async def client_redirect_uri_error_handler(
    _: Request, exc: ClientRedirectUriError
) -> JSONResponse:
    logger.exception(exc)

    content = {"message": "Redirect Uri not found"}

    return JSONResponse(
        status_code=HTTP_404_NOT_FOUND,
        content=content,
    )
