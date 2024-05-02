from datetime import datetime

import prisma
import prisma.enums
import prisma.models
from pydantic import BaseModel


class Status(BaseModel):
    """
    Enumeration of possible appointment statuses such as Pending, Confirmed, Completed, and Cancelled.
    """

    pass


class BookingConfirmationResponse(BaseModel):
    """
    Response model after a successful booking, confirming the details of the newly created appointment.
    """

    message: str
    appointmentId: int
    status: Status


async def createBooking(
    userId: int, professionalId: int, appointmentTime: datetime
) -> BookingConfirmationResponse:
    """
    Creates a booking for a user with a professional, consulting the Calendar Module to confirm availability. Upon successful booking, it triggers the Notification Module to send confirmation to the user. Requires details of the booking including user ID, professional ID, and time of the appointment.

    Args:
        userId (int): The ID of the user who is creating the booking.
        professionalId (int): The ID of the professional with whom the booking is to be made.
        appointmentTime (datetime): The desired time for the appointment.

    Returns:
        BookingConfirmationResponse: Response model after a successful booking, confirming the details of the newly created appointment.
    """
    user = await prisma.models.User.prisma().find_unique(where={"id": userId})
    professional_profile = await prisma.models.Profile.prisma().find_unique(
        where={"id": professionalId}, include={"professionalInfo": True}
    )
    if (
        not user
        or not professional_profile
        or (not professional_profile.professionalInfo)
    ):
        return BookingConfirmationResponse(
            message="User or professional not found",
            appointmentId=-1,
            status=prisma.enums.Status.Cancelled,
        )
    overlapping_appointments = await prisma.models.Appointment.prisma().find_many(
        where={
            "profileId": professionalId,
            "status": prisma.enums.Status.Confirmed,
            "time": appointmentTime,
        }
    )
    if overlapping_appointments:
        return BookingConfirmationResponse(
            message="No available slots for the requested time",
            appointmentId=-1,
            status=prisma.enums.Status.Cancelled,
        )
    new_appointment = await prisma.models.Appointment.prisma().create(
        data={
            "userId": userId,
            "profileId": professionalId,
            "time": appointmentTime,
            "status": prisma.enums.Status.Pending,
        }
    )
    await prisma.models.Notification.prisma().create(
        data={
            "userId": userId,
            "message": f"Your appointment with professional ID {professionalId} at {appointmentTime} has been booked.",
            "isRead": False,
        }
    )
    return BookingConfirmationResponse(
        message="Booking successfully created.",
        appointmentId=new_appointment.id,
        status=prisma.enums.Status.Confirmed,
    )
