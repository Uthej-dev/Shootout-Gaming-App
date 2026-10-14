from bson import ObjectId
from bson.errors import InvalidId


class AppError(Exception):
    def __init__(self, status: int, code: str, message: str):
        self.status, self.code, self.message = status, code, message


def ok(data=None, message: str = "Success"):
    return {"success": True, "data": data if data is not None else {}, "message": message}


def parse_oid(value: str, what: str = "id") -> ObjectId:
    try:
        return ObjectId(value)
    except (InvalidId, TypeError):
        raise AppError(422, "INVALID_ID", f"Invalid {what}")
