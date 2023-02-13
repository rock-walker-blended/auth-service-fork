import logging

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send

from src.business_logic.services.jwt_token import JWTService

logger = logging.getLogger(__name__)


class AccessTokenMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, jwt_service: JWTService = JWTService()):
        self.app = app
        self.jwt_service = jwt_service

    async def dispatch_func(self, request: Request, call_next):

        if "/administration/" in request.url.path:
            token = request.headers.get("access-token")

            try:
                if not await self.jwt_service.verify_token(token):
                    logger.exception("403 Incorrect Access Token")
                    return JSONResponse(
                        status_code=status.HTTP_403_FORBIDDEN,
                        content="Incorrect Access Token",
                    )
                else:
                    logger.info("Access Token Auth Passed")

                    response = await call_next(request)
                    return response
            except:
                logger.exception("403 Incorrect Access Token")
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content="Incorrect Access Token",
                )
        else:
            response = await call_next(request)
            return response
