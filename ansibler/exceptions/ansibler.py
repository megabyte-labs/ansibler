class BaseException(Exception):
    message = "Error"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args)
        self.message = kwargs.get("message", self.message)

    def __str__(self) -> str:
        return self.message


class CommandNotFound(BaseException):
    message = "Command not found"


class RolesParseError(BaseException):
    message = "Could not parse default roles"


class MetaYMLError(BaseException):
    message = "Invalid meta/main.yml"
