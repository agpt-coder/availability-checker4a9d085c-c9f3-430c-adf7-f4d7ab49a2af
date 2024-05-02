from datetime import datetime
from enum import Enum
from typing import Optional

import prisma
import prisma.models
from pydantic import BaseModel


class Profile(BaseModel):
    """
    The model containing extended information about the user like bio and professional information.
    """

    firstName: str
    lastName: str
    bio: Optional[str] = None


class Role(Enum):
    """
    Enumeration of possible roles a user can hold, such as Admin or Professional.
    """

    value: str  # TODO(autogpt): "value" incorrectly overrides property of same name in class "Enum". reportIncompatibleMethodOverride


class User(BaseModel):
    """
    User model for general user information.
    """

    email: str
    role: Role


class Status(BaseModel):
    """
    Enumeration of possible appointment statuses such as Pending, Confirmed, Completed, and Cancelled.
    """

    pass


class BookingDetailsResponse(BaseModel):
    """
    Response model containing detailed information about the booking, including time, participants, and their roles.
    """

    bookingTime: datetime
    professional: Profile
    userDetails: User
    status: Status


async def getBooking(bookingId: int) -> BookingDetailsResponse:
    """
    Retrieves information about a specific booking. It fetches from an appointment table along with embedded user and professional profiles,
    and returns a composed response that includes key details about the booking.

    Args:
        bookingId (int): Unique identifier for the booking.

    Returns:
        BookingDetailsResponse: Response model containing detailed information about the booking,
                                 including time, professional details, and user details.

    Example:
        booking_details = await getBooking(5)
    """
    appointment = await prisma.models.Appointment.prisma().find_unique(
        where={"id": bookingId}, include={"user": True, "profile": True}
    )
    if not appointment:
        raise ValueError("Booking not found")
    professional_profile = Profile(
        firstName=appointment.profile.firstName,
        lastName=appointment.profile.lastName,
        bio=appointment.profile.bio,
    )
    userDetails = User(email=appointment.user.email, role=appointment.user.role.value)
    bookingDetails = BookingDetailsResponse(
        bookingTime=appointment.time,
        professional=professional_profile,
        userDetails=userDetails,
        status=appointment.status.value,
    )
    return bookingDetails
