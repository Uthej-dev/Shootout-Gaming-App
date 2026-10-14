from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.errors import AppError
from app.db.database import client, init_indexes
from app.routes import auth, matches, rooms, users, wallet


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_indexes()
    yield
    await client.close()


app = FastAPI(title="ShootOut API", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def _err(status, code, message, details=None):
    body = {"success": False, "code": code, "message": message}
    if details:
        body["details"] = details
    return JSONResponse(status_code=status, content=body)


@app.exception_handler(AppError)
async def app_error(_: Request, e: AppError):
    return _err(e.status, e.code, e.message)


@app.exception_handler(RequestValidationError)
async def validation_error(_: Request, e: RequestValidationError):
    details = [{"field": ".".join(str(p) for p in x["loc"][1:]), "message": x["msg"]} for x in e.errors()]
    return _err(422, "VALIDATION_ERROR", "Invalid request data", details)


@app.exception_handler(Exception)
async def unhandled(_: Request, e: Exception):
    return _err(500, "INTERNAL_ERROR", "Something went wrong")


for r in (auth.router, users.router, wallet.router, matches.router, rooms.router):
    app.include_router(r)


@app.get("/health", tags=["meta"])
async def health():
    return {"success": True, "data": {"status": "ok"}, "message": "Success"}
