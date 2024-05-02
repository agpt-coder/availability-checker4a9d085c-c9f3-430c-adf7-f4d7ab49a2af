import prisma
import prisma.models
from pydantic import BaseModel


class NotificationAvailabilityResponseModel(BaseModel):
    """
    Response model confirming that a notification has been sent successfully.
    """

    message: str
    status: str


async def sendAvailabilityAlert(
    professionalId: int, userId: int, newAvailability: bool
) -> NotificationAvailabilityResponseModel:
    """
    This endpoint sends alerts to users when there is a change in the availability status of professionals.
    It is triggered by the Real-Time Status Module. The endpoint accepts data such as professional ID,
    user ID, and the new availability status. It uses internal logic to send alerts either through email or SMS,
    based on user preferences.

    Args:
    professionalId (int): The unique identifier of the professional whose availability status has changed.
    userId (int): The unique identifier of the user to whom the notification will be sent.
    newAvailability (bool): The new availability status of the professional, either true (available) or false (not available).

    Returns:
    NotificationAvailabilityResponseModel: Response model confirming that a notification has been sent successfully.
    """
    user = await prisma.models.User.prisma().find_unique(
        where={"id": userId}, include={"profile": True}
    )
    professional_info = await prisma.models.ProfessionalInfo.prisma().find_first(
        where={"profile": {"userId": professionalId}}
    )
    if user is None or professional_info is None:
        return NotificationAvailabilityResponseModel(
            message="Notification failed: User or professional not found.",
            status="failed",
        )
    if user.profile is None:
        return NotificationAvailabilityResponseModel(
            message="Notification failed: User profile not found.", status="failed"
        )
    real_time_status = await prisma.models.RealTimeStatus.prisma().find_unique(
        where={"professionalInfoId": professional_info.id}
    )
    if real_time_status and real_time_status.isAvailable != newAvailability:
        await prisma.models.RealTimeStatus.prisma().update(
            where={"id": real_time_status.id}, data={"isAvailable": newAvailability}
        )
    available_text = "available" if newAvailability else "not available"
    message = (
        f"{user.profile.firstName} {user.profile.lastName} is now {available_text}."
    )
    await prisma.models.Notification.prisma().create(
        data={"userId": userId, "message": message}
    )
    return NotificationAvailabilityResponseModel(
        message="Notification sent successfully.", status="success"
    )
