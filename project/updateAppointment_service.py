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


class AppointmentUpdateResponse(BaseModel):
    """
    Response model indicating the outcome of the update operation, reflecting current state of the specified appointment.
    """

    success: bool
    updated_appointment: Appointment


async def updateAppointment(
    appointmentId: int,
    new_time: datetime,
    new_professionalId: Optional[int],
    notes: Optional[str],
) -> AppointmentUpdateResponse:
    """
    Provides functionality to update an existing appointment. This could involve changing the time, adding notes, or changing the professional booked. It ensures the changes are synchronized with the Booking Module and updates are reflected in real-time in the Calendar module.

    Args:
        appointmentId (int): The unique identifier for the appointment to be updated.
        new_time (datetime): The new time for the appointment, reflecting changes if any.
        new_professionalId (Optional[int]): ID of the new professional (if changed).
        notes (Optional[str]): Additional notes to be attached with the appointment.

    Returns:
        AppointmentUpdateResponse: Response model indicating the outcome of the update operation, reflecting current state of the specified appointment.

    """
    appointment = await prisma.models.Appointment.prisma().find_unique(
        where={"id": appointmentId}
    )
    if not appointment:
        return AppointmentUpdateResponse(success=False, updated_appointment=None)
    update_data = {"time": new_time, "updatedAt": datetime.now()}
    if new_professionalId is not None:
        update_data["profileId"] = new_professionalId
    if notes is not None:
        update_data["notes"] = notes
    updated_appointment = await prisma.models.Appointment.prisma().update(
        where={"id": appointmentId}, data=update_data
    )
    response = AppointmentUpdateResponse(
        success=True, updated_appointment=updated_appointment
    )
    return response
