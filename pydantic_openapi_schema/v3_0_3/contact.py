from typing import Optional, Union

from pydantic import AnyUrl, BaseModel, EmailStr, Extra, validator


class Contact(BaseModel):
    """
    Contact information for the exposed API.
    """

    name: Optional[str] = None
    """
    The identifying name of the contact person/organization.
    """

    url: Optional[AnyUrl] = None
    """
    The URL pointing to the contact information. MUST be in the format of a URL.
    """

    email: Optional[Union[EmailStr, str]] = None
    """
    The email address of the contact person/organization. MUST be in the format of an email address.
    """

    @validator("email", pre=True)
    def validate_email(  # pylint: disable=no-self-argument
        cls,
        v: Union[EmailStr, str],
    ) -> EmailStr:
        """Validates that email is a valid email address

        Args:
            v (EmailStr|str): Holds the email string to be validated

        Raises:
            ValueError: Value is not a valid email address

        Returns:
            _type_: CompressionBackend
        """
        if isinstance(v, str):
            v = EmailStr(v)
        return v

    class Config:
        extra = Extra.ignore
        schema_extra = {
            "examples": [
                {"name": "API Support", "url": "http://www.example.com/support", "email": "support@example.com"}
            ]
        }
