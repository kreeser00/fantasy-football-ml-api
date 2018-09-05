from enum import Enum


class ResponseStatusCodes(Enum):
    OK = "200"
    ERROR = "400"
    INTERNAL_SERVER_ERROR = "500"
