# College Event & Student Reservation API

## Project Overview

This project is a beginner-friendly FastAPI REST API for managing college events and student seat reservations. It uses SQLite and SQLModel, with automatic database table creation when the application starts.

## Features

- Create, list, view, update, and delete events.
- Reserve seats only for open events.
- Prevent reservations after an event reaches capacity.
- List and cancel reservations.
- Check booked and remaining seats.
- Validate event fields and student email addresses.
- Explore and test the API through Swagger UI.

## Tech Stack

- Python 3.10+
- FastAPI
- SQLModel
- SQLite
- Uvicorn
- Pydantic and EmailStr

## Folder Structure

```text
event-reservation-api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   └── crud.py
├── screenshots/
│   └── .gitkeep
├── requirements.txt
├── README.md
└── .gitignore
```

The SQLite file `events.db` is generated at runtime and ignored by Git.

## Installation

From this project directory, create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the Application

```bash
uvicorn app.main:app --reload
```

The API is available at `http://127.0.0.1:8000`.

Swagger documentation: `http://127.0.0.1:8000/docs`

## API Endpoints

- `POST /events` - Create an event.
- `GET /events` - List all events.
- `GET /events/{event_id}` - Get one event.
- `PUT /events/{event_id}` - Update an event.
- `DELETE /events/{event_id}` - Delete an event and its reservations.
- `POST /events/{event_id}/reserve` - Create a reservation.
- `GET /events/{event_id}/reservations` - List reservations for an event.
- `DELETE /reservations/{reservation_id}` - Cancel a reservation.
- `GET /events/{event_id}/availability` - Get capacity, booked, and remaining seats.

## Example Request Bodies

Create an event:

```json
{
  "title": "Python Workshop",
  "venue": "Seminar Hall",
  "capacity": 50,
  "organizer": "CSE Department",
  "status": "Open"
}
```

Create a reservation:

```json
{
  "student_name": "Ishan Sharma",
  "roll_number": "CSE123",
  "email": "ishan@example.com"
}
```

## Application Logic

### 1. How do you check whether an event exists before creating a reservation?

The reservation endpoint queries the `Event` table using the requested event ID. If no event is returned, it responds with `404 Event not found` before checking any other reservation rule.

### 2. How do you calculate booked and remaining seats?

The API counts reservations in the `Reservation` table for the event:

```text
booked = count of reservations for the event
remaining = capacity - booked
```

The booked count is always calculated from the database rather than trusted from the client.

### 3. How do you prevent overbooking?

Before inserting a reservation, the API compares the current reservation count with the event capacity. If `booked >= capacity`, it rejects the request with `409 Event is full. No seats available.`

### 4. How do you prevent reservations for closed events?

The event status is checked after confirming that the event exists. If the status is `Closed`, the API rejects the request with a `400 Event is closed` response, even when seats remain.

### 5. How is SQLModel Session used?

FastAPI injects a SQLModel `Session` into each endpoint through the `get_session` dependency. The session is used to query, insert, update, delete, commit, and refresh database records.

When an event is deleted, its reservations are deleted first so orphaned reservations are not left behind. When a reservation is cancelled, the reservation count decreases, so the seat becomes available automatically.

## Proof of Work / Screenshots

Capture these screenshots manually from `/docs` while testing the running application. No screenshots are included or claimed here:

1. `POST /events`
2. `GET /events`
3. Successful `POST /events/{event_id}/reserve`
4. `GET /events/{event_id}/reservations`
5. `GET /events/{event_id}/availability`
6. Successful `DELETE /reservations/{reservation_id}`
7. Failed reservation when the event is full or closed
