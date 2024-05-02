import prisma
import prisma.models
from pydantic import BaseModel


class FeedbackResponse(BaseModel):
    """
    A response to be returned after feedback submission. It includes information whether the attempt was successful or if errors occurred.
    """

    success: bool
    message: str


async def createFeedback(
    professional_id: str, user_id: str, content: str, rating: int
) -> FeedbackResponse:
    """
    This route allows a user to submit feedback about a professional. It accepts feedback details and the user's ID (retrieved via session tokens) as input. The route checks the user’s validity through the User Management Module before saving the feedback. Expected response is a success message or error details.

    Args:
    professional_id (str): The ID of the professional to whom the feedback is being given.
    user_id (str): The ID of the user submitting the feedback. Extracted from session token and validated.
    content (str): The textual content of the feedback given by the user.
    rating (int): A numerical rating that accompanies the feedback text, typically on a scale.

    Returns:
    FeedbackResponse: A response to be returned after feedback submission. It includes information whether the attempt was successful or if errors occurred.
    """
    user = await prisma.models.User.prisma().find_unique(where={"id": int(user_id)})
    if not user:
        return FeedbackResponse(success=False, message="User not found.")
    professional = await prisma.models.Profile.prisma().find_unique(
        where={"id": int(professional_id)}
    )
    if not professional:
        return FeedbackResponse(success=False, message="Professional not found.")
    if not professional.professionalInfo:
        return FeedbackResponse(
            success=False, message="This professional does not accept feedback."
        )
    feedback = await prisma.models.Feedback.prisma().create(
        data={
            "userId": int(user_id),
            "profileId": int(professional_id),
            "content": content,
            "rating": rating,
        }
    )
    if feedback:
        return FeedbackResponse(
            success=True, message="Feedback submitted successfully."
        )
    else:
        return FeedbackResponse(success=False, message="Failed to submit feedback.")
