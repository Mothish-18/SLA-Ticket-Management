# 🎫 Enterprise Operations & SLA Ticket Management Engine

A full-stack Django application for managing support tickets with automated SLA (Service Level Agreement) tracking, role-based access control, real-time notifications, and a REST API.

## Overview

This project simulates a real-world enterprise ticketing system (similar to Zendesk/Freshdesk) where customers raise issues, support engineers resolve them, and admins oversee the entire operation — all while the system automatically tracks SLA response/resolution deadlines and flags breaches.

## Features

- **Role-Based Access Control** — Three distinct roles (Administrator, Support Engineer, Employee) with separate dashboards and permissions
- **Ticket Lifecycle Management** — Create, assign, update, and track tickets through Open → In Progress → On Hold → Resolved → Closed
- **SLA Policy Engine** — Configurable response/resolution time targets per priority level (Low/Medium/High/Critical), with automatic breach detection
- **Ticket History Tracking** — Full audit trail of every status change, who made it, and when
- **Comments & Collaboration** — Threaded comments on tickets between customers and engineers
- **Real-Time Notifications** — In-app notifications for ticket creation, assignment, status changes, and new comments
- **Dashboard Analytics** — Live counts of open/resolved/breached tickets, priority breakdown, filtered by role
- **Search & Filtering** — Filter tickets by status, priority, and SLA breach state
- **REST API** — Full API layer built with Django REST Framework, secured with JWT authentication

## Tech Stack

- **Backend:** Python, Django
- **Database:** MySQL
- **API:** Django REST Framework, Simple JWT
- **Frontend:** Django Templates, HTML/CSS

## Project Structure

SLA_Ticket_Management/
├── config/ # Project settings, URLs, WSGI/ASGI
├── Tickets/
│ ├── models.py # Ticket, SLAPolicy, TicketHistory, TicketComment, Notification
│ ├── views.py # Dashboard, ticket CRUD, auth views
│ ├── forms.py
│ ├── services.py # SLA breach calculation logic
│ ├── utils.py
│ ├── context_processors.py
│ └── API/ # DRF viewsets, serializers, permissions
├── templates/ # HTML templates
└── manage.py


## Getting Started

### Prerequisites
- Python 3.10+
- MySQL Server

### Installation

1. **Clone the repository**
```bash
   git clone https://github.com/Mothish-18/SLA-Ticket-Management.git
   cd SLA-Ticket-Management
```

2. **Create and activate a virtual environment**
```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
   pip install -r requirements.txt
```

4. **Set up environment variables**

   Create a `.env` file in the project root:

   SECRET_KEY=your-secret-key-here
    DEBUG=True
    DB_NAME=SLA_Project_Database
    DB_USER=root
    DB_PASSWORD=your-db-password
    DB_HOST=localhost
    DB_PORT=3306


5. **Create the MySQL database**
```sql
   CREATE DATABASE SLA_Project_Database;
```

6. **Run migrations**
```bash
   python manage.py migrate
```

7. **Create user groups** (via Django admin or shell)
   - Admin
   - Support Engineer
   - Customer

8. **Create a superuser**
```bash
   python manage.py createsuperuser
```

9. **Run the development server**
```bash
   python manage.py runserver
```

   Visit `http://127.0.0.1:8000`

## API Endpoints

| Endpoint | Description |
|---|---|
| `POST /token/` | Obtain JWT access/refresh token pair |
| `POST /token/refresh/` | Refresh access token |
| `GET/POST /api/tickets/` | List/create tickets |
| `GET/POST /api/comments/` | List/create comments |
| `GET /api/history/` | Ticket status change history |
| `GET /api/dashboard/` | Dashboard summary stats |

## Roadmap / Future Improvements

- Email notifications (currently console backend only)
- Automated SLA escalation for near-breach tickets
- Docker containerization
- CI/CD pipeline
