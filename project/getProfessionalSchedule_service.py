from datetime import date, datetime, timedelta
from typing import List, Optional

import prisma
import prisma.models
from pydantic import BaseModel


class ScheduleDetail(BaseModel):
    """
    Details a single time slot in the professional's schedule, indicating whether it's booked or free.
    """

    startTime: datetime
    endTime: datetime
    isBooked: bool
    status: Optional[str] = None


class FetchScheduleResponse(BaseModel):
    """
    Output model showcasing the professional's schedule, including both booked appointments and available slots, associated with real-time statuses.
    """

    professionalId: str
    schedules: List[ScheduleDetail]


async def getProfessionalSchedule(
    professionalId: str,
    startDate: Optional[date] = None,
    endDate: Optional[date] = None,
) -> FetchScheduleResponse:
    """
    Fetches the full schedule of a professional for a specific day or a range of days.

    Args:
        professionalId (str): The unique identifier of the professional whose schedule is being requested.
        startDate (Optional[date]): The start date of the period for which the schedule is requested. Defaults to today if None.
        endDate (Optional[date]): The end date of the period for which the schedule is requested. Only needed if a range is required.

    Returns:
        FetchScheduleResponse: Output model showcasing the professional's schedule, including both booked appointments and available slots, associated with real-time statuses.
    """
    if startDate is None:
        startDate = date.today()
    if endDate is None:
        endDate = startDate
    appointments = await prisma.models.Appointment.prisma().find_many(
        where={
            "AND": [
                {
                    "profile": {
                        "professionalInfo": {"profileId": {"equals": professionalId}}
                    }
                },
                {"time": {"gte": datetime.combine(startDate, datetime.min.time())}},
                {"time": {"lte": datetime.combine(endDate, datetime.max.time())}},
            ]
        },
        order={"time": "asc"},
    )
    schedule_details = []
    for appointment in appointments:
        start_time = appointment.time
        end_time = start_time + timedelta(hours=1)
        schedule_details.append(
            ScheduleDetail(
                startTime=start_time,
                endTime=end_time,
                isBooked=True,
                status=appointment.status.name,
            )
        )
    return FetchScheduleResponse(
        professionalId=professionalId, schedules=schedule_details
    )
