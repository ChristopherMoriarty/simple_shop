from fastapi import HTTPException


async def basic_exception(
    status_code: int = 500,
    message: str = "Server error, try later",
    status: str = "error",
):
    raise HTTPException(
        status_code=status_code,
        detail={
            "status": status,
            "data": None,
            "detail": message,
        },
    )