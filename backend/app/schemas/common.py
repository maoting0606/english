from typing import Generic, TypeVar
from pydantic import BaseModel
T = TypeVar("T")
class ApiResponse(BaseModel, Generic[T]):
    code: int = 200
    msg: str = "success"
    data: T | None = None

def ok(data=None):
    return {"code": 200, "msg": "success", "data": data}
