🚀 Skillev API Test Guide Use this documentation to test your endpoints in Postman or Requestly.  1. User Registration Description: Creates a new account. Check the terminal for the OTP.  Endpoint: POST /users/register  Request Body (JSON):  JSON {   "email": "user@example.com",   "password": "your_secure_password" } Success Response (200 OK):  JSON {   "message": "OTP sent to your email" } 2. Email Verification Description: Activates the user account using the OTP code.  Endpoint: POST /users/verify  Request Body (JSON):  JSON {   "email": "user@example.com",   "otp": "123456" } Success Response (200 OK):  JSON {   "message": "Account verified!" } 3. User Login Description: Exchanges credentials for a JWT access token.  Endpoint: POST /users/login  Request Body (JSON):  JSON {   "email": "user@example.com",   "password": "your_secure_password" } Success Response (200 OK):  JSON {   "access_token": "eyJhbGciOiJIUzI1NiIsInR5...",   "token_type": "bearer" } 4. Forgot Password Description: Requests a password reset OTP.  Endpoint: POST /users/forgot-password  Request Body (JSON):  JSON {   "email": "user@example.com" } 5. Reset Password Description: Sets a new password using the reset OTP.  Endpoint: POST /users/reset-password  Request Body (JSON):  JSON {   "email": "user@example.com",   "otp": "654321",   "new_password": "new_awesome_password" } 6. Secure Data (Token Required) Description: A protected endpoint to verify the JWT token works.  Endpoint: GET /secure-data  Header: Authorization: Bearer <your_access_token>  Success Response (200 OK):  JSON {   "message": "🎉 You cracked the code!",   "status": "Authorized" }  give me the full readme md formate for github only markdown formate


run cmds
 python3 -m uvicorn main:app --reload   

 docker build -t skillev-labs-auth:latest .

 docker build --no-cache -t skillev-labs-auth:V2 .

 docker build -t skillev-labs-idor:v1 .

 docker build --load -t skillev-labs-idor:v1 .

 sudo -u postgres psql -d skillev