import prisma
import prisma.models
from pydantic import BaseModel


class UpdateFeedbackResponse(BaseModel):
    """
    Response model after attempting to update a feedback. It provides a message indicating the success or failure of the operation.
    """

    message: str


async def updateFeedback(feedbackId: int, content: str) -> UpdateFeedbackResponse:
    """
    Allows updates to a specific feedback entry. Only the user who submitted the feedback or an admin can update it. Requires feedback ID and new feedback content. Validates the user’s permission and then updates the entry, returning a success or error message.

    Args:
        feedbackId (int): The unique identifier of the feedback to be updated.
        content (str): The new content to update the existing feedback.

    Returns:
        UpdateFeedbackResponse: Response model after attempting to update a feedback. It provides a message indicating the success or failure of the operation.
    """
    current_user_id, current_user_role = await get_current_user_details()
    feedback = await prisma.models.Feedback.prisma().find_unique(
        where={"id": feedbackId}
    )
    if feedback is None:
        return UpdateFeedbackResponse(
            message=f"No feedback found with ID: {feedbackId}"
        )
    if feedback.userId != current_user_id and current_user_role != "Admin":
        return UpdateFeedbackResponse(
            message="You do not have permission to update this feedback."
        )
    updated_feedback = await prisma.models.Feedback.prisma().update(
        where={"id": feedbackId}, data={"content": content}
    )
    return UpdateFeedbackResponse(message="Feedback has been successfully updated.")


async def get_current_user_details():
    """
    Simulates retrieval of the current user's ID and role from session or authentication context.
    Replace this method to integrate with actual user authentication system.

    Returns:
        tuple: (user_id: int, user_role: str) Tuple containing current user's ID and role
    """
    return (1, "Admin")
