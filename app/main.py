import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from app.config import get_settings
from app.core.database import connect_db, disconnect_db
from app.middleware.auth_middleware import AuthMiddleware
from app.middleware.logging_middleware import LoggingMiddleware
from app.models.response_model import ApiResponse
from app.routers import auth_router, health_router, internal_router, users_router, vehicle_router

settings = get_settings()

# ── Logging setup ──
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await disconnect_db()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "TrueDNA Authentication API — login, logout, token refresh, audit logs.\n\n"
        "**How to authenticate in Swagger:**\n"
        "1. Call `POST /api/auth/login` → copy the `access_token`.\n"
        "2. Click the **Authorize 🔒** button (top right).\n"
        "3. Paste the token in the **BearerAuth (http, Bearer)** field → Authorize."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    swagger_ui_parameters={"persistAuthorization": True},
)


# ── Inject BearerAuth security scheme into OpenAPI schema ──────────────────
# FastAPI auto-registers "HTTPBearer" from router-level Depends(HTTPBearer()).
# We rename it to "BearerAuth" with a clear description so Swagger shows a
# labelled input field in the Authorize dialog.
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Replace whatever name FastAPI chose with the canonical "BearerAuth" name
    components = schema.setdefault("components", {})
    components["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": (
                "Enter the access_token from POST /api/auth/login.\n"
                "Do **not** prefix with 'Bearer ' — Swagger adds it automatically."
            ),
        }
    }

    # Rewrite every operation's security array to reference "BearerAuth"
    for path_item in schema.get("paths", {}).values():
        for operation in path_item.values():
            if not isinstance(operation, dict):
                continue
            # If the auto-generated schema put "HTTPBearer" here, replace it
            raw = operation.get("security")
            if raw:
                operation["security"] = [{"BearerAuth": []}]
            # Operations that had no security yet (public routes) stay open

    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi  # type: ignore[method-assign]

# ── Middleware (outermost added last wraps innermost) ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LoggingMiddleware)
app.add_middleware(AuthMiddleware)

# ── Routers ──
app.include_router(health_router.router)
app.include_router(auth_router.router)
app.include_router(internal_router.router)
app.include_router(users_router.router)    # /api/v1/users/* — JWT protected
app.include_router(vehicle_router.router)  # /api/v1/vehicles/* — JWT protected


# ── Global exception handlers ─────────────────────────────────────────────────
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ApiResponse.error(
            message=exc.detail if isinstance(exc.detail, str) else str(exc.detail),
            status_code=exc.status_code,
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logging.getLogger(__name__).exception("Unhandled error: %s", exc)
    return JSONResponse(
        status_code=500,
        content=ApiResponse.error(
            message="An unexpected server error occurred.",
            status_code=500,
        ).model_dump(),
    )