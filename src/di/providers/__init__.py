from .config import provide_config
from .db import provide_db
from .repositories import (
    provide_wellknown_repo,
    provide_wellknown_repo_stub,
    provide_client_repo,
    provide_client_repo_stub,
    provide_device_repo,
    provide_device_repo_stub,
    provide_group_repo,
    provide_persistent_grant_repo,
    provide_persistent_grant_repo_stub,
    provide_role_repo,
    provide_third_party_oidc_repo,
    provide_third_party_oidc_repo_stub,
    provide_user_repo,
    provide_user_repo_stub,
    provide_blacklisted_repo,
    provide_blacklisted_repo_stub
)
from .services import (
    provide_wellknown_service,
    provide_wellknown_service_stub,
    provide_admin_auth_service,
    provide_admin_auth_service_stub,
    provide_admin_group_service,
    provide_admin_group_service_stub,
    provide_admin_role_service,
    provide_admin_role_service_stub,
    provide_admin_user_service,
    provide_admin_user_service_stub,
    provide_auth_service,
    provide_auth_service_stub,
    provide_auth_third_party_linkedin_service,
    provide_auth_third_party_linkedin_service_stub,
    provide_auth_third_party_oidc_service,
    provide_auth_third_party_oidc_service_stub,
    provide_third_party_google_service_stub,
    provide_third_party_google_service,
    provide_third_party_facebook_service_stub,
    provide_third_party_facebook_service,
    provide_third_party_gitlab_service_stub,
    provide_third_party_gitlab_service,
    provide_third_party_microsoft_service_stub,
    provide_third_party_microsoft_service,
    provide_device_service,
    provide_device_service_stub,
    provide_endsession_service,
    provide_endsession_service_stub,
    provide_introspection_service,
    provide_introspection_service_stub,
    provide_jwt_service,
    provide_jwt_service_stub,
    provide_login_form_service,
    provide_login_form_service_stub,
    provide_password_service,
    provide_password_service_stub,
    provide_token_service,
    provide_token_service_stub,
    provide_userinfo_service,
    provide_userinfo_service_stub,
)
