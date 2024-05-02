import prisma
import prisma.models
from pydantic import BaseModel


class BookingNotificationResponse(BaseModel):
    """
    This response model provides a confirmation that the notification has been sent successfully along with details like a message.
    """

    success: bool
    message: str


async def sendBookingConfirmation(
    booking_id: int, user_id: int, professional_id: int
) -> BookingNotificationResponse:
    """
    This route handles the sending of booking confirmation notifications to users. It is activated once a booking is
    successfully made through the Booking Module. The endpoint receives information like booking ID, user ID, and
    professional ID, and sends a confirmation message detailing the booking date, time, and professional's name.

    Args:
        booking_id (int): The ID of the booking, used to fetch booking details.
        user_id (int): The ID of the user to whom the notification is to be sent.
        professional_id (int): The ID of the professional involved in the booking, to fetch additional details like name for the notification.

    Returns:
        BookingNotificationResponse: This response model provides a confirmation that the notification has been sent successfully along with details like a message.
    """
    booking = await prisma.models.Appointment.prisma().find_unique(
        where={"id": booking_id}, include={"profile": True}
    )
    if booking is None:
        return BookingNotificationResponse(success=False, message="Booking not found.")
    if booking.profile is None:
        return BookingNotificationResponse(
            success=False,
            message="Profile information for the professional is missing.",
        )
    user = await prisma.models.User.prisma().find_unique(where={"id": user_id})
    if user is None:
        return BookingNotificationResponse(success=False, message="User not found.")
    professional_name = booking.profile.firstName + " " + booking.profile.lastName
    booking_datetime = booking.time.strftime("%Y-%m-%d at %H:%M")
    message = f"Booking confirmed! Your appointment with {professional_name} is scheduled for {booking_datetime}."
    await prisma.models.Notification.prisma().create(
        data={"userId": user_id, "message": message}
    )
    return BookingNotificationResponse(success=True, message=message)
