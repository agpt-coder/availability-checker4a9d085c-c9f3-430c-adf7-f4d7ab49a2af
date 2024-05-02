import prisma
import prisma.enums
import prisma.models
from pydantic import BaseModel


class CancelAppointmentResponse(BaseModel):
    """
    This model is used to provide a confirmation response indicating whether the appointment was successfully canceled.
    """

    success: bool
    message: str


async def cancelAppointment(appointmentId: int) -> CancelAppointmentResponse:
    """
    Enables users or professionals to cancel an appointment. This will interact with the Booking Module to free up the previously reserved slot and update the professional’s availability status in the Real-Time Status Module.

    This function checks for the appointment in the database and updates its status to 'Cancelled'. It should also handle any errors or situations where the appointment doesn't exist.

    Args:
        appointmentId (int): Unique identifier of the appointment to be canceled.

    Returns:
        CancelAppointmentResponse: This model is used to provide a confirmation response indicating whether the appointment was successfully canceled.

    Example:
        response = await cancelAppointment(123)
        print(response)
        > CancelAppointmentResponse(success=True, message='Appointment canceled successfully.')
    """
    appointment = await prisma.models.Appointment.prisma().find_unique(
        where={"id": appointmentId}
    )
    if appointment is None:
        return CancelAppointmentResponse(
            success=False, message="No appointment found with the provided ID."
        )
    if appointment.status == prisma.enums.Status.Cancelled:
        return CancelAppointmentResponse(
            success=False, message="The appointment is already canceled."
        )
    updated_appointment = await prisma.models.Appointment.prisma().update(
        where={"id": appointmentId}, data={"status": prisma.enums.Status.Cancelled}
    )
    if updated_appointment:
        return CancelAppointmentResponse(
            success=True, message="Appointment canceled successfully."
        )
    else:
        return CancelAppointmentResponse(
            success=False, message="Failed to cancel the appointment."
        )
