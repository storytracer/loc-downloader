class LocAPIError(Exception):
    pass


class RateLimitError(LocAPIError):
    pass