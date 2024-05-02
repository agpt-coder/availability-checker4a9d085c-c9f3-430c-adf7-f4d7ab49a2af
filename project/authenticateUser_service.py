import bcrypt
import prisma
import prisma.models
from jose import jwt
from pydantic import BaseModel


class AuthenticationResponse(BaseModel):
    """
    The response model returns a JWT token that the client can use in subsequent requests to authenticate sessions if the credentials are verified successfully.
    """

    token: str


async def authenticateUser(email: str, password: str) -> AuthenticationResponse:
    """
    This endpoint handles user authentication. Users submit their email and password,
    which are validated against the stored credentials. Upon successful authentication,
    it issues a token (JWT) recognizable for subsequent requests that require authentication.

    Args:
        email (str): The email address of the user attempting to authenticate.
                     This should match with the registered email in the User database.
        password (str): The user's password. This should be verified against
                        the hashed password stored in the User database.

    Returns:
        AuthenticationResponse: The response model returns a JWT token that the client
        can use in subsequent requests to authenticate sessions if the credentials
        are verified successfully.
    """
    user = await prisma.models.User.prisma().find_unique(where={"email": email})
    if user and bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
        token_data = {"user_id": user.id, "role": user.role}
        token = jwt.encode(token_data, "your-secret-key", algorithm="HS256")
        return AuthenticationResponse(token=token)
    else:
        raise Exception("Invalid email or password")
