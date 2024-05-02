import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import (
    date,
)  # TODO(autogpt): "date" is unknown import symbol. reportAttributeAccessIssue
from typing import List, Optional

import project.authenticateUser_service
import project.bookAppointment_service
import project.bulkUpdateAvailability_service
import project.cancelAppointment_service
import project.checkAllAvailability_service
import project.checkAvailability_service
import project.createBooking_service
import project.createFeedback_service
import project.deleteAvailability_service
import project.deleteBooking_service
import project.deleteFeedback_service
import project.deleteUser_service
import project.getAvailability_service
import project.getBooking_service
import project.getFeedback_service
import project.getProfessionalSchedule_service
import project.getUserDetails_service
import project.listFeedback_service
import project.registerUser_service
import project.sendAvailabilityAlert_service
import project.sendBookingConfirmation_service
import project.setAvailability_service
import project.updateAppointment_service
import project.updateAvailability_service
import project.updateBooking_service
import project.updateFeedback_service
import project.updateUserRole_service
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response
from prisma import Prisma

logger = logging.getLogger(__name__)

db_client = Prisma(auto_register=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db_client.connect()
    yield
    await db_client.disconnect()


app = FastAPI(
    title="Availability Checker",
    lifespan=lifespan,
    description="Function that returns the real-time availability of professionals, updating based on current activity or schedule.",
)


@app.post(
    "/availability/{professionalId}",
    response_model=project.setAvailability_service.ProfessionalAvailabilityUpdateResponse,
)
async def api_post_setAvailability(
    professionalId: str, isAvailable: bool, currentActivity: Optional[str]
) -> project.setAvailability_service.ProfessionalAvailabilityUpdateResponse | Response:
    """
    Sets or updates the availability status of a professional. This will not only update the module's internal state but also trigger an interaction with the Calendar Module to update the professional's schedule.
    """
    try:
        res = project.setAvailability_service.setAvailability(
            professionalId, isAvailable, currentActivity
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post("/feedback", response_model=project.createFeedback_service.FeedbackResponse)
async def api_post_createFeedback(
    professional_id: str, user_id: str, content: str, rating: int
) -> project.createFeedback_service.FeedbackResponse | Response:
    """
    This route allows a user to submit feedback about a professional. It accepts feedback details and the user's ID (retrieved via session tokens) as input. The route checks the user’s validity through the User Management Module before saving the feedback. Expected response is a success message or error details.
    """
    try:
        res = await project.createFeedback_service.createFeedback(
            professional_id, user_id, content, rating
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post(
    "/bookings",
    response_model=project.createBooking_service.BookingConfirmationResponse,
)
async def api_post_createBooking(
    userId: int, professionalId: int, appointmentTime: datetime
) -> project.createBooking_service.BookingConfirmationResponse | Response:
    """
    Creates a booking for a user with a professional, consulting the Calendar Module to confirm availability. Upon successful booking, it triggers the Notification Module to send confirmation to the user. Requires details of the booking including user ID, professional ID, and time of the appointment.
    """
    try:
        res = await project.createBooking_service.createBooking(
            userId, professionalId, appointmentTime
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.delete(
    "/bookings/{bookingId}",
    response_model=project.deleteBooking_service.DeleteBookingResponse,
)
async def api_delete_deleteBooking(
    bookingId: int,
) -> project.deleteBooking_service.DeleteBookingResponse | Response:
    """
    Deletes a specific booking. Uses the booking ID provided in the path. Upon deletion, it updates the Calendar Module to free up the time slot and notifies the user and professional through the Notification Module.
    """
    try:
        res = await project.deleteBooking_service.deleteBooking(bookingId)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.delete(
    "/availability/{professionalId}",
    response_model=project.deleteAvailability_service.DeleteProfessionalAvailabilityResponse,
)
async def api_delete_deleteAvailability(
    professionalId: int,
) -> project.deleteAvailability_service.DeleteProfessionalAvailabilityResponse | Response:
    """
    Removes a professional's availability status from the system, typically used when a professional is no longer working or needs to be temporarily disabled from the system.
    """
    try:
        res = await project.deleteAvailability_service.deleteAvailability(
            professionalId
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.get(
    "/availability",
    response_model=project.checkAllAvailability_service.FetchAvailabilityResponse,
)
async def api_get_checkAllAvailability(
    request: project.checkAllAvailability_service.FetchAvailabilityRequest,
) -> project.checkAllAvailability_service.FetchAvailabilityResponse | Response:
    """
    Fetches the availability status of all professionals currently registered in the system. Enables administrative or collective views on professional availability.
    """
    try:
        res = await project.checkAllAvailability_service.checkAllAvailability(request)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.get(
    "/availability/{professionalId}",
    response_model=project.getAvailability_service.AvailabilityCheckResponse,
)
async def api_get_getAvailability(
    professionalId: int,
) -> project.getAvailability_service.AvailabilityCheckResponse | Response:
    """
    Retrieves the current availability status of a specified professional. This endpoint will query the current state and return an availability status. Expected to be used frequently to provide real-time updates.
    """
    try:
        res = await project.getAvailability_service.getAvailability(professionalId)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.get(
    "/users/{id}", response_model=project.getUserDetails_service.UserDetailsResponse
)
async def api_get_getUserDetails(
    id: str,
) -> project.getUserDetails_service.UserDetailsResponse | Response:
    """
    Fetches detailed user information for a specific user ID. It requires authentication and is critical for confirming user permissions across modules and delivering personalized alerts. The response includes fields like user's role, status, and registered details.
    """
    try:
        res = await project.getUserDetails_service.getUserDetails(id)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.get("/feedback", response_model=project.listFeedback_service.FeedbackListResponse)
async def api_get_listFeedback(
    professional_id: Optional[int], user_id: Optional[int]
) -> project.listFeedback_service.FeedbackListResponse | Response:
    """
    Lists all feedback entries. Accessible by admins for monitoring or analysis purposes. Can be filtered by professional's ID or user's ID. Returns a list of feedback entries or an empty list if none are found.
    """
    try:
        res = await project.listFeedback_service.listFeedback(professional_id, user_id)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.delete("/users/{id}", response_model=project.deleteUser_service.DeleteUserResponse)
async def api_delete_deleteUser(
    confirmation: bool, id: str, admin_user_id: str, token: str
) -> project.deleteUser_service.DeleteUserResponse | Response:
    """
    This endpoint provides a mechanism for removing a user from the system database. It is restricted to admins and requires a confirmation step through their authenticated session before proceeding with deletion.
    """
    try:
        res = await project.deleteUser_service.deleteUser(
            confirmation, id, admin_user_id, token
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.get(
    "/bookings/{bookingId}",
    response_model=project.getBooking_service.BookingDetailsResponse,
)
async def api_get_getBooking(
    bookingId: int,
) -> project.getBooking_service.BookingDetailsResponse | Response:
    """
    Retrieves information about a specific booking. It uses the booking ID provided in the path. Expected to return details like booking time, professional involved, and user details.
    """
    try:
        res = await project.getBooking_service.getBooking(bookingId)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.delete(
    "/feedback/{feedbackId}",
    response_model=project.deleteFeedback_service.DeleteFeedbackResponse,
)
async def api_delete_deleteFeedback(
    feedbackId: int,
) -> project.deleteFeedback_service.DeleteFeedbackResponse | Response:
    """
    Removes a feedback entry identified by its ID. Restricted to the user who posted the feedback or an admin. The route verifies the user's identity and permission, then deletes the feedback, returning a success or error response.
    """
    try:
        res = await project.deleteFeedback_service.deleteFeedback(feedbackId)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.put(
    "/calendar/appointment/{appointmentId}",
    response_model=project.updateAppointment_service.AppointmentUpdateResponse,
)
async def api_put_updateAppointment(
    appointmentId: int,
    new_time: datetime,
    new_professionalId: Optional[int],
    notes: Optional[str],
) -> project.updateAppointment_service.AppointmentUpdateResponse | Response:
    """
    Provides functionality to update an existing appointment. This could involve changing the time, adding notes, or changing the professional booked. It ensures the changes are synchronized with the Booking Module and updates are reflected in real-time in the Calendar module.
    """
    try:
        res = await project.updateAppointment_service.updateAppointment(
            appointmentId, new_time, new_professionalId, notes
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.delete(
    "/calendar/appointment/{appointmentId}",
    response_model=project.cancelAppointment_service.CancelAppointmentResponse,
)
async def api_delete_cancelAppointment(
    appointmentId: int,
) -> project.cancelAppointment_service.CancelAppointmentResponse | Response:
    """
    Enables users or professionals to cancel an appointment. This will interact with the Booking Module to free up the previously reserved slot and update the professional’s availability status in the Real-Time Status Module.
    """
    try:
        res = await project.cancelAppointment_service.cancelAppointment(appointmentId)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post(
    "/users/register",
    response_model=project.registerUser_service.UserRegistrationResponse,
)
async def api_post_registerUser(
    name: str, email: str, password: str
) -> project.registerUser_service.UserRegistrationResponse | Response:
    """
    This route allows new users to register. It accepts user details such as name, email, and password, then creates a new user record in the database. The response includes a success message and user ID. It utilizes hashing for passwords before storage for security.
    """
    try:
        res = await project.registerUser_service.registerUser(name, email, password)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.get(
    "/calendar/schedule/{professionalId}",
    response_model=project.getProfessionalSchedule_service.FetchScheduleResponse,
)
async def api_get_getProfessionalSchedule(
    professionalId: str, startDate: Optional[date], endDate: Optional[date]
) -> project.getProfessionalSchedule_service.FetchScheduleResponse | Response:
    """
    Fetches the full schedule of a professional for a specific day or range of days. This is useful for both users planning to book and for professionals managing their schedules. The response includes all booked and available time slots, integrating data from both the Booking and Real-Time Status Modules.
    """
    try:
        res = await project.getProfessionalSchedule_service.getProfessionalSchedule(
            professionalId, startDate, endDate
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post(
    "/availability/bulk",
    response_model=project.bulkUpdateAvailability_service.BulkAvailabilityUpdateResponse,
)
async def api_post_bulkUpdateAvailability(
    updates: List[
        project.bulkUpdateAvailability_service.ProfessionalAvailabilityUpdate
    ],
) -> project.bulkUpdateAvailability_service.BulkAvailabilityUpdateResponse | Response:
    """
    Provides a mechanism to set or update the availability for multiple professionals at once. This is particularly valuable in scenarios where a group of professionals need to update their status due to a common event or change.
    """
    try:
        res = await project.bulkUpdateAvailability_service.bulkUpdateAvailability(
            updates
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post(
    "/users/authenticate",
    response_model=project.authenticateUser_service.AuthenticationResponse,
)
async def api_post_authenticateUser(
    email: str, password: str
) -> project.authenticateUser_service.AuthenticationResponse | Response:
    """
    This endpoint handles user authentication. Users submit their email and password, which are validated against the stored credentials. Upon successful authentication, it issues a token (JWT) recognizable for subsequent requests that require authentication.
    """
    try:
        res = await project.authenticateUser_service.authenticateUser(email, password)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post(
    "/notifications/booking",
    response_model=project.sendBookingConfirmation_service.BookingNotificationResponse,
)
async def api_post_sendBookingConfirmation(
    booking_id: int, user_id: int, professional_id: int
) -> project.sendBookingConfirmation_service.BookingNotificationResponse | Response:
    """
    This route handles the sending of booking confirmation notifications to users. It is activated once a booking is successfully made through the Booking Module. The endpoint receives information like booking ID, user ID, and professional ID, and sends a confirmation message detailing the booking date, time, and professional's name.
    """
    try:
        res = await project.sendBookingConfirmation_service.sendBookingConfirmation(
            booking_id, user_id, professional_id
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post(
    "/notifications/availability",
    response_model=project.sendAvailabilityAlert_service.NotificationAvailabilityResponseModel,
)
async def api_post_sendAvailabilityAlert(
    professionalId: int, userId: int, newAvailability: bool
) -> project.sendAvailabilityAlert_service.NotificationAvailabilityResponseModel | Response:
    """
    This endpoint sends alerts to users when there is a change in the availability status of professionals. It is triggered by the Real-Time Status Module. The endpoint accepts data such as professional ID, user ID, and the new availability status. It uses internal logic to send alerts either through email or SMS, based on user preferences.
    """
    try:
        res = await project.sendAvailabilityAlert_service.sendAvailabilityAlert(
            professionalId, userId, newAvailability
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post(
    "/calendar/book",
    response_model=project.bookAppointment_service.CalendarBookingResponse,
)
async def api_post_bookAppointment(
    professionalId: int, userId: int, time: datetime, notes: Optional[str]
) -> project.bookAppointment_service.CalendarBookingResponse | Response:
    """
    Allows a user or professional to book an appointment. This endpoint receives the details of the booking, such as professional ID, user ID, time slot, and optionally any special notes or requirements, then it communicates with the Booking Module to finalize the booking. A successful booking will update the professional's availability both in the Calendar and Real-Time Status Modules.
    """
    try:
        res = await project.bookAppointment_service.bookAppointment(
            professionalId, userId, time, notes
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.put(
    "/feedback/{feedbackId}",
    response_model=project.updateFeedback_service.UpdateFeedbackResponse,
)
async def api_put_updateFeedback(
    feedbackId: int, content: str
) -> project.updateFeedback_service.UpdateFeedbackResponse | Response:
    """
    Allows updates to a specific feedback entry. Only the user who submitted the feedback or an admin can update it. Requires feedback ID and new feedback content. Validates the user’s permission and then updates the entry, returning a success or error message.
    """
    try:
        res = await project.updateFeedback_service.updateFeedback(feedbackId, content)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.put(
    "/users/{id}/role", response_model=project.updateUserRole_service.RoleUpdateResponse
)
async def api_put_updateUserRole(
    id: str, new_role: project.updateUserRole_service.Role
) -> project.updateUserRole_service.RoleUpdateResponse | Response:
    """
    Allows updating the role of a user. Only accessible by admins. This function is essential for role management within the system. It involves a check against the Access Control Module to confirm the admin status before the role update is allowed.
    """
    try:
        res = await project.updateUserRole_service.updateUserRole(id, new_role)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.patch(
    "/availability/{professionalId}",
    response_model=project.updateAvailability_service.AvailabilityUpdateResponse,
)
async def api_patch_updateAvailability(
    professionalId: int, isAvailable: bool, currentActivity: Optional[str]
) -> project.updateAvailability_service.AvailabilityUpdateResponse | Response:
    """
    Allows for partial updates to a professional's availability status. Useful for quick status toggles, like marking a brief break or returning to an available state.
    """
    try:
        res = await project.updateAvailability_service.updateAvailability(
            professionalId, isAvailable, currentActivity
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.get(
    "/availability/{professionalId}",
    response_model=project.checkAvailability_service.ProfessionalAvailabilityResponse,
)
async def api_get_checkAvailability(
    professionalId: int,
) -> project.checkAvailability_service.ProfessionalAvailabilityResponse | Response:
    """
    Checks the real-time availability of a professional via the Calendar Module before booking. It retrieves the professional's schedule and current activities and returns whether they are available. It uses the professional ID provided in the path to fetch data.
    """
    try:
        res = await project.checkAvailability_service.checkAvailability(professionalId)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.get(
    "/feedback/{feedbackId}",
    response_model=project.getFeedback_service.FeedbackDetailsResponse,
)
async def api_get_getFeedback(
    feedbackId: str, role: str
) -> project.getFeedback_service.FeedbackDetailsResponse | Response:
    """
    Fetches details of a specific feedback entry by its ID. It ensures the requester has the right to view the feedback, either by being an admin, the user who created it or the professional it's about. Returns the feedback details if permitted.
    """
    try:
        res = await project.getFeedback_service.getFeedback(feedbackId, role)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.put(
    "/bookings/{bookingId}",
    response_model=project.updateBooking_service.UpdateBookingResponse,
)
async def api_put_updateBooking(
    bookingId: int,
    newTime: Optional[datetime],
    status: project.updateBooking_service.Status,
) -> project.updateBooking_service.UpdateBookingResponse | Response:
    """
    Updates details of an existing booking. It could be updating the time or canceling the booking. Notifies the professional and user of the updated booking details through the Notification Module. Required information includes booking ID and new booking details.
    """
    try:
        res = await project.updateBooking_service.updateBooking(
            bookingId, newTime, status
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )
