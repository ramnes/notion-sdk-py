from enum import Enum


class APIResponseError(Exception):
    pass


class APIErrorCode(Enum):
    Unauthorized = "unauthorized"
    RestrictedResource = "restricted_resource"
    ObjectNotFound = "object_not_found"
    RateLimited = "rate_limited"
    InvalidJSON = "invalid_json"
    InvalidRequestURL = "invalid_request_url"
    InvalidRequest = "invalid_request"
    ValidationError = "validation_error"
    ConflictError = "conflict_error"
    InternalServerError = "internal_server_error"
    ServiceUnavailable = "service_unavailable"
