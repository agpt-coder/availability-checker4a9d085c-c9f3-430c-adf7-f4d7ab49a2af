import prisma
import prisma.models
from pydantic import BaseModel


class DeleteProfessionalAvailabilityResponse(BaseModel):
    """
    Response model for the deletion of a professional's availability. Will return a confirmation message along with the status of the operation.
    """

    message: str
    status: bool


async def deleteAvailability(
    professionalId: int,
) -> DeleteProfessionalAvailabilityResponse:
    """
    Removes a professional's availability status from the system, typically used when a professional is no longer working or needs to be temporarily disabled from the system.

    Args:
        professionalId (int): The unique identifier for the professional whose availability status is to be deleted.

    Returns:
        DeleteProfessionalAvailabilityResponse: Response model for the deletion of a professional's availability. Will return a confirmation message along with the status of the operation.

    Example:
        response = deleteAvailability(5)
        > DeleteProfessionalAvailabilityResponse(message="Professional availability removed.", status=True)
    """
    profile = await prisma.models.Profile.prisma().find_first(
        where={"professionalInfo": {"profileId": professionalId}},
        include={"professionalInfo": True},
    )
    if profile and profile.professionalInfo:
        await prisma.models.RealTimeStatus.prisma().delete_many(
            where={"professionalInfoId": profile.professionalInfo.id}
        )
        profile.professionalInfo = await prisma.models.ProfessionalInfo.prisma().update(
            where={"id": profile.professionalInfo.id}, data={"availability": "{}"}
        )
        return DeleteProfessionalAvailabilityResponse(
            message="Professional availability removed.", status=True
        )
    else:
        return DeleteProfessionalAvailabilityResponse(
            message="Failed to find professional or availability info.", status=False
        )
