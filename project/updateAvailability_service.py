from typing import Optional

import prisma
import prisma.models
from pydantic import BaseModel


class RealTimeStatus(BaseModel):
    """
    Related real-time status type with details about availability and current activity.
    """

    isAvailable: bool
    currentActivity: Optional[str] = None


class AvailabilityUpdateResponse(BaseModel):
    """
    Response model indicating the success or failure of the update operation.
    """

    success: bool
    message: str
    updatedStatus: RealTimeStatus


async def updateAvailability(
    professionalId: int, isAvailable: bool, currentActivity: Optional[str] = None
) -> AvailabilityUpdateResponse:
    """
    Allows for partial updates to a professional's availability status. Useful for quick status toggles,
    like marking a brief break or returning to an available state.

    Args:
        professionalId (int): The ID for the professional whose availability status is to be updated.
        isAvailable (bool): Flag indicating whether the professional is currently available; True for available, false for unavailable.
        currentActivity (Optional[str]): Optional brief description of the current activity or reason for availability status change.

    Returns:
        AvailabilityUpdateResponse: Response model indicating the success or failure of the update operation.

    Example:
        response = await updateAvailability(1, False, "In a meeting")
        print(response.success)  # True
        print(response.message)  # "Availability status updated successfully."
        print(response.updatedStatus.isAvailable)  # False
        print(response.updatedStatus.currentActivity)  # "In a meeting"
    """
    try:
        rt_status = await prisma.models.RealTimeStatus.prisma().find_unique(
            where={"professionalInfoId": professionalId}
        )
        if not rt_status:
            return AvailabilityUpdateResponse(
                success=False,
                message=f"No real-time status found for professional ID {professionalId}.",
                updatedStatus=RealTimeStatus(
                    isAvailable=isAvailable, currentActivity=currentActivity
                ),
            )
        updated_status = await prisma.models.RealTimeStatus.prisma().update(
            where={"professionalInfoId": professionalId},
            data={"isAvailable": isAvailable, "currentActivity": currentActivity},
        )
        return AvailabilityUpdateResponse(
            success=True,
            message="Availability status updated successfully.",
            updatedStatus=RealTimeStatus(
                isAvailable=updated_status.isAvailable,
                currentActivity=updated_status.currentActivity,
            ),
        )
    except Exception as e:
        return AvailabilityUpdateResponse(
            success=False,
            message=f"Failed to update availability: {str(e)}",
            updatedStatus=RealTimeStatus(
                isAvailable=isAvailable, currentActivity=currentActivity
            ),
        )
