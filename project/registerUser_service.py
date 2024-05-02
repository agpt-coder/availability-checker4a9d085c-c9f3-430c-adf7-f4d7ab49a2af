from typing import Optional

import bcrypt
import prisma
import prisma.enums
import prisma.models
from pydantic import BaseModel


class UserRegistrationResponse(BaseModel):
    """
    Responds with the outcome of the registration attempt including the newly assigned user ID if successful.
    """

    success: bool
    user_id: Optional[int] = None
    message: str


async def registerUser(
    name: str, email: str, password: str
) -> UserRegistrationResponse:
    """
    This route allows new users to register. It accepts user details such as name, email, and password, then creates a
    new user record in the database. The response includes a success message and user ID. It utilizes hashing for
    passwords before storage for security.

    Args:
        name (str): Full name of the user registering.
        email (str): Email of the user which will be unique to each user.
        password (str): Password that will be hashed before storage for security.

    Returns:
        UserRegistrationResponse: Responds with the outcome of the registration attempt including the newly assigned user ID if successful.

    Example:
        registerUser("John Doe", "john.doe@example.com", "s3cr3t")
        > {
            "success": True,
            "user_id": 123,
            "message": "User registered successfully."
        }
    """
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    try:
        user = await prisma.models.User.prisma().create(
            data={
                "email": email,
                "password": hashed_password.decode("utf-8"),
                "role": prisma.enums.Role.User,
                "profile": {
                    "create": {
                        "firstName": name.split()[0],
                        "lastName": " ".join(name.split()[1:])
                        if len(name.split()) > 1
                        else "",
                    }
                },
            }
        )
        return UserRegistrationResponse(
            success=True, user_id=user.id, message="User registered successfully."
        )
    except Exception as e:
        return UserRegistrationResponse(
            success=False, message=f"Failed to register user: {str(e)}"
        )
