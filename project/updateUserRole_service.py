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


class RoleUpdateResponse(BaseModel):
    """
    Confirmatory response indicating whether the role update was successful or not. Includes the ID of the updated user and the new role, or an error message if applicable.
    """

    success: bool
    user_id: str
    new_role: Role
    message: Optional[str] = None


async def updateUserRole(id: str, new_role: Role) -> RoleUpdateResponse:
    """
    Updates the role of a user in the system, restricted to be performed by admin users only.

    Args:
        id (str): The unique identifier of the user whose role is being updated.
        new_role (Role): The new role to be assigned to the user.

    Returns:
        RoleUpdateResponse: A detailed response about the outcome of the update operation.
    """
    user = await prisma.models.User.prisma().find_unique(where={"id": int(id)})
    if not user:
        return RoleUpdateResponse(
            success=False, user_id=id, message="User not found."
        )  # TODO(autogpt): Argument missing for parameter "new_role". reportCallIssue
    try:
        updated_user = await prisma.models.User.prisma().update(
            {"where": {"id": int(id)}, "data": {"role": new_role}}
        )  # TODO(autogpt): Argument missing for parameter "where". reportCallIssue
        return RoleUpdateResponse(
            success=True,
            user_id=id,
            new_role=new_role,
            message="User role successfully updated.",
        )
    except Exception as e:
        return RoleUpdateResponse(
            success=False, user_id=id, message=f"Failed to update role: {str(e)}"
        )  # TODO(autogpt): Argument missing for parameter "new_role". reportCallIssue
