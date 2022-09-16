from typing import TYPE_CHECKING, Any, List, Optional, Set, Type, TypeVar, cast

from pydantic import BaseModel, create_model
from pydantic.schema import schema

from pydantic_openapi_schema import v3_1_0

if TYPE_CHECKING:
    from typing import Dict

REF_PREFIX = "#/components/schemas/"
SCHEMA_NAME_ATTRIBUTE = "__schema_name__"

T = TypeVar("T", bound=v3_1_0.OpenAPI)


class OpenAPI310PydanticSchema(v3_1_0.Schema):
    """Special `Schema` class to indicate a reference from pydantic class."""

    schema_class: Type[BaseModel]
    """the class that is used for generate the schema"""


def construct_open_api_with_schema_class(
    open_api_schema: T,
    schema_classes: Optional[List[Type[BaseModel]]] = None,
    scan_for_pydantic_schema_reference: bool = True,
    by_alias: bool = True,
) -> T:
    """Construct a new OpenAPI object, with the use of pydantic classes to
    produce JSON schemas.

    Args:
        open_api_schema: the base `OpenAPI` object
        schema_classes: pydantic classes that their schema will be used as "#/components/schemas" values
        scan_for_pydantic_schema_reference: flag to indicate if scanning for `PydanticSchemaReference`
            class is needed for "#/components/schemas" value updates
        by_alias: construct schema by alias (default is True)

    Returns:
        new OpenAPI object with "#/components/schemas" values updated. If there is no update in
            "#/components/schemas" values, the original `open_api` will be returned.
    """
    copied_schema = open_api_schema.copy(deep=True)

    if scan_for_pydantic_schema_reference:
        extracted_schema_classes = extract_pydantic_types_to_openapi_components(
            obj=copied_schema, ref_class=v3_1_0.Reference
        )
        schema_classes = list(
            {*schema_classes, *extracted_schema_classes} if schema_classes else extracted_schema_classes
        )

    if not schema_classes:
        return open_api_schema

    if not copied_schema.components:
        copied_schema.components = v3_1_0.Components(schemas={})
    elif not copied_schema.components.schemas:
        copied_schema.components.schemas = cast("Dict[str, Any]", {})

    schema_classes = [
        cls if not hasattr(cls, "__schema_name__") else create_model(getattr(cls, SCHEMA_NAME_ATTRIBUTE), __base__=cls)
        for cls in schema_classes
    ]
    schema_classes.sort(key=lambda x: x.__name__)
    schema_definitions = schema(schema_classes, by_alias=by_alias, ref_prefix=REF_PREFIX)["definitions"]
    copied_schema.components.schemas.update(  # type: ignore
        {key: v3_1_0.Schema.parse_obj(schema_dict) for key, schema_dict in schema_definitions.items()}
    )
    return copied_schema


def extract_pydantic_types_to_openapi_components(obj: Any, ref_class: Type[v3_1_0.Reference]) -> Set[Type[BaseModel]]:
    """Recursively traverses the OpenAPI document, replacing any found Pydantic
    Models with $references to the schema's components section and returning
    the pydantic models themselves.

    Args:
        obj:
        ref_class:

    Returns:
        set of pydantic schema classes
    """
    pydantic_schemas: Set[Type[BaseModel]] = set()
    if isinstance(obj, BaseModel):
        fields = obj.__fields_set__
        for field in fields:
            child_obj = getattr(obj, field)
            if isinstance(child_obj, OpenAPI310PydanticSchema):
                setattr(obj, field, ref_class(ref=create_ref_prefix(child_obj.schema_class)))
                pydantic_schemas.add(child_obj.schema_class)
            else:
                pydantic_schemas.update(extract_pydantic_types_to_openapi_components(child_obj, ref_class=ref_class))
    elif isinstance(obj, list):
        for index, elem in enumerate(obj):
            if isinstance(elem, OpenAPI310PydanticSchema):
                obj[index] = ref_class(ref=create_ref_prefix(elem.schema_class))
                pydantic_schemas.add(elem.schema_class)
            else:
                pydantic_schemas.update(extract_pydantic_types_to_openapi_components(elem, ref_class=ref_class))
    elif isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, OpenAPI310PydanticSchema):
                obj[key] = ref_class(ref=create_ref_prefix(value.schema_class))
                pydantic_schemas.add(value.schema_class)
            else:
                pydantic_schemas.update(extract_pydantic_types_to_openapi_components(value, ref_class=ref_class))
    return pydantic_schemas


def create_ref_prefix(model: Type[BaseModel]) -> str:
    """

    Args:
        model: Pydantic model instance.

    Returns:
        A prefixed name.
    """
    return REF_PREFIX + getattr(model, SCHEMA_NAME_ATTRIBUTE, model.__name__)
