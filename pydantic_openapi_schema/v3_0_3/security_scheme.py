from typing import Optional, Union

from pydantic import AnyUrl, BaseModel, Extra, Field
from typing_extensions import Literal

from .oauth_flows import OAuthFlows


class SecurityScheme(BaseModel):
    """Defines a security scheme that can be used by the operations.

    Supported schemes are HTTP authentication,
    an API key (either as a header, a cookie parameter or as a query parameter),
    OAuth2's common flows (implicit, password, client credentials and authorization code)
    as defined in [RFC6749](https://tools.ietf.org/html/rfc6749),
    and [OpenID Connect Discovery](https://tools.ietf.org/html/draft-ietf-oauth-discovery-06).
    """

    type: Literal["apiKey", "http", "oauth2", "openIdConnect"]
    """
    **REQUIRED**. The type of the security scheme.
    """

    description: Optional[str] = None
    """
    A short description for security scheme.
    [CommonMark syntax](https://spec.commonmark.org/) MAY be used for rich text representation.
    """

    name: Optional[str] = None
    """
    **REQUIRED** for `apiKey`. The name of the header, query or cookie parameter to be used.
    """

    security_scheme_in: Optional[Literal["query", "header", "cookie"]] = Field(alias="in", default=None)
    """
    **REQUIRED** for `apiKey`. The location of the API key.
    """

    scheme: Optional[str] = None
    """
    **REQUIRED** for `http`. The name of the HTTP Authorization scheme to be used in the
    [Authorization header as defined in RFC7235](https://tools.ietf.org/html/rfc7235#section-5.1).

    The values used SHOULD be registered in the
    [IANA Authentication Scheme registry](https://www.iana.org/assignments/http-authschemes/http-authschemes.xhtml).
    """

    bearerFormat: Optional[str] = None
    """
    A hint to the client to identify how the bearer token is formatted.

    Bearer tokens are usually generated by an authorization server,
    so this information is primarily for documentation purposes.
    """

    flows: Optional[OAuthFlows] = None
    """
    **REQUIRED** for `oauth2`. An object containing configuration information for the flow types supported.
    """

    openIdConnectUrl: Optional[Union[AnyUrl, str]] = None
    """
    **REQUIRED** for `openIdConnect`. OpenId Connect URL to discover OAuth2 configuration values.
    This MUST be in the form of a URL.
    """

    class Config:
        extra = Extra.ignore
        allow_population_by_field_name = True
        schema_extra = {
            "examples": [
                {"type": "http", "scheme": "basic"},
                {"type": "apiKey", "name": "api_key", "in": "header"},
                {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"},
                {
                    "type": "oauth2",
                    "flows": {
                        "implicit": {
                            "authorizationUrl": "https://example.com/api/oauth/dialog",
                            "scopes": {"write:pets": "modify pets in your account", "read:pets": "read your pets"},
                        }
                    },
                },
                {"type": "openIdConnect", "openIdConnectUrl": "https://example.com/openIdConnect"},
                {"type": "openIdConnect", "openIdConnectUrl": "openIdConnect"},  # #5: allow relative path
            ]
        }
