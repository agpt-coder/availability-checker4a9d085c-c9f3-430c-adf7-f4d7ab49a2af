from enum import Enum
from typing import Optional

import prisma
import prisma.models
from pydantic import BaseModel


class Role(Enum):
    """
    Enumeration of possible roles a user can hold, such as Admin or Professional.
    """

    value: str  # TODO(autogpt): "value" incorrectly overrides property of same name in class "Enum". reportIncompatibleMethodOverride


class Profile(BaseModel):
    """
    The model containing extended information about the user like bio and professional information.
    """

    firstName: str
    lastName: str
    bio: Optional[str] = None


class UserDetailsResponse(BaseModel):
    """
    Contains detailed information about the user, including roles and status, after securing proper authorization. This model is crucial for role-based access in the application.
    """

    email: str
    role: Role
    status: str
    profile: Profile


async def getUserDetails(id: str) -> UserDetailsResponse:
    """
    Fetches detailed user information for a specific user ID. It requires authentication and is critical for
    confirming user permissions across modules and delivering personalized alerts. The response includes fields
    like user's role, status, and registered details.

    Args:
        id (str): The unique identifier for the user, used to fetch comprehensive details.

    Returns:
        UserDetailsResponse: Contains detailed information about the user, including roles and status,
        after securing proper authorization. This model is crucial for role-based access in the application.

    Example:
        response = await getUserDetails('1')
        print(response)
    """
    user = await prisma.models.User.prisma().find_unique(
        where={"id": int(id)}, include={"profile": True}
    )
    if not user:
        raise ValueError(f"User with ID {id} does not exist.")
    user_profile = (
        user.profile if user.profile else Profile(firstName="", lastName="", bio=None)
    )
    user_details = UserDetailsResponse(
        email=user.email,
        role=Role[user.role],
        status="Active" if user else "Inactive",
        profile=user_profile,
    )
    return user_details
