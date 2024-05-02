import prisma
import prisma.models
from pydantic import BaseModel


class DeleteFeedbackResponse(BaseModel):
    """
    Response model indicating the result of the feedback deletion attempt. It will return a success message on successful deletion or an error message on failure, including lack of permissions or incorrect feedbackId.
    """

    message: str
    success: bool


async def deleteFeedback(feedbackId: int) -> DeleteFeedbackResponse:
    """
    Removes a feedback entry identified by its ID. Restricted to the user who posted the feedback or an admin. The route verifies the user's identity and permission, then deletes the feedback, returning a success or error response.

    Args:
    feedbackId (int): The unique identifier for the feedback to be deleted.

    Returns:
    DeleteFeedbackResponse: Response model indicating the result of the feedback deletion attempt. It will return a success message on successful deletion or an error message on failure, including lack of permissions or incorrect feedbackId.

    Example:
        async def test_deleteFeedback():
            response = await deleteFeedback(1)
            print(response)
    """
    feedback = await prisma.models.Feedback.prisma().find_many(where={"id": feedbackId})
    if not feedback:
        return DeleteFeedbackResponse(
            message="prisma.models.Feedback ID not found.", success=False
        )
    result = await prisma.models.Feedback.prisma().delete(where={"id": feedbackId})
    if result is None:
        return DeleteFeedbackResponse(
            message="Failed to delete prisma.models.Feedback. It may have been deleted already.",
            success=False,
        )
    return DeleteFeedbackResponse(
        message="prisma.models.Feedback successfully deleted.", success=True
    )
