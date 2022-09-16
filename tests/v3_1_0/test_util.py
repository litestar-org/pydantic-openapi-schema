from pydantic import BaseModel, Field

from pydantic_openapi_schema.utils.utils import (
    OpenAPI310PydanticSchema,
    construct_open_api_with_schema_class,
)
from pydantic_openapi_schema.v3_1_0 import (
    Info,
    MediaType,
    OpenAPI,
    Operation,
    PathItem,
    Reference,
    RequestBody,
    Response,
)
from tests.v3_1_0.utils import PingRequest as OtherPingRequest
from tests.v3_1_0.utils import PingResponse as OtherPingResponse


class PingRequest(BaseModel):
    """Ping Request."""

    req_foo: str = Field(description="foo value of the request")
    req_bar: str = Field(description="bar value of the request")


class PingResponse(BaseModel):
    """Ping response."""

    resp_foo: str = Field(description="foo value of the response")
    resp_bar: str = Field(description="bar value of the response")


class PongResponse(BaseModel):
    """Pong response."""

    resp_foo: str = Field(alias="pong_foo", description="foo value of the response")
    resp_bar: str = Field(alias="pong_bar", description="bar value of the response")


def test_construct_open_api_with_schema_class_1() -> None:
    open_api = OpenAPI.parse_obj(
        {
            "info": {"title": "My own API", "version": "v0.0.1"},
            "paths": {
                "/ping": {
                    "post": {
                        "requestBody": {
                            "content": {
                                "application/json": {"schema": OpenAPI310PydanticSchema(schema_class=PingRequest)}
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "pong",
                                "content": {
                                    "application/json": {"schema": OpenAPI310PydanticSchema(schema_class=PingResponse)}
                                },
                            }
                        },
                    }
                }
            },
        }
    )
    result_open_api_1 = construct_open_api_with_schema_class(open_api)
    result_open_api_2 = construct_open_api_with_schema_class(open_api, [PingRequest, PingResponse])
    assert result_open_api_1.components == result_open_api_2.components
    assert result_open_api_1 == result_open_api_2


def test_construct_open_api_with_schema_class_2() -> None:
    open_api_1 = OpenAPI.parse_obj(
        {
            "info": {"title": "My own API", "version": "v0.0.1"},
            "paths": {
                "/ping": {
                    "post": {
                        "requestBody": {
                            "content": {
                                "application/json": {"schema": OpenAPI310PydanticSchema(schema_class=PingRequest)}
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "pong",
                                "content": {
                                    "application/json": {"schema": OpenAPI310PydanticSchema(schema_class=PingResponse)}
                                },
                            }
                        },
                    }
                }
            },
        }
    )
    open_api_2 = OpenAPI(
        info=Info(
            title="My own API",
            version="v0.0.1",
        ),
        paths={
            "/ping": PathItem(
                post=Operation(
                    requestBody=RequestBody(
                        content={
                            "application/json": MediaType(
                                media_type_schema=Reference(ref="#/components/schemas/PingRequest")
                            )
                        }
                    ),
                    responses={
                        "200": Response(
                            description="pong",
                            content={
                                "application/json": MediaType(
                                    media_type_schema=Reference(ref="#/components/schemas/PingResponse")
                                )
                            },
                        )
                    },
                )
            )
        },
    )
    result_open_api_1 = construct_open_api_with_schema_class(open_api_1)
    result_open_api_2 = construct_open_api_with_schema_class(open_api_2, [PingRequest, PingResponse])
    assert result_open_api_1 == result_open_api_2


def test_construct_open_api_with_schema_class_3() -> None:
    open_api_3 = OpenAPI(
        info=Info(
            title="My own API",
            version="v0.0.1",
        ),
        paths={
            "/ping": PathItem(
                post=Operation(
                    requestBody=RequestBody(
                        content={
                            "application/json": MediaType(
                                media_type_schema=OpenAPI310PydanticSchema(schema_class=PingRequest)
                            )
                        }
                    ),
                    responses={
                        "200": Response(
                            description="pong",
                            content={
                                "application/json": MediaType(
                                    media_type_schema=OpenAPI310PydanticSchema(schema_class=PongResponse)
                                )
                            },
                        )
                    },
                )
            )
        },
    )

    result_with_alias_1 = construct_open_api_with_schema_class(open_api_3)
    schema_with_alias = result_with_alias_1.components.schemas["PongResponse"]  # type: ignore
    assert "pong_foo" in schema_with_alias.properties  # type: ignore
    assert "pong_bar" in schema_with_alias.properties  # type: ignore

    result_with_alias_2 = construct_open_api_with_schema_class(open_api_3)
    assert result_with_alias_1 == result_with_alias_2

    result_without_alias = construct_open_api_with_schema_class(open_api_3, by_alias=False)
    schema_without_alias = result_without_alias.components.schemas["PongResponse"]  # type: ignore
    assert "resp_foo" in schema_without_alias.properties  # type: ignore
    assert "resp_bar" in schema_without_alias.properties  # type: ignore


def test_handling_of_models_with_same_name() -> None:
    open_api = OpenAPI(
        info=Info(
            title="My own API",
            version="v0.0.1",
        ),
        paths={
            "/ping1": PathItem(
                post=Operation(
                    requestBody=RequestBody(
                        content={
                            "application/json": MediaType(
                                media_type_schema=OpenAPI310PydanticSchema(schema_class=PingRequest)
                            )
                        }
                    ),
                    responses={
                        "200": Response(
                            description="pong",
                            content={
                                "application/json": MediaType(
                                    media_type_schema=OpenAPI310PydanticSchema(schema_class=PingResponse)
                                )
                            },
                        )
                    },
                )
            ),
            "/ping2": PathItem(
                post=Operation(
                    requestBody=RequestBody(
                        content={
                            "application/json": MediaType(
                                media_type_schema=OpenAPI310PydanticSchema(schema_class=OtherPingRequest)
                            )
                        }
                    ),
                    responses={
                        "200": Response(
                            description="pong",
                            content={
                                "application/json": MediaType(
                                    media_type_schema=OpenAPI310PydanticSchema(schema_class=OtherPingResponse)
                                )
                            },
                        )
                    },
                )
            ),
        },
    )
    result = construct_open_api_with_schema_class(open_api)
    assert result.dict(exclude_none=True) == {
        "openapi": "3.1.0",
        "info": {"title": "My own API", "version": "v0.0.1"},
        "servers": [{"url": "/"}],
        "paths": {
            "/ping1": {
                "post": {
                    "requestBody": {
                        "content": {
                            "application/json": {"media_type_schema": {"ref": "#/components/schemas/PingRequest"}}
                        },
                        "required": False,
                    },
                    "responses": {
                        "200": {
                            "description": "pong",
                            "content": {
                                "application/json": {"media_type_schema": {"ref": "#/components/schemas/PingResponse"}}
                            },
                        }
                    },
                    "deprecated": False,
                }
            },
            "/ping2": {
                "post": {
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "media_type_schema": {"ref": "#/components/schemas/RenamedPingRequest"}
                            }
                        },
                        "required": False,
                    },
                    "responses": {
                        "200": {
                            "description": "pong",
                            "content": {
                                "application/json": {
                                    "media_type_schema": {"ref": "#/components/schemas/RenamedPingResponse"}
                                }
                            },
                        }
                    },
                    "deprecated": False,
                }
            },
        },
        "components": {
            "schemas": {
                "PingRequest": {
                    "properties": {
                        "req_foo": {"type": "string", "title": "Req Foo", "description": "foo value of the request"},
                        "req_bar": {"type": "string", "title": "Req Bar", "description": "bar value of the request"},
                    },
                    "type": "object",
                    "required": ["req_foo", "req_bar"],
                    "title": "PingRequest",
                    "description": "Ping Request.",
                },
                "PingResponse": {
                    "properties": {
                        "resp_foo": {"type": "string", "title": "Resp Foo", "description": "foo value of the response"},
                        "resp_bar": {"type": "string", "title": "Resp Bar", "description": "bar value of the response"},
                    },
                    "type": "object",
                    "required": ["resp_foo", "resp_bar"],
                    "title": "PingResponse",
                    "description": "Ping response.",
                },
                "RenamedPingRequest": {
                    "properties": {
                        "req_foo": {"type": "string", "title": "Req Foo", "description": "foo value of the request"},
                        "req_bar": {"type": "string", "title": "Req Bar", "description": "bar value of the request"},
                    },
                    "type": "object",
                    "required": ["req_foo", "req_bar"],
                    "title": "RenamedPingRequest",
                    "description": "Ping Request.",
                },
                "RenamedPingResponse": {
                    "properties": {
                        "resp_foo": {"type": "string", "title": "Resp Foo", "description": "foo value of the response"},
                        "resp_bar": {"type": "string", "title": "Resp Bar", "description": "bar value of the response"},
                    },
                    "type": "object",
                    "required": ["resp_foo", "resp_bar"],
                    "title": "RenamedPingResponse",
                    "description": "Ping response.",
                },
            }
        },
    }
