from sqlmodel import Session, func, select

from app.models import Event, Reservation
from app.schemas import EventCreate, ReservationCreate


def get_event(session: Session, event_id: int) -> Event | None:
    return session.get(Event, event_id)


def get_reservation(session: Session, reservation_id: int) -> Reservation | None:
    return session.get(Reservation, reservation_id)


def count_reservations(session: Session, event_id: int) -> int:
    statement = select(func.count()).select_from(Reservation).where(
        Reservation.event_id == event_id
    )
    return session.exec(statement).one()


def create_event(session: Session, event_data: EventCreate) -> Event:
    event = Event(**event_data.model_dump())
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


def update_event(
    session: Session, event: Event, event_data: EventCreate
) -> Event:
    for field, value in event_data.model_dump().items():
        setattr(event, field, value)
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


def create_reservation(
    session: Session, event_id: int, reservation_data: ReservationCreate
) -> Reservation:
    reservation = Reservation(
        event_id=event_id,
        **reservation_data.model_dump(),
    )
    session.add(reservation)
    session.commit()
    session.refresh(reservation)
    return reservation


def get_event_reservations(
    session: Session, event_id: int
) -> list[Reservation]:
    statement = select(Reservation).where(Reservation.event_id == event_id)
    return list(session.exec(statement).all())


def delete_event_reservations(session: Session, event_id: int) -> None:
    reservations = get_event_reservations(session, event_id)
    for reservation in reservations:
        session.delete(reservation)


def delete_record(session: Session, record: Event | Reservation) -> None:
    session.delete(record)
    session.commit()
