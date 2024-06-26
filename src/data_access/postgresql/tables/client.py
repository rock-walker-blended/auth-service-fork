import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table
)
from sqlalchemy.orm import relationship

from .base import Base, BaseModel

clients_scopes = Table(
    "clients_scopes",
    BaseModel.metadata,
    Column(
        "client_id", ForeignKey("clients.id", ondelete="CASCADE"),  primary_key=True,
    ),
    Column(
        "scope_id", ForeignKey("client_scopes.id", ondelete="CASCADE"), primary_key=True
    ),
)

clients_response_types = Table(
    "clients_response_types",
    BaseModel.metadata,
    Column(
        "client_id", ForeignKey("clients.id", ondelete="CASCADE"),  primary_key=True,
    ),
    Column(
        "response_type_id", ForeignKey("response_types.id", ondelete="CASCADE"), primary_key=True
    ),
)

clients_grant_types = Table(
    "clients_grant_types",
    BaseModel.metadata,
    Column(
        "client_id", ForeignKey("clients.id", ondelete="CASCADE"),  primary_key=True,
    ),
    Column(
        "persistent_grant_type_id", ForeignKey("persistent_grant_types.id", ondelete="CASCADE"), primary_key=True
    ),
)

class Client(BaseModel):
    __tablename__ = "clients"

    client_id = Column(String(80), nullable=False, unique=True)
    absolute_refresh_token_lifetime = Column(
        Integer, default=2592000, nullable=False
    )
    access_token_lifetime = Column(Integer, default=3600, nullable=False)
    access_token_type_id = Column(
        Integer,
        ForeignKey("access_token_types.id", ondelete="CASCADE"),
        nullable=False,
    )
    access_token_type = relationship(
        "AccessTokenType",
        backref="client",
        foreign_keys="Client.access_token_type_id",
        lazy = 'joined'
    )
    allow_access_token_via_browser = Column(
        Boolean, default=False, nullable=False
    )
    allow_offline_access = Column(Boolean, default=False, nullable=False)
    allow_plain_text_pkce = Column(Boolean, default=False, nullable=False)
    allow_remember_consent = Column(Boolean, default=True, nullable=False)
    always_include_user_claims_id_token = Column(
        Boolean, default=False, nullable=False
    )
    always_send_client_claims = Column(Boolean, default=False, nullable=False)
    authorization_code_lifetime = Column(Integer, default=300, nullable=False)
    device_code_lifetime = Column(Integer, default=600, nullable=False)
    client_name = Column(String(50), nullable=False)
    client_uri = Column(String(65), default="*enter_here*", nullable=False)
    enable_local_login = Column(Boolean, default=True)
    enabled = Column(Boolean, default=True)
    identity_token_lifetime = Column(Integer, default=300, nullable=False)
    include_jwt_id = Column(Boolean, default=False, nullable=False)
    logo_uri = Column(String, default="*enter_here*", nullable=False)
    logout_session_required = Column(Boolean, default=False, nullable=False)
    logout_uri = Column(String, default="*enter_here*", nullable=False)
    token_endpoint_auth_method = Column(String, default="client_secret_post", nullable=False)
    prefix_client_claims = Column(
        String,
        default="*enter_here*",
    )

    protocol_type_id = Column(
        Integer,
        ForeignKey("protocol_types.id", ondelete="CASCADE"),
        nullable=False,
    )
    protocol_type = relationship(
        "ProtocolType",
        backref="client",
    )

    refresh_token_expiration_type_id = Column(
        Integer,
        ForeignKey("refresh_token_expiration_types.id", ondelete="CASCADE"),
        nullable=False,
    )
    refresh_token_expiration_type = relationship(
        "RefreshTokenExpirationType",
        backref="client",
        lazy = 'joined'
    )

    refresh_token_usage_type_id = Column(
        Integer,
        ForeignKey("refresh_token_usage_types.id", ondelete="CASCADE"),
        nullable=False,
    )
    refresh_token_usage_type = relationship(
        "RefreshTokenUsageType",
        backref="client",
        lazy = 'joined'
    )

    require_client_secret = Column(Boolean, default=True, nullable=False)
    require_consent = Column(Boolean, default=True, nullable=False)
    require_pkce = Column(Boolean, default=False, nullable=False)
    sliding_refresh_token_lifetime = Column(
        Integer, default=1296000, nullable=False
    )
    update_access_token_claims_on_refresh = Column(
        Boolean, default=False, nullable=False
    )

    grants = relationship(
        "PersistentGrant",
        back_populates="client"
    )
    secrets = relationship("ClientSecret", back_populates="client", lazy="subquery")
    redirect_uris = relationship("ClientRedirectUri", backref="client", lazy = "subquery")
    claims = relationship("ClientClaim", back_populates="client")
    post_logout_redirect_uris = relationship(
        "ClientPostLogoutRedirectUri", 
        back_populates="client",
        lazy = 'subquery'
    )
    ##############################################
    scope = relationship(
        "ClientScope", 
        secondary=clients_scopes,
        back_populates="client",
        lazy = 'subquery'
        )
    
    cors_origins = relationship(
        "ClientCorsOrigin",
        back_populates="client",
        lazy = 'subquery'
    )
    id_restrictions = relationship(
        "ClientIdRestriction", 
        back_populates="client",
        lazy = 'subquery'
    )
    grant_types = relationship(
        "PersistentGrantType",
        secondary=clients_grant_types,
        cascade="all,delete",
        # lazy = '
    )
    
    response_types = relationship(
        "ResponseType",
        secondary=clients_response_types,
        cascade="all,delete",
        lazy = "subquery"
    )
    
    devices = relationship(
        "Device",
        back_populates = 'client',    
    )

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.id} id: {self.client_name}"

    def __repr__(self) -> str:  # pragma: no cover
        return f"{self.id} id: {self.client_name}"

class ResponseType(Base):
    __tablename__ = "response_types"
    id = Column(Integer, primary_key=True)
    type = Column(String, unique=True)
    def __str__(self) -> str:  # pragma: no cover
        return f"{self.type}"

    def __repr__(self) -> str:  # pragma: no cover
        return f"{self.type}"


class AccessTokenType(BaseModel):
    __tablename__ = "access_token_types"
    type = Column(String, unique=True)

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.type}"

    def __repr__(self) -> str:  # pragma: no cover
        return f"{self.type}"


class ProtocolType(BaseModel):
    __tablename__ = "protocol_types"
    id = Column(Integer, primary_key=True)
    type = Column(String, unique=True)

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.type}"

    def __repr__(self) -> str:  # pragma: no cover
        return f"{self.type}"


class RefreshTokenExpirationType(BaseModel):
    __tablename__ = "refresh_token_expiration_types"
    type = Column(String, unique=True)

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.type}"

    def __repr__(self) -> str:  # pragma: no cover
        return f"{self.type}"


class RefreshTokenUsageType(BaseModel):
    __tablename__ = "refresh_token_usage_types"
    type = Column(String, unique=True)

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.type}"

    def __repr__(self) -> str:  # pragma: no cover
        return f"{self.type}"


class ClientIdRestriction(BaseModel):
    __tablename__ = "client_id_restrictions"

    provider = Column(String, nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"))
    client = relationship(
        "Client",
        back_populates="id_restrictions",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"{self.provider}"


class ClientClaim(BaseModel):
    __tablename__ = "client_claims"

    type = Column(String, nullable=False)
    value = Column(String, nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"))
    client = relationship(
        "Client",
        back_populates="claims",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"{self.type}"


# class ClientScope(BaseModel):
#     __tablename__ = "client_scopes"

#     scope = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), unique=True)
#     client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), unique=True)
#     client = relationship(
#         "Client",
#         back_populates="scopes",
#     )

#     def __str__(self) -> str:  # pragma: no cover
#         return f"{self.scope}"

#     def __repr__(self) -> str:  # pragma: no cover
#         return f"{self.scope}"


class ClientPostLogoutRedirectUri(BaseModel):
    __tablename__ = "client_post_logout_redirect_uris"

    post_logout_redirect_uri = Column(String, nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), )
    client = relationship(
        "Client",
        back_populates="post_logout_redirect_uris",
    )

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.post_logout_redirect_uri}"

    def __repr__(self) -> str:  # pragma: no cover
        return f"Model {self.__class__.__name__}: {self.id}"


class ClientCorsOrigin(BaseModel):
    __tablename__ = "client_cors_origins"

    origin = Column(String, nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"))
    client = relationship(
        "Client",
        back_populates="cors_origins",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"Model {self.__class__.__name__}: {self.id}"


class ClientRedirectUri(BaseModel):
    __tablename__ = "client_redirect_uris"

    redirect_uri = Column(String, nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"))
    # client = relationship("Client", back_populates="redirect_uris")

    def __repr__(self) -> str:  # pragma: no cover
        return f"Model {self.__class__.__name__}: {self.id}"


class ClientSecret(BaseModel):
    __tablename__ = "client_secrets"

    description = Column(String, nullable=False)
    expiration = Column(Integer, nullable=False)
    type = Column(String, nullable=False)
    value = Column(String, nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), unique=True)
    client = relationship("Client", back_populates="secrets")

    def __repr__(self) -> str:  # pragma: no cover
        return f"Model {self.__class__.__name__}: {self.type}"
