class NotFoundError(Exception):
    pass


class InvalidInputError(Exception):
    pass


class UnauthorizedError(Exception):
    pass


class ConflictError(Exception):
    pass


class InternalError(Exception):
    pass


class RoomUnavailableError(Exception):
    pass


class TimeRangeInvalidError(Exception):
    pass
