from enum import IntEnum

class FieldErrorCode(IntEnum):
    MISSING = 100
    WRONG_TYPE = 101
    INVALID_PATTERN = 102
    TOO_SHORT = 103
    TOO_LONG = 104
    NOT_IN_RANGE = 105
