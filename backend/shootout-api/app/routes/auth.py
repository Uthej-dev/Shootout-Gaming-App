from fastapi import APIRouter
from app.core.errors import AppError, ok
from app.schemas.auth import ForgotPasswordRequest, LoginRequest, RegisterRequest
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=201)
async def register(req: RegisterRequest):
    return ok(await auth_service.register_user(req), "Registration successful")


@router.post("/login")
async def login(req: LoginRequest):
    return ok(await auth_service.login_user(req), "Login successful")


@router.post("/forgot-password")
async def forgot_password(req: ForgotPasswordRequest):
    # Future: look up user, send OTP via SMS provider. Same reply either way (no user enumeration).
    return ok({}, "If the account exists, an OTP will be sent")


@router.post("/verify-otp")
async def verify_otp():
    raise AppError(501, "NOT_IMPLEMENTED", "OTP verification is not implemented yet")


@router.post("/reset-password")
async def reset_password():
    raise AppError(501, "NOT_IMPLEMENTED", "Password reset is not implemented yet")
