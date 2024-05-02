import prisma
import prisma.models
from pydantic import BaseModel


class DeleteBookingResponse(BaseModel):
    """
    Response model for DELETE /bookings/{bookingId}. This model returns a confirmation of the deletion.
    """
    success: bool  
    message: str

async def deleteBooking(bookingId: int) -> DeleteBookingResponse:
    """
    Deletes a specific booking. Uses the booking ID provided in the path. Upon deletion, it updates the Calendar Module to free up the time slot 
    and notifies the user and professional through the Notification Module.

    Args:
        bookingId (int): The unique identifier for the booking to be deleted. This identifier is used to locate the specific booking in the database.

    Returns:
        DeleteBookingResponse: Response model for DELETE /bookings/{bookingId}. This model returns a confirmation of the deletion.
    """
    booking = await prisma.models.Appointment.prisma().find_unique(where={'id': bookingId}, include={'user': True, 'profile': {'include': {'user': True}}})
    if not booking:
        return DeleteBookingResponse(success=False, message='Booking does not exist.')
    user_id = booking.user.id if booking.user else None
    professional_user_id = booking.profile.user.id if booking.profile and booking.profile.user else None
    if user_id and professional_user_id:
        message_user = f'Your booking on {booking.time.strftime('%Y-%m-%d %H:%M')} has been canceled.'
        message_professional = f'A booking on {booking.time.strftime('%Y-%m-%d %H:%M')} has been canceled.'
        await prisma.models.Notification.prisma().create_many(data=[{'userId': user_id, 'message': message_user}, {'userId': professional_user_id, 'message': message_professional}])
    await prisma.models.Appointment.prisma().delete(where={'id': bookingId})
    return DeleteBookingResponse(success=True, message='Booking and notifications processed successfully.')