import prisma
import prisma.enums
import prisma.models
from pydantic import BaseModel


class DeleteUserResponse(BaseModel):
    """
    Response model confirming the deletion of the user. It indicates whether the deletion was successfully executed or if there were any issues (e.g., user not found or insufficient permissions).
    """

    success: bool
    message: str


async def deleteUser(
    id: str, confirmation: bool, admin_user_id: str, token: str
) -> DeleteUserResponse:
    """
    This endpoint provides a mechanism for removing a user from the system database. It is restricted to admins and requires a confirmation step through their authenticated session before proceeding with deletion.

    Args:
        id (str): The unique identifier for the user to delete.
        confirmation (bool): Confirmation flag to ensure that the delete action is intentional.
        admin_user_id (str): The ID of the admin authorized to delete the user.
        token (str): Authentication token to validate the admin's session.

    Returns:
        DeleteUserResponse: Response model confirming the deletion of the user. It indicates whether the deletion was successfully executed or if there were any issues (e.g., user not found or insufficient permissions).
    """
    admin_user = await prisma.models.User.prisma().find_unique(
        where={"id": int(admin_user_id)}
    )
    if (
        not admin_user
        or admin_user.role != prisma.enums.Role.Admin
        or (not validate_token(admin_user, token))
    ):
        return DeleteUserResponse(
            success=False, message="Invalid admin credentials or token."
        )
    if not confirmation:
        return DeleteUserResponse(success=False, message="Deletion not confirmed.")
    user_to_delete = await prisma.models.User.prisma().find_unique(
        where={"id": int(id)}
    )
    if user_to_delete is None:
        return DeleteUserResponse(success=False, message="User not found.")
    await prisma.models.User.prisma().delete(where={"id": int(id)})
    return DeleteUserResponse(success=True, message="User successfully deleted.")


def validate_token(user, token):
    """
    Simulates token validation against stored user credentials.

    Args:
        user (prisma.models.User): The user data from the database.
        token (str): The provided authentication token.

    Returns:
        bool: Whether the token is valid for the given user.
    """
    return token == user.email[::-1]
