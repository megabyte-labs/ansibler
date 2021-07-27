class BaseAnsiblerException(Exception):
    message = "Error"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args)
        self.message = kwargs.get("message", self.message)

    def __str__(self) -> str:
        return self.message


class CommandNotFound(BaseAnsiblerException):
    message = "Command not found"


class RolesParseError(BaseAnsiblerException):
    message = "Could not parse default roles"


class MetaYMLError(BaseAnsiblerException):
    message = "Invalid meta/main.yml"


class RoleMetadataError(BaseAnsiblerException):
    message = "Role metadata error"


class MoleculeTestsNotFound(BaseAnsiblerException):
    message = "Molecule tests not foound"


class MoleculeTestParseError(BaseAnsiblerException):
    message = "Could not parse molecule test file"
