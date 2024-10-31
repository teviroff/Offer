from enum import IntEnum

class GenericError[T: IntEnum]:
    error_code: T
    error_message: str

    def __init__(self, error_code: T, error_message: str) -> None:
        self.error_code = error_code
        self.error_message = error_message
