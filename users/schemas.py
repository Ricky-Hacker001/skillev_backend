from pydantic import BaseModel, EmailStr

# 1. Register
class UserCreate(BaseModel):
    email: EmailStr
    password: str

# 2. Login
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# 3. Verify OTP
class UserVerify(BaseModel):
    email: EmailStr
    otp: str

# 4. Forgot Password (Request OTP)
class ForgotPassword(BaseModel):
    email: EmailStr

# 5. Reset Password (Use OTP + New Pass)
class ResetPassword(BaseModel):
    email: EmailStr
    otp: str
    new_password: str

# 6. Response Token
class Token(BaseModel):
    access_token: str
    token_type: str