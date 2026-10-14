from pydantic import BaseModel, Field, model_validator


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=20, pattern=r"^[A-Za-z0-9_]+$")
    mobileNumber: str = Field(pattern=r"^[6-9]\d{9}$")
    password: str = Field(min_length=8, max_length=64)
    confirmPassword: str

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.confirmPassword:
            raise ValueError("Passwords do not match")
        return self


class LoginRequest(BaseModel):
    identifier: str = Field(min_length=3, description="Username or mobile number")
    password: str


class ForgotPasswordRequest(BaseModel):
    identifier: str
