from fastapi import HTTPException, status
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse

class AppExceptionHandler(Exception):
    def __init__(self, status_code: int, context: dict):
        self.exception_case = self.__class__.__name__
        self.status_code = status_code
        self.context = context

    def __str__(self):
        return (
            f"<AppException {self.exception_case} - "
            f"status_code={self.status_code} - context={self.context}"
        )
    
async def app_exception_handler(request: Request, exc: AppExceptionHandler):
    return JSONResponse(status_code=exc.status_code, content={
        "error": exc.exception_case,
        "context": exc.context
    })

class AppException:
    class UserNotFound(AppExceptionHandler):
        def __init__(self, user_id: str):
            status_code = status.HTTP_404_NOT_FOUND
            context = {"user_id": user_id, "message": "User not found"}
            super().__init__(status_code, context)

    class Unauthorized(AppExceptionHandler):
        def __init__(self):
            status_code = status.HTTP_401_UNAUTHORIZED
            context = {"message": "Invalid credentials"}
            super().__init__(status_code, context)

    # Add another (Postpone for now)


async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    reformated_errors = []
    for error in exc.errors():
        reformated_errors.append(
            {
                "field": error['loc'][-1],
                "message": error['msg'],
                "type": error['type']
            }
        )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": reformated_errors}
    )


async def python_validation_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"errors": exc.errors()}
    )

def add_exception_handlers(app):
    app.add_exception_handler(AppExceptionHandler,app_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValidationError, python_validation_handler)