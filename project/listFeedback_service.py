from datetime import datetime
from typing import List, Optional

import prisma
import prisma.models
from pydantic import BaseModel


class Feedback(BaseModel):
    """
    This subtype describes individual feedback entries as stored in the database.
    """

    id: int
    userId: int
    profileId: int
    content: str
    rating: int
    createdAt: datetime


class FeedbackListResponse(BaseModel):
    """
    A list of feedback entries that have been filtered as requested, if any.
    """

    feedbacks: List[Feedback]


async def listFeedback(
    professional_id: Optional[int], user_id: Optional[int]
) -> FeedbackListResponse:
    """
    Lists all feedback entries. Accessible by admins for monitoring or analysis purposes. Can be filtered by professional's ID or user's ID. Returns a list of feedback entries or an empty list if none are found.

    Args:
        professional_id (Optional[int]): Optional filtering by Professional's ID to view feedback for a specific professional.
        user_id (Optional[int]): Optional filtering by User's ID to view feedback given by a specific user.

    Returns:
        FeedbackListResponse: A list of feedback entries that have been filtered as requested, if any.
    """
    query_params = {}
    if professional_id:
        query_params["profileId"] = professional_id
    if user_id:
        query_params["userId"] = user_id
    feedback_records = await prisma.models.Feedback.prisma().find_many(
        where=query_params
    )
    feedback_list = [Feedback(**feedback.__dict__) for feedback in feedback_records]
    return FeedbackListResponse(feedbacks=feedback_list)
