from datetime import datetime
from typing import Optional

import prisma
import prisma.models
from pydantic import BaseModel


class Status(BaseModel):
    """
    Enumeration of possible appointment statuses such as Pending, Confirmed, Completed, and Cancelled.
    """

    pass


class Appointment(BaseModel):
    """
    Details an appointment which includes ID, associated user and professional ID, time of the appointment, and current status.
    """

    id: int
    userId: int
    profileId: int
    time: datetime
    status: Status
    notes: Optional[str] = None


class UpdateBookingResponse(BaseModel):
    """
    Response model indicating the result of the booking update operation, including a confirmation of the changes made.
    """

    success: bool
    message: str
    updatedBooking: Appointment


async def updateBooking(
    bookingId: int, newTime: Optional[datetime], status: Status
) -> UpdateBookingResponse:
    """
    Updates details of an existing booking. It could be updating the time or canceling the booking.
    Notifies the professional and user of the updated booking details through the Notification Module.
    Required information includes booking ID and new booking details.

    Args:
        bookingId (int): The ID of the booking to be updated.
        newTime (Optional[datetime]): The new time for the booking, if it is being rescheduled.
        status (Status): The updated status of the booking, typically to confirm cancellation or other changes.

    Returns:
        UpdateBookingResponse: Response model indicating the result of the booking update operation,
                               including a confirmation of the changes made.
    """
    appointment = await prisma.models.Appointment.prisma().find_unique(
        where={"id": bookingId}
    )
    if not appointment:
        return UpdateBookingResponse(
            success=False,
            message=f"No booking found with ID {bookingId}",
            updatedBooking=None,
        )
    updated_data = {"status": status}
    if newTime:
        updated_data["time"] = newTime
    updated_appointment = await prisma.models.Appointment.prisma().update(
        where={"id": bookingId}, data=updated_data
    )
    user_notification_message = f"Your booking has been updated. New status: {status}."
    professional_notification_message = (
        f"Booking with ID {bookingId} has been updated. New status: {status}."
    )
    profile = await prisma.models.Profile.prisma().find_unique(
        where={"id": updated_appointment.profileId}, include={"user": True}
    )
    if profile and profile.user:
        await prisma.models.Notification.prisma().create(
            data={
                "userId": updated_appointment.userId,
                "message": user_notification_message,
                "isRead": False,
                "createdAt": datetime.now(),
            }
        )
        await prisma.models.Notification.prisma().create(
            data={
                "userId": profile.user.id,
                "message": professional_notification_message,
                "isRead": False,
                "createdAt": datetime.now(),
            }
        )
    return UpdateBookingResponse(
        success=True,
        message="Booking updated successfully",
        updatedBooking=updated_appointment,
    )
