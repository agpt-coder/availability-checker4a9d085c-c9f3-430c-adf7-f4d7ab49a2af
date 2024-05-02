from typing import List, Optional

import prisma
import prisma.models
from pydantic import BaseModel


class FetchAvailabilityRequest(BaseModel):
    """
    Request model for fetching the real-time availability of all professionals. No specific parameters are needed for this request as it fetches availability in bulk.
    """

    pass


class ProfessionalAvailability(BaseModel):
    """
    Details the availability and current activity of a single professional.
    """

    professional_id: int
    is_available: bool
    current_activity: Optional[str] = None


class FetchAvailabilityResponse(BaseModel):
    """
    Provides a list of all professionals' availability including their current activity and availability status.
    """

    availability: List[ProfessionalAvailability]


async def checkAllAvailability(
    request: FetchAvailabilityRequest,
) -> FetchAvailabilityResponse:
    """
    Fetches the availability status of all professionals currently registered in the system. Enables administrative or collective views on professional availability.

    Args:
        request (FetchAvailabilityRequest): Request model for fetching the real-time availability of all professionals. No specific parameters are needed for this request as it fetches availability in bulk.

    Returns:
        FetchAvailabilityResponse: Provides a list of all professionals' availability including their current activity and availability status.

    Example:
        request = FetchAvailabilityRequest()
        response = await checkAllAvailability(request)
        print(response.availability)  # Outputs a list of ProfessionalAvailability models
    """
    real_time_statuses = await prisma.models.RealTimeStatus.prisma().find_many(
        include={"professionalInfo": {"include": {"profile": True}}}
    )
    availabilities = [
        ProfessionalAvailability(
            professional_id=status.professionalInfo.profile.userId,
            is_available=status.isAvailable,
            current_activity=status.currentActivity,
        )
        for status in real_time_statuses
        if status.professionalInfo and status.professionalInfo.profile
    ]
    response = FetchAvailabilityResponse(availability=availabilities)
    return response
