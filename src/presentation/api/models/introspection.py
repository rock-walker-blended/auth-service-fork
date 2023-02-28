from dataclasses import dataclass
from typing import Optional

from fastapi import Form
from pydantic import BaseModel


@dataclass
class BodyRequestIntrospectionModel:
    token: str = Form(...)
    token_type_hint: str = Form(None)

    class Config:
        orm_mode = True

    def __repr__(self) -> str:
        return f"Model {self.__class__.__name__}"  # pragma: no coverage


class ResponceIntrospectionModel(BaseModel):
    active: bool
    scope: Optional[str]
    client_id: Optional[str]
    username: Optional[str]
    token_type: Optional[str]
    exp: Optional[int]
    iat: Optional[int]
    nbf: Optional[int]
    sub: Optional[str]
    aud: Optional[str]
    iss: Optional[str]
    jti: Optional[str]

    class Config:
        orm_mode = True

    def __repr__(self) -> str:
        return f"Model {self.__class__.__name__}"  # pragma: no coverage
