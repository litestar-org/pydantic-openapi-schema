from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from pydantic_openapi_schema.v3_0_3.path_item import PathItem

Callback = Dict[str, "PathItem"]
"""
A map of possible out-of band callbacks related to the parent operation.
Each value in the map is a `Path Item Object <https://spec.openapis.org/oas/v3.0.3#pathItemObject>`__
that describes a set of requests that may be initiated by the API provider and the expected responses.
The key value used to identify the path item object is an expression, evaluated at runtime,
that identifies a URL to use for the callback operation.

Patterned Fields:

{expression}: 'PathItem' = ...

A Path Item Object used to define a callback request and expected responses.

A `complete example <https://github.com/OAI/OpenAPI-Specification/blob/main/examples/v3.0/callback-example.yaml>`__
is available.
"""
