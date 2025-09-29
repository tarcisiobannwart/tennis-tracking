"""
Custom exceptions and error handlers
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import structlog


logger = structlog.get_logger(__name__)


class TennisTrackingException(Exception):
    """Base exception for tennis tracking application"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class MatchNotFoundException(TennisTrackingException):
    """Exception raised when match is not found"""
    def __init__(self, match_id: str):
        super().__init__(
            message=f"Match with ID {match_id} not found",
            status_code=status.HTTP_404_NOT_FOUND
        )


class PlayerNotFoundException(TennisTrackingException):
    """Exception raised when player is not found"""
    def __init__(self, player_id: str):
        super().__init__(
            message=f"Player with ID {player_id} not found",
            status_code=status.HTTP_404_NOT_FOUND
        )


class VideoProcessingException(TennisTrackingException):
    """Exception raised during video processing"""
    def __init__(self, message: str):
        super().__init__(
            message=f"Video processing failed: {message}",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )


class InvalidVideoFormatException(TennisTrackingException):
    """Exception raised for invalid video format"""
    def __init__(self, format_received: str):
        super().__init__(
            message=f"Invalid video format: {format_received}. Supported formats: mp4, avi, mov, mkv",
            status_code=status.HTTP_400_BAD_REQUEST
        )


class FileTooLargeException(TennisTrackingException):
    """Exception raised when uploaded file is too large"""
    def __init__(self, file_size: int, max_size: int):
        super().__init__(
            message=f"File size {file_size} bytes exceeds maximum allowed size {max_size} bytes",
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
        )


async def tennis_tracking_exception_handler(
    request: Request,
    exc: TennisTrackingException
) -> JSONResponse:
    """Handle custom tennis tracking exceptions"""
    logger.error(
        "Tennis tracking exception occurred",
        path=request.url.path,
        method=request.method,
        error=exc.message,
        status_code=exc.status_code
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.message,
            "type": exc.__class__.__name__
        }
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """Handle request validation errors"""
    logger.error(
        "Validation error occurred",
        path=request.url.path,
        method=request.method,
        errors=exc.errors()
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": True,
            "message": "Validation error",
            "details": exc.errors()
        }
    )


async def sqlalchemy_exception_handler(
    request: Request,
    exc: SQLAlchemyError
) -> JSONResponse:
    """Handle SQLAlchemy database errors"""
    logger.error(
        "Database error occurred",
        path=request.url.path,
        method=request.method,
        error=str(exc)
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "message": "Database error occurred",
            "type": "DatabaseError"
        }
    )


async def general_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """Handle general exceptions"""
    logger.error(
        "Unexpected error occurred",
        path=request.url.path,
        method=request.method,
        error=str(exc),
        exc_info=True
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "message": "Internal server error",
            "type": "InternalServerError"
        }
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """Setup all exception handlers for the FastAPI application"""
    app.add_exception_handler(TennisTrackingException, tennis_tracking_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)