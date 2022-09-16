from pydantic import BaseModel, Field


class PingRequest(BaseModel):
    """Ping Request."""

    __schema_name__ = "RenamedPingRequest"

    req_foo: str = Field(description="foo value of the request")
    req_bar: str = Field(description="bar value of the request")


class PingResponse(BaseModel):
    """Ping response."""

    __schema_name__ = "RenamedPingResponse"

    resp_foo: str = Field(description="foo value of the response")
    resp_bar: str = Field(description="bar value of the response")
