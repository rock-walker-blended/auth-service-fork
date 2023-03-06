import jwt
import mock
import pytest
from Crypto.PublicKey.RSA import construct
from jwkest import base64_to_long

from src.business_logic.services.jwt_token import JWTService
from src.business_logic.services.well_known import WellKnownServices
from typing import Any, no_type_check

class UrlMock:
    path = ''

class RequestMock:
    authorization = 0
    url  = UrlMock()

@no_type_check
async def decode_token(self, token: str) -> dict[str, Any]:
    token = token.replace("Bearer ", "")

    decoded = jwt.decode(
        token,
        key=self.keys.public_key,
        algorithms=self.algorithms
    )
    return decoded


@pytest.mark.asyncio
class TestWellKnownServices:

    # def setup_class(self) -> None:
    #     self.wks = WellKnownServices()
    #     self.wks.request = RequestMock()
    #     self.wks.request.url = "/localhost/.well-known/openid-configuration"

    def new_get_all_urls(self, *args:Any, **kwargs:Any) -> dict[str, str]:
        return {
            "openapi": "http://127.0.0.1:800...enapi.json",
            "swagger_ui_html": "http://127.0.0.1:8000/docs",
            "swagger_ui_redirect": "http://127.0.0.1:800...2-redirect",
            "redoc_html": "http://127.0.0.1:8000/redoc",
            "get_authorize": "http://127.0.0.1:800...authorize/",
            "post_authorize": "http://127.0.0.1:800...authorize/",
            "get_userinfo": "http://127.0.0.1:800.../userinfo/",
            "get_userinfo_jwt": "http://127.0.0.1:800...erinfo/jwt",
            "get_default_token": "http://127.0.0.1:800...ault_token",
            "get_openid_configuration": "http://127.0.0.1:800...figuration",
            "get_tokens": "http://127.0.0.1:800...token",
            "get_jwks": "http://127.0.0.1:800...jwks",
            "end_session": "http://127.0.0.1:800...end_session",
            "false": "/ Not ready yet",
        }

    async def test_well_known_openid_cofig(
            self,  
            wlk_services: WellKnownServices,
        ) -> None:
        with mock.patch.object(
                WellKnownServices, "get_all_urls", new=self.new_get_all_urls
        ):
            wks = wlk_services
            wks.request = RequestMock
            result = await wks.get_openid_configuration()
            dict_of_parametrs_and_types = {
                "issuer": str,
                "jwks_uri": str,
                "authorization_endpoint": str,
                "token_endpoint": str,
                "id_token_signing_alg_values_supported": list,
                "subject_types_supported": list,
                "response_types_supported": list,
                "claims_supported": list,
                "scopes_supported": list,
                "registration_endpoint": str,
                "userinfo_endpoint": str,
                "frontchannel_logout_session_supported": bool,
                "frontchannel_logout_supported": bool,
                "end_session_endpoint": str,
                "check_session_iframe": str,
                "op_tos_uri": str,
                "op_policy_uri": str,
                "require_request_uri_registration": bool,
                "request_uri_parameter_supported": bool,
                "request_parameter_supported": bool,
                "claims_parameter_supported": bool,
                "ui_locales_supported": list,
                "claims_locales_supported": list,
                "service_documentation": list,
                "claim_types_supported": list,
                "display_values_supported": list,
                "token_endpoint_auth_signing_alg_values_supported": list,
                "token_endpoint_auth_methods_supported": list,
                "request_object_encryption_enc_values_supported": list,
                "request_object_encryption_alg_values_supported": list,
                "request_object_signing_alg_values_supported": list,
                "userinfo_encryption_enc_values_supported": list,
                "userinfo_encryption_alg_values_supported": list,
                "userinfo_signing_alg_values_supported": list,
                "id_token_encryption_enc_values_supported": list,
                "id_token_encryption_alg_values_supported": list,
                "acr_values_supported": list,
                "grant_types_supported": list,
                "response_modes_supported": list,
            }

            for key in result.keys():
                assert type(result[key]) == dict_of_parametrs_and_types[key]

            KEYS_REQUIRED = (
                "issuer",
                "jwks_uri",
                "authorization_endpoint",
                "token_endpoint",
                "id_token_signing_alg_values_supported",
                "subject_types_supported",
                "response_types_supported",
            )

            for key in KEYS_REQUIRED:
                assert key in result.keys()

    async def test_jwks_RSA(self, wlk_services: WellKnownServices,) -> None:
        wks = wlk_services
        jwt_service = JWTService()
        result = await wks.get_jwks()
        test_token = await jwt_service.encode_jwt(payload={"sub": 1})

        if result["alg"] == "RS256":
            n = base64_to_long(result["n"])
            e = base64_to_long(result["e"])

            test_key = construct((n, e))

            assert jwt_service.keys.public_key == test_key.public_key().export_key('PEM')
            assert result["kty"] == "RSA"
            assert bool(await jwt_service.decode_token(
                token=test_token,
                # key=test_key.public_key().export_key('PEM'),
                # algorithms=["RS256", ]
            )
            )
            assert result["use"] == "sig"
