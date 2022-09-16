from pydantic_openapi_schema.v3_1_0 import Reference, Schema


def test_schema_parse_obj() -> None:
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
