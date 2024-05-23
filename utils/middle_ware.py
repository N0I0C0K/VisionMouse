from fastapi import Request
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from utils import logger


async def error_handling_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Unhandled error: {e}")
        # raise HTTPException(500, str(e))
        return JSONResponse({"error": str(e)}, 500)
