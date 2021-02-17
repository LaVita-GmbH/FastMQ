from enum import Enum
from typing import Dict, Optional, List, Iterable, Callable, Any, Union
from pydantic import BaseModel, Field, AnyUrl
from ..logging import logger

try:
    import email_validator  # type: ignore

    assert email_validator  # make autoflake ignore the unused import
    from pydantic import EmailStr
except ImportError:  # pragma: no cover

    class EmailStr(str):  # type: ignore
        @classmethod
        def __get_validators__(cls) -> Iterable[Callable[..., Any]]:
            yield cls.validate

        @classmethod
        def validate(cls, v: Any) -> str:
            logger.warning(
                "email-validator not installed, email fields will be treated as str.\n"
                "To install, run: pip install email-validator"
            )
            return str(v)


class ExternalDocumentation(BaseModel):
    description: Optional[str] = None
    url: AnyUrl


class Contact(BaseModel):
    name: Optional[str] = None
    url: Optional[AnyUrl] = None
    email: Optional[EmailStr] = None


class License(BaseModel):
    name: str
    url: Optional[AnyUrl] = None


class Info(BaseModel):
    title: str
    description: Optional[str] = None
    termsOfService: Optional[str] = None
    contact: Optional[Contact] = None
    license: Optional[License] = None
    version: str


class ServerVariable(BaseModel):
    enum: Optional[List[str]] = None
    default: str
    description: Optional[str] = None


class ServerProtocol(Enum):
    amqp = 'amqp'
    amqps = 'amqps'
    http = 'http'
    https = 'https'
    jms = 'jms'
    kafka = 'kafka'
    kafka_secure = 'kafka-secure'
    mqtt = 'mqtt'
    secure_mqtt = 'secure-mqtt'
    stomp = 'stomp'
    stomps = 'stomps'
    ws = 'ws'
    wss = 'wss'


class Server(BaseModel):
    url: Union[AnyUrl, str]
    description: Optional[str] = None
    variables: Optional[Dict[str, ServerVariable]] = None
    protocol: ServerProtocol
    protocolVersion: str
    security: Optional[Dict[str, List[str]]] = None
    bindings: Optional[Dict[str, dict]] = None


class Reference(BaseModel):
    ref: str = Field(..., alias="$ref")


class Discriminator(BaseModel):
    propertyName: str
    mapping: Optional[Dict[str, str]] = None


class SchemaBase(BaseModel):
    ref: Optional[str] = Field(None, alias="$ref")
    title: Optional[str] = None
    multipleOf: Optional[float] = None
    maximum: Optional[float] = None
    exclusiveMaximum: Optional[float] = None
    minimum: Optional[float] = None
    exclusiveMinimum: Optional[float] = None
    maxLength: Optional[int] = Field(None, gte=0)
    minLength: Optional[int] = Field(None, gte=0)
    pattern: Optional[str] = None
    maxItems: Optional[int] = Field(None, gte=0)
    minItems: Optional[int] = Field(None, gte=0)
    uniqueItems: Optional[bool] = None
    maxProperties: Optional[int] = Field(None, gte=0)
    minProperties: Optional[int] = Field(None, gte=0)
    required: Optional[List[str]] = None
    enum: Optional[List[Any]] = None
    type: Optional[str] = None
    allOf: Optional[List[Any]] = None
    oneOf: Optional[List[Any]] = None
    anyOf: Optional[List[Any]] = None
    not_: Optional[Any] = Field(None, alias="not")
    items: Optional[Any] = None
    properties: Optional[Dict[str, Any]] = None
    additionalProperties: Optional[Union[Dict[str, Any], bool]] = None
    description: Optional[str] = None
    format: Optional[str] = None
    default: Optional[Any] = None
    nullable: Optional[bool] = None
    discriminator: Optional[Discriminator] = None
    readOnly: Optional[bool] = None
    writeOnly: Optional[bool] = None
    externalDocs: Optional[ExternalDocumentation] = None
    example: Optional[Any] = None
    deprecated: Optional[bool] = None


class Schema(SchemaBase):
    allOf: Optional[List[SchemaBase]] = None
    oneOf: Optional[List[SchemaBase]] = None
    anyOf: Optional[List[SchemaBase]] = None
    not_: Optional[SchemaBase] = Field(None, alias="not")
    items: Optional[SchemaBase] = None
    properties: Optional[Dict[str, SchemaBase]] = None
    additionalProperties: Optional[Union[Dict[str, Any], bool]] = None


class Parameter(BaseModel):
    location: Optional[str] = None
    description: Optional[str] = None
    schema: Optional[Schema] = None


class Tag(BaseModel):
    pass


class Components(BaseModel):
    pass


class CorrelationID(BaseModel):
    description: Optional[str] = None
    location: str


class MessageBase(BaseModel):
    headers: Optional[Union[Schema, Reference]] = None
    payload: Any
    correlationId: Optional[Union[CorrelationID, Reference]] = None
    schemaFormat: Optional[str] = None
    contentType: Optional[str] = None
    name: Optional[str] = None
    title: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[Tag]] = None
    externalDocs: Optional[ExternalDocumentation] = None
    bindings: Optional[Dict[str, dict]] = None
    examples: Optional[Dict[str, Any]] = None


class Message(MessageBase):
    traits: Optional[List[MessageBase]] = None


class OperationTrait(BaseModel):
    operationId: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[Tag]] = None
    externalDocs: Optional[ExternalDocumentation] = None
    bindings: Optional[Dict[str, dict]] = None


class OperationBase(BaseModel):
    operationId: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    externalDocs: Optional[ExternalDocumentation] = None
    bindings: Optional[Dict[str, dict]] = None


class Operation(OperationBase):
    traits: Optional[OperationBase] = None
    message: Optional[Message] = None


class ChannelItem(BaseModel):
    ref: Optional[str] = Field(None, alias="$ref")
    description: Optional[str] = None
    subscribe: Optional[Operation] = None
    publish: Optional[Operation] = None
    parameters: Optional[Dict[str, Union[Parameter, Reference]]] = None
    bindings: Optional[Dict[str, dict]] = None


class AsyncAPI(BaseModel):
    asyncapi: str
    id: Optional[str]
    info: Info
    servers: Optional[List[Server]] = None
    channels: Dict[str, ChannelItem]
    components: Optional[Components] = None
    tags: Optional[List[Tag]] = None
    externalDocs: Optional[ExternalDocumentation] = None
