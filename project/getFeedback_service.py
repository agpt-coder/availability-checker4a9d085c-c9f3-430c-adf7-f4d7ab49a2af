from datetime import datetime

import prisma
import prisma.models
from pydantic import BaseModel


class NestedUserDetails(BaseModel):
    """
    Details of the user including any relevant user identification.
    """

    userId: str
    username: str
    profilePic: str


class FeedbackDetailsResponse(BaseModel):
    """
    The response model returning the details of the feedback if the requester has the appropriate permissions to view it. Includes details such as the feedback content, rating, and associated user info.
    """

    id: str
    content: str
    rating: int
    createdAt: datetime
    userDetails: NestedUserDetails


async def getFeedback(feedbackId: str, role: str) -> FeedbackDetailsResponse:
    """
    Fetches details of a specific feedback entry by its ID. It ensures the
    requester has the right to view the feedback, either by being an
    admin, the user who created it, or the professional it's about.
    Returns the feedback details if permitted.

    Args:
        feedbackId (str): The unique identifier for the feedback entry,
                          used to fetch the specific feedback details.
        role (str): The role of the individual requesting to view the feedback.
                    This field determines permission access.

    Returns:
        FeedbackDetailsResponse: The response model returning the details of
                                 the feedback if the requester has the appropriate
                                 permissions to view it. Includes details such as
                                 the feedback content, rating, and associated user info.
    """
    feedback = await prisma.models.Feedback.prisma().find_unique(
        where={"id": int(feedbackId)}, include={"user": True, "profile": True}
    )
    if feedback is None:
        raise ValueError("Feedback not found")
    feedback_user_id = str(
        feedback.user_id
    )  # TODO(autogpt): Cannot access member "user_id" for type "Feedback"
    #     Member "user_id" is unknown. reportAttributeAccessIssue
    feedback_profile_id = str(
        feedback.profile_id
    )  # TODO(autogpt): Cannot access member "profile_id" for type "Feedback"
    #     Member "profile_id" is unknown. reportAttributeAccessIssue
    if role != "Admin" and feedback_user_id != role and (feedback_profile_id != role):
        raise PermissionError("You do not have permission to view this feedback")
    user_details = await prisma.models.User.prisma().find_unique(
        where={"id": feedback.user_id}
    )  # TODO(autogpt): Cannot access member "user_id" for type "Feedback"
    #     Member "user_id" is unknown. reportAttributeAccessIssue
    profile_pic_url = (
        user_details.profile.profilePic
        if user_details.profile and user_details.profile.profilePic
        else "default_profile.png"
    )  # TODO(autogpt): Cannot access member "profilePic" for type "Profile"
    #     Member "profilePic" is unknown. reportAttributeAccessIssue
    feedback_details_response = FeedbackDetailsResponse(
        id=feedbackId,
        content=feedback.content,
        rating=feedback.rating,
        createdAt=feedback.createdAt,
        userDetails=NestedUserDetails(
            userId=feedback_user_id,
            username=user_details.username,
            profilePic=profile_pic_url,
        ),
    )  # TODO(autogpt): Cannot access member "username" for type "User"
    #     Member "username" is unknown. reportAttributeAccessIssue
    return feedback_details_response
