from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.config import connect_to_mongo, close_mongo_connection
from app.routes.employees import router as employee_router
from app.routes.attendance import router as attendance_router

app = FastAPI(
    title="HRMS Lite",
    description="A lightweight Human Resource Management System API",
    version="1.0.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Startup & Shutdown events
@app.on_event("startup")
async def startup():
    await connect_to_mongo()


@app.on_event("shutdown")
async def shutdown():
    await close_mongo_connection()


# Global exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"] if loc != "body")
        errors.append({"field": field, "message": error["msg"]})
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error", "errors": errors},
    )


# Generic exception handler
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred"},
    )


# Register routers
app.include_router(employee_router)
app.include_router(attendance_router)


# Health check
@app.get("/", tags=["Health"])
async def root():
    return {"status": "healthy", "message": "HRMS Lite API is running"}


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}
