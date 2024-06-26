import factory
from factory.alchemy import SQLAlchemyModelFactory
from factory.fuzzy import FuzzyChoice

import factories.data.data_for_factories as data
import factories.factory_session as sess
import src.data_access.postgresql.tables.client as client
import src.data_access.postgresql.tables.resources_related as res


class ClientFactory(SQLAlchemyModelFactory):
    class Meta:
        model = client.Client
        sqlalchemy_session = sess.session
        sqlalchemy_get_or_create = ("client_id",)

    client_id = factory.Iterator(data.CLIENT_IDS.values())
    absolute_refresh_token_lifetime = factory.Faker(
        "pyint", min_value=3600, max_value=50000
    )
    access_token_lifetime = factory.Faker(
        "pyint", min_value=300, max_value=10000
    )
    access_token_type_id = factory.Faker("pyint", min_value=1, max_value=2)
    allow_access_token_via_browser = FuzzyChoice([True, False])
    allow_offline_access = factory.Faker("pybool")
    allow_plain_text_pkce = factory.Faker("pybool")
    allow_remember_consent = factory.Faker("pybool")
    always_include_user_claims_id_token = factory.Faker("pybool")
    always_send_client_claims = factory.Faker("pybool")
    authorization_code_lifetime = factory.Faker(
        "pyint", min_value=600, max_value=50000
    )
    device_code_lifetime = factory.Faker(
        "pyint", min_value=600, max_value=50000
    )
    client_name = factory.Faker("user_name")
    client_uri = factory.Faker("url")
    enable_local_login = factory.Faker("pybool")
    enabled = factory.Faker("pybool")
    identity_token_lifetime = factory.Faker("random_number")
    include_jwt_id = factory.Faker("pybool")
    logo_uri = factory.Faker("url")
    logout_session_required = factory.Faker("pybool")
    logout_uri = factory.Faker("url")
    prefix_client_claims = factory.Faker("word")
    protocol_type_id = factory.Faker("pyint", min_value=1, max_value=1)
    refresh_token_expiration_type_id = factory.Faker(
        "pyint", min_value=1, max_value=2
    )
    refresh_token_usage_type_id = factory.Faker(
        "pyint", min_value=1, max_value=2
    )
    require_client_secret = factory.Faker("pybool")
    require_consent = factory.Faker("pybool")
    require_pkce = factory.Faker("pybool")
    sliding_refresh_token_lifetime = factory.Faker(
        "pyint", min_value=300, max_value=1296000
    )
    update_access_token_claims_on_refresh = FuzzyChoice([True, False])


class ClientIdRestrictionFactory(SQLAlchemyModelFactory):
    class Meta:
        model = client.ClientIdRestriction
        sqlalchemy_session = sess.session

    provider = factory.Faker("word")
    client_id = factory.SubFactory(ClientFactory)


class ClientClaimFactory(SQLAlchemyModelFactory):
    class Meta:
        model = client.ClientClaim
        sqlalchemy_session = sess.session

    type = factory.Faker("word")
    value = factory.Faker("word")
    client_id = factory.SubFactory(ClientFactory)


  


class ClientPostLogoutRedirectUriFactory(SQLAlchemyModelFactory):
    class Meta:
        model = client.ClientPostLogoutRedirectUri
        sqlalchemy_session = sess.session

    post_logout_redirect_uri = factory.Faker("url")
    client_id = factory.SubFactory(ClientFactory)


class ClientCorsOriginFactory(SQLAlchemyModelFactory):
    class Meta:
        model = client.ClientCorsOrigin
        sqlalchemy_session = sess.session

    origin = factory.Faker("sentence")
    client_id = factory.SubFactory(ClientFactory)


class ClientRedirectUriFactory(SQLAlchemyModelFactory):
    class Meta:
        model = client.ClientRedirectUri
        sqlalchemy_session = sess.session

    redirect_uri = factory.Faker("url")
    client_id = factory.SubFactory(ClientFactory)


class ClientSecretFactory(SQLAlchemyModelFactory):
    class Meta:
        model = client.ClientSecret
        sqlalchemy_session = sess.session

    description = factory.Faker("sentence")
    expiration = factory.Faker("random_number")
    type = factory.Faker("word")
    value = factory.Faker("word")
    client_id = factory.SubFactory(ClientFactory)

class AccessTokenTypeFactory(SQLAlchemyModelFactory):
    class Meta:
        model = client.AccessTokenType
        sqlalchemy_session = sess.session

    type = factory.Iterator(["jwt", "reference"])

class ResponseTypeFactory(SQLAlchemyModelFactory):
    class Meta:
        model = client.ResponseType
        sqlalchemy_session = sess.session

    type = factory.Iterator(data.RESPONSE_TYPES)

class ProtocolTypeFactory(SQLAlchemyModelFactory):
    class Meta:
        model = client.ProtocolType
        sqlalchemy_session = sess.session

    type = factory.Iterator(["open_id_connect"])


class RefreshTokenExpirationTypeFactory(SQLAlchemyModelFactory):
    class Meta:
        model = client.RefreshTokenExpirationType
        sqlalchemy_session = sess.session

    type = factory.Iterator(["absolute", "sliding"])


class RefreshTokenUsageTypeFactory(SQLAlchemyModelFactory):
    class Meta:
        model = client.RefreshTokenUsageType
        sqlalchemy_session = sess.session

    type = factory.Iterator(["one_time_only", "reuse"])

class ClientsScopeFactory(SQLAlchemyModelFactory):
    class Meta:
        model = client.clients_scopes
        sqlalchemy_session = sess.session

    # client_id = factory.SubFactory(client.ClientFactory)
    client_id = factory.SubFactory(client.Client)
    scope_id = factory.SubFactory(res.ClientScope)
    