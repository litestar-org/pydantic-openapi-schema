from typing import TYPE_CHECKING, Any, Set, Type, TypeVar, Union, cast

from pydantic import BaseModel, create_model
from pydantic.generics import GenericModel
from pydantic.schema import schema

from pydantic_openapi_schema import v3_1_0

if TYPE_CHECKING:
    from typing import Dict

REF_PREFIX = "#/components/schemas/"
SCHEMA_NAME_ATTRIBUTE = "__schema_name__"

T = TypeVar("T", bound=v3_1_0.OpenAPI)


class OpenAPI310PydanticSchema(v3_1_0.Schema):
    """Special `Schema` class to indicate a reference from pydantic class."""

    schema_class: Union[Type[BaseModel], Type[GenericModel]]
    """the class that is used for generate the schema"""


def construct_open_api_with_schema_class(
    open_api_schema: T,
) -> T:
    """Construct a new OpenAPI object, with the use of pydantic classes to produce JSON schemas.

    Args:
        open_api_schema: An instance of the OpenAPI model.

    Returns:
        new OpenAPI object with "#/components/schemas" values updated. If there is no update in
            "#/components/schemas" values, the original `open_api` will be returned.
    """
    copied_schema = open_api_schema.copy(deep=True)
    schema_classes = list(extract_pydantic_types_to_openapi_components(obj=copied_schema, ref_class=v3_1_0.Reference))

    if not schema_classes:
        return open_api_schema

    if not copied_schema.components:
        copied_schema.components = v3_1_0.Components(schemas={})
    if copied_schema.components.schemas is None:  # pragma: no cover
        copied_schema.components.schemas = cast("Dict[str, Any]", {})

    schema_classes = [
        cls if not hasattr(cls, "__schema_name__") else create_model(getattr(cls, SCHEMA_NAME_ATTRIBUTE), __base__=cls)
        for cls in schema_classes
    ]
    schema_classes.sort(key=lambda x: x.__name__)
    schema_definitions = schema(schema_classes, ref_prefix=REF_PREFIX)["definitions"]
    copied_schema.components.schemas.update(
        {key: v3_1_0.Schema.parse_obj(schema_dict) for key, schema_dict in schema_definitions.items()}
    )
    return copied_schema


def extract_pydantic_types_to_openapi_components(
    obj: Any, ref_class: Type[v3_1_0.Reference]
) -> Set[Union[Type[BaseModel], Type[GenericModel]]]:
    """Recursively traverses the OpenAPI document, replacing any found Pydantic Models with $references to the schema's
    components section and returning the pydantic models themselves.

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


def create_ref_prefix(model: Union[Type[BaseModel], Type[GenericModel]]) -> str:
    """Create a ref prefix for the given model.

    Args:
        model: Pydantic model instance.

    Returns:
        A prefixed name.
    """
    return REF_PREFIX + getattr(model, SCHEMA_NAME_ATTRIBUTE, model.__name__)
