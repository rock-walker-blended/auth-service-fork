from src.data_access.postgresql.tables.users import UserClaim, USER_CLAIM_TYPE
from src.data_access.postgresql.tables.persistent_grant import PersistentGrant
from src.data_access.postgresql.tables.persistent_grant import TYPES_OF_GRANTS
from src.business_logic.services.jwt_token import JWTService
from jwkest import long_to_base64, base64_to_long
import logging

from jwkest import base64_to_long, long_to_base64
from fastapi import Request
from src.business_logic.services.jwt_token import JWTService
from src.data_access.postgresql.tables.persistent_grant import PersistentGrant
from src.data_access.postgresql.tables.users import UserClaim
from typing import Any, Union

logger = logging.getLogger(__name__)


class WellKnownServies:
    def __init__(self) -> None:
        self.request:Union[Request, Any] =None
        
    def get_list_of_types(
        self, list_of_types: list[Any] = [("Not ready yet", "")]
    ) -> list[str]:
        return [claim[0] for claim in list_of_types]

    def get_all_urls(self, result:dict[str, Any]) -> dict[str, Any]:
        if self.request is None:
            raise ValueError
        return {
            route.name: result["issuer"] + route.path
            for route in self.request.app.routes
        } | {"false": "/ Not ready yet"}

    async def get_openid_configuration(
        self,
    ) -> dict[str, Any]:
        if self.request is None:
            raise ValueError
       
        # For key description: https://ldapwiki.com/wiki/Openid-configuration
        
        # REQUIRED
        result:dict[str, Any] ={}
        result["issuer"] = str(self.request.url).replace(
                "/.well-known/openid-configuration", ""
            )
        

        urls_dict = self.get_all_urls(result)

        result["jwks_uri"] = urls_dict["false"]
        result["authorization_endpoint"] = urls_dict["get_authorize"]
        result[
            "id_token_signing_alg_values_supported"
        ] = self.get_list_of_types()
        result["subject_types_supported"] = self.get_list_of_types()
        result["response_types_supported"] = self.get_list_of_types()

        # may be REQUIRED
        result["token_endpoint"] = urls_dict["get_tokens"]
        result["end_session_endpoint"] = urls_dict["false"]
        result["check_session_iframe"] = urls_dict["false"]

        # RECOMMENDED
        result["claims_supported"] = self.get_list_of_types(
            USER_CLAIM_TYPE
        )
        result["scopes_supported"] = self.get_list_of_types()
        result["registration_endpoint"] = urls_dict["false"]
        result["userinfo_endpoint"] = urls_dict["get_userinfo"]

        # OPTIONAL
        result["frontchannel_logout_session_supported"] = False  # i don't know
        result["frontchannel_logout_supported"] = False  # i don't know
        result["op_tos_uri"] = urls_dict["false"]
        result["op_policy_uri"] = urls_dict["false"]
        result["require_request_uri_registration"] = False  # i don't know
        result["request_uri_parameter_supported"] = False  # i don't know
        result["request_parameter_supported"] = False  # i don't know
        result["claims_parameter_supported"] = False  # i don't know
        result["ui_locales_supported"] = self.get_list_of_types()
        result["claims_locales_supported"] = self.get_list_of_types()
        result["service_documentation"] = self.get_list_of_types()
        result["claim_types_supported"] = self.get_list_of_types()
        result["display_values_supported"] = self.get_list_of_types()
        result[
            "token_endpoint_auth_signing_alg_values_supported"
        ] = self.get_list_of_types()
        result[
            "token_endpoint_auth_methods_supported"
        ] = self.get_list_of_types()
        result[
            "request_object_encryption_enc_values_supported"
        ] = self.get_list_of_types()
        result[
            "request_object_encryption_alg_values_supported"
        ] = self.get_list_of_types()
        result[
            "request_object_signing_alg_values_supported"
        ] = self.get_list_of_types()
        result[
            "userinfo_encryption_enc_values_supported"
        ] = self.get_list_of_types()
        result[
            "userinfo_encryption_alg_values_supported"
        ] = self.get_list_of_types()
        result[
            "userinfo_signing_alg_values_supported"
        ] = self.get_list_of_types()
        result[
            "id_token_encryption_enc_values_supported"
        ] = self.get_list_of_types()
        result[
            "id_token_encryption_alg_values_supported"
        ] = self.get_list_of_types()
        result["acr_values_supported"] = self.get_list_of_types()
        result["grant_types_supported"] = self.get_list_of_types(TYPES_OF_GRANTS)
        result["response_modes_supported"] = self.get_list_of_types()
        # result[""] = urls_dict['false']

        return result

    async def get_jwks(self) -> dict[str, Any]:
        jwt_service = JWTService()
        kty = ""
        if "RS" in jwt_service.algorithm:
            kty = "RSA"
        elif "HS" in jwt_service.algorithm:
            kty = "HMAC"
        else:
            raise ValueError

        result = {
            "kty": kty,
            "alg": jwt_service.algorithm,
            "use": "sig",
            # "kid" : ... ,
            "n": long_to_base64(await jwt_service.get_module()),
            "e": long_to_base64(await jwt_service.get_pub_key_expanent()),
        }
        logger.info(
            f"n =  {base64_to_long(result['n'])}\ne = {base64_to_long(result['e'])}"
        )
        return result
