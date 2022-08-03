from pydantic import Extra, Field
from typing_extensions import Literal

from .parameter import Parameter


class Header(Parameter):
    """
    The Header Object follows the structure of the `Parameter Object <https://spec.openapis.org/oas/v3.1.0#parameterObject>`__ with the following changes:

    1. `name` MUST NOT be specified, it is given in the corresponding `headers` map.
    2. `in` MUST NOT be specified, it is implicitly in `header`.
    3. All traits that are affected by the location MUST be applicable to a location of `header`
       (for example, `style <https://spec.openapis.org/oas/v3.1.0#parameterStyle>`__).
    """

    name: Literal[""] = Field(default="", const=True)
    param_in: Literal["header"] = Field(default="header", const=True, alias="in")

    class Config:
        extra = Extra.ignore
        allow_population_by_field_name = True
        schema_extra = {
            "examples": [
                {"description": "The number of allowed requests in the current period", "schema": {"type": "integer"}}
            ]
        }
