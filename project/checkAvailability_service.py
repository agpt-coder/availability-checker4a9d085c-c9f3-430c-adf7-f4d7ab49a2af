from datetime import datetime, timedelta
from typing import Optional

import prisma
import prisma.models
from pydantic import BaseModel


class ProfessionalAvailabilityResponse(BaseModel):
    """
    Response model indicating the real-time availability status of a professional, which considers both scheduled and spontaneous events that might affect this status.
    """

    isAvailable: bool
    nextAvailableTime: Optional[datetime] = None
    message: Optional[str] = None


async def checkAvailability(professionalId: int) -> ProfessionalAvailabilityResponse:
    """
    Checks the real-time availability of a professional via the Calendar Module before booking. It retrieves the
    professional's schedule and current activities and returns whether they are available.

    This function examines both the current real-time availability status from the `RealTimeStatus` model and checks
    the `Calendar` and `Appointment` models for any existing appointments that clash with the current time.

    Args:
    professionalId (int): The unique identifier for the professional whose availability is being checked.

    Returns:
    ProfessionalAvailabilityResponse: Response model indicating the real-time availability status of a professional, which considers both scheduled and spontaneous events that might affect this status.
    """
    real_time_status = await prisma.models.RealTimeStatus.prisma().find_unique(
        where={"professionalInfoId": professionalId}
    )
    if real_time_status and (not real_time_status.isAvailable):
        return ProfessionalAvailabilityResponse(
            isAvailable=False,
            message=f"Currently not available due to: {real_time_status.currentActivity}.",
        )
    current_time = datetime.now()
    appointments = await prisma.models.Appointment.prisma().find_many(
        where={
            "profileId": professionalId,
            "time": {"gte": current_time},
            "status": {"not": "Cancelled"},
        },
        order={"time": "asc"},
    )
    if appointments:
        first_appointment = appointments[0]
        if first_appointment.time <= current_time:
            return ProfessionalAvailabilityResponse(
                isAvailable=False,
                nextAvailableTime=first_appointment.time + timedelta(minutes=30),
                message="Currently in an appointment.",
            )
        return ProfessionalAvailabilityResponse(
            isAvailable=False,
            nextAvailableTime=first_appointment.time,
            message=f"Next available at {first_appointment.time}.",
        )
    return ProfessionalAvailabilityResponse(
        isAvailable=True, message="Professional is currently available."
    )
