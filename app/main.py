from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from sqlmodel import Session, select

from app import crud
from app.database import create_db_and_tables, get_session
from app.models import Event
from app.schemas import (
    AvailabilityRead,
    EventCreate,
    EventRead,
    ReservationCreate,
    ReservationRead,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="College Event & Student Reservation API",
    description="A simple API for managing college events and student reservations.",
    lifespan=lifespan,
)


@app.post(
    "/events",
    response_model=EventRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create an event",
)
def create_event(
    event_data: EventCreate,
    session: Session = Depends(get_session),
) -> EventRead:
    return crud.create_event(session, event_data)


@app.get("/events", response_model=list[EventRead], summary="List all events")
def list_events(session: Session = Depends(get_session)) -> list[EventRead]:
    return list(session.exec(select(Event)).all())


@app.get("/events/{event_id}", response_model=EventRead, summary="Get one event")
def get_event(
    event_id: int,
    session: Session = Depends(get_session),
) -> EventRead:
    event = crud.get_event(session, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@app.put("/events/{event_id}", response_model=EventRead, summary="Update an event")
def update_event(
    event_id: int,
    event_data: EventCreate,
    session: Session = Depends(get_session),
) -> EventRead:
    event = crud.get_event(session, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    booked = crud.count_reservations(session, event_id)
    if event_data.capacity < booked:
        raise HTTPException(
            status_code=400,
            detail="Capacity cannot be less than existing reservations",
        )

    return crud.update_event(session, event, event_data)


@app.delete("/events/{event_id}", summary="Delete an event")
def delete_event(
    event_id: int,
    session: Session = Depends(get_session),
) -> dict[str, str]:
    event = crud.get_event(session, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    crud.delete_event_reservations(session, event_id)
    crud.delete_record(session, event)
    return {"message": "Event deleted successfully"}


@app.post(
    "/events/{event_id}/reserve",
    response_model=ReservationRead,
    status_code=status.HTTP_201_CREATED,
    summary="Reserve a seat",
)
def reserve_seat(
    event_id: int,
    reservation_data: ReservationCreate,
    session: Session = Depends(get_session),
) -> ReservationRead:
    event = crud.get_event(session, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    if event.status == "Closed":
        raise HTTPException(status_code=400, detail="Event is closed")

    booked = crud.count_reservations(session, event_id)
    if booked >= event.capacity:
        raise HTTPException(status_code=409, detail="Event is full. No seats available.")

    return crud.create_reservation(session, event_id, reservation_data)


@app.get(
    "/events/{event_id}/reservations",
    response_model=list[ReservationRead],
    summary="List event reservations",
)
def list_reservations(
    event_id: int,
    session: Session = Depends(get_session),
) -> list[ReservationRead]:
    if crud.get_event(session, event_id) is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return crud.get_event_reservations(session, event_id)


@app.delete("/reservations/{reservation_id}", summary="Cancel a reservation")
def delete_reservation(
    reservation_id: int,
    session: Session = Depends(get_session),
) -> dict[str, str]:
    reservation = crud.get_reservation(session, reservation_id)
    if reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")

    crud.delete_record(session, reservation)
    return {"message": "Reservation deleted successfully"}


@app.get(
    "/events/{event_id}/availability",
    response_model=AvailabilityRead,
    summary="Check event availability",
)
def get_availability(
    event_id: int,
    session: Session = Depends(get_session),
) -> AvailabilityRead:
    event = crud.get_event(session, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    booked = crud.count_reservations(session, event_id)
    return AvailabilityRead(
        capacity=event.capacity,
        booked=booked,
        remaining=event.capacity - booked,
    )
