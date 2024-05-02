from typing import List, Optional

import prisma
import prisma.models
from pydantic import BaseModel


class ProfessionalAvailabilityUpdate(BaseModel):
    """
    Details regarding a single professional's availability update.
    """

    professionalInfoId: int
    isAvailable: bool
    currentActivity: Optional[str] = None


class BulkAvailabilityUpdateResponse(BaseModel):
    """
    Response model returning the status of the bulk availability update operation.
    """

    updatedCount: int
    errors: Optional[List[str]] = None


async def bulkUpdateAvailability(
    updates: List[ProfessionalAvailabilityUpdate],
) -> BulkAvailabilityUpdateResponse:
    """
    Provides a mechanism to set or update the availability for multiple professionals at once. This is particularly valuable in scenarios where a group of professionals need to update their status due to a common event or change.

    Args:
        updates (List[ProfessionalAvailabilityUpdate]): List of individual availability updates for professionals.

    Returns:
        BulkAvailabilityUpdateResponse: Response model returning the status of the bulk availability update operation.
    """
    updated_count = 0
    errors = []
    for update in updates:
        try:
            status = await prisma.models.RealTimeStatus.prisma().find_unique(
                where={"professionalInfoId": update.professionalInfoId}
            )
            if not status:
                await prisma.models.RealTimeStatus.prisma().create(
                    data={
                        "professionalInfoId": update.professionalInfoId,
                        "isAvailable": update.isAvailable,
                        "currentActivity": update.currentActivity,
                    }
                )
            else:
                await prisma.models.RealTimeStatus.prisma().update(
                    where={"professionalInfoId": update.professionalInfoId},
                    data={
                        "isAvailable": update.isAvailable,
                        "currentActivity": update.currentActivity,
                    },
                )
            updated_count += 1
        except Exception as e:
            errors.append(
                f"Failed to update professionalInfoId {update.professionalInfoId}: {str(e)}"
            )
    return BulkAvailabilityUpdateResponse(
        updatedCount=updated_count, errors=errors if errors else None
    )
