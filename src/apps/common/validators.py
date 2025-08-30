from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class FileValidator(FileExtensionValidator):
    """
    Validator for both file extension and file size.

    This validator extends Django's built-in `FileExtensionValidator` to add
    a file size validation check. It is designed to be used on `FileField`
    or `ImageField` in Django models or forms.
    """

    message_max_size = _("File size should not exceed %(max_size)s MB.")
    code_max_size = "invalid_size"

    def __init__(self, allowed_extensions=None, max_size=None, message=None, code=None):
        """
        Initializes the validator with allowed extensions and maximum file size.

        Args:
            allowed_extensions (list, optional): A list of valid file extensions.
                Defaults to None.
            max_size (int, optional): The maximum allowed file size in bytes.
                For example, `5 * 1024 * 1024` for 5 MB. Defaults to None.
            message (str, optional): The custom error message for an invalid
                extension. Defaults to Django's default.
            code (str, optional): The custom error code for an invalid extension.
                Defaults to Django's default.
        """
        super().__init__(allowed_extensions=allowed_extensions, message=message, code=code)
        self.max_size = max_size

    def __call__(self, value):
        """
        Validates the file extension and size.

        This method first calls the parent's `__call__` method to validate
        the file extension. If the extension is valid, it then checks the
        file's size against the `max_size`.

        Args:
            value (File): The file object to validate.

        Raises:
            ValidationError: If the file extension is invalid or if the file
                size exceeds `max_size`. The error message and code vary
                depending on the type of validation failure.
        """
        # Validate the file extension using the parent's logic
        super().__call__(value)

        # Check the file size if max_size is defined
        if self.max_size is not None and value.size > self.max_size:
            raise ValidationError(
                self.message_max_size,
                code=self.code_max_size,
                params={
                    "max_size": round(self.max_size / (1024 * 1024), 2),
                    "value": value,
                },
            )