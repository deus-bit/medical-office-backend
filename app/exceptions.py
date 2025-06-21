class BaseException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class EntityNotFound(BaseException):
    def __init__(self, message: str = "Entity not found.") -> None:
        super().__init__(message)


class ConnectionTimeout(BaseException):
    def __init__(self, message: str = "Connection timeout.") -> None:
        super().__init__(message)


class EntityAlreadyExists(BaseException):
    def __init__(self, message: str = "Entity already exists.") -> None:
        super().__init__(message)
