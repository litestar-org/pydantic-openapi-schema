from pydantic import BaseModel, Extra
from pydantic.schema import schema

from pydantic_openapi_schema.v3_1_0 import Reference, Schema


def test_schema() -> None:
    parsed_schema = Schema.parse_obj(
        {
            "title": "reference list",
            "description": "schema for list of reference type",
            "allOf": [{"$ref": "#/definitions/TestType"}],
        }
    )
    assert parsed_schema.allOf
    assert isinstance(parsed_schema.allOf, list)
    assert isinstance(parsed_schema.allOf[0], Reference)
    assert parsed_schema.allOf[0].ref == "#/definitions/TestType"


def test_issue_4() -> None:
    """https://github.com/kuimono/openapi-schema-pydantic/issues/4."""

    class TestModel(BaseModel):
        test_field: str

        class Config:
            extra = Extra.forbid

    schema_definition = schema([TestModel])
    assert schema_definition == {
        "definitions": {
            "TestModel": {
                "title": "TestModel",
                "type": "object",
                "properties": {"test_field": {"title": "Test Field", "type": "string"}},
                "required": ["test_field"],
                "additionalProperties": False,
            }
        }
    }

    # allow "additionalProperties" to have boolean value
    result = Schema.parse_obj(schema_definition["definitions"]["TestModel"])
    assert result.additionalProperties is False
