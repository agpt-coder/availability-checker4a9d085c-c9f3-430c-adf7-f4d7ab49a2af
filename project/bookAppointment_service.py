from datetime import datetime
from typing import Optional

import prisma
import prisma.enums
import prisma.models
from pydantic import BaseModel


class Status(BaseModel):
    """
    Enumeration of possible appointment statuses such as Pending, Confirmed, Completed, and Cancelled.
    """

    pass


class AppointmentDetails(BaseModel):
    """
    Represents detailed information about the booked appointment.
    """

    appointmentId: int
    time: datetime
    professionalName: str
    userName: str
    status: Status


class CalendarBookingResponse(BaseModel):
    """
    Outputs the result of the booking attempt, reflecting the new status of the appointment along with a confirmation.
    """

    success: bool
    message: str
    appointmentDetails: AppointmentDetails


async def bookAppointment(
    professionalId: int, userId: int, time: datetime, notes: Optional[str] = None
) -> CalendarBookingResponse:
    """
    Allows a user or professional to book an appointment. This endpoint receives the details of the booking, such as professional ID, user ID, time slot, and optionally any special notes or requirements, then it communicates with the Booking Module to finalize the booking. A successful booking will update the professional's availability both in the Calendar and Real-Time Status Modules.

    Args:
        professionalId (int): The unique identifier for the professional.
        userId (int): The unique identifier for the user initiating the booking.
        time (datetime): Desired time slot for the appointment.
        notes (Optional[str]): Optional notes or special requirements for the booking.

    Returns:
        CalendarBookingResponse: Outputs the result of the booking attempt, reflecting the new status of the appointment along with a confirmation.
    """
    user = await prisma.models.User.prisma().find_unique(where={"id": userId})
    professional_profile = await prisma.models.Profile.prisma().find_unique(
        where={"userId": professionalId}
    )
    if not user or not professional_profile or (not professional_profile.user):
        return CalendarBookingResponse(
            success=False,
            message="User or Professional not found.",
            appointmentDetails=None,
        )
    if not user.profile:
        return CalendarBookingResponse(
            success=False,
            message="User's profile information is incomplete.",
            appointmentDetails=None,
        )
    new_appointment = await prisma.models.Appointment.prisma().create(
        data={
            "userId": userId,
            "profileId": professional_profile.id,
            "time": time,
            "status": prisma.enums.Status.Pending,
        }
    )
    appointment_details = AppointmentDetails(
        appointmentId=new_appointment.id,
        time=new_appointment.time,
        professionalName=f"{professional_profile.firstName} {professional_profile.lastName}",
        userName=f"{user.profile.firstName} {user.profile.lastName}",
        status=new_appointment.status,
    )
    return CalendarBookingResponse(
        success=True,
        message="Appointment booked successfully.",
        appointmentDetails=appointment_details,
    )
