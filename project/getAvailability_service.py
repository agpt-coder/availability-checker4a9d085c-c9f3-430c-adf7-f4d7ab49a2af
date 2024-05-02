from typing import Optional

import prisma
import prisma.models
from pydantic import BaseModel


class AvailabilityCheckResponse(BaseModel):
    """
    A response model to represent the current availability status of a professional.
    """

    isAvailable: bool
    currentActivity: Optional[str] = None


async def getAvailability(professionalId: int) -> AvailabilityCheckResponse:
    """
    Retrieves the current availability status of a specified professional. This endpoint will query the current state and return an availability status. Expected to be used frequently to provide real-time updates.

    Args:
        professionalId (int): The unique identifier for the professional whose availability is to be checked.

    Returns:
        AvailabilityCheckResponse: A response model to represent the current availability status of a professional.

    Example:
        # Assuming professionalId of 1 exists in RealTimeStatus and marked available
        getAvailability(1)
        > AvailabilityCheckResponse(isAvailable=True, currentActivity=None)
    """
    real_time_status = await prisma.models.RealTimeStatus.prisma().find_unique(
        where={"professionalInfoId": professionalId}
    )
    if real_time_status is None:
        return AvailabilityCheckResponse(
            isAvailable=False, currentActivity="No status available"
        )
    return AvailabilityCheckResponse(
        isAvailable=real_time_status.isAvailable,
        currentActivity=real_time_status.currentActivity,
    )
