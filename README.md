# Risk Tracker Application

A web-based tool for tracking project epics, associated risks, and sending email notifications for date change requests.

## Features

- **Epic Management**: Create, view, edit, and delete project epics
- **Risk Tracking**: Add and manage risks associated with each epic
- **Risk Updates**: Add timestamped updates to track risk progress
- **Date Change Requests**: Send formatted email requests to managers for epic date changes
- **Modern Web Interface**: Clean, responsive UI built with modern CSS
- **API Endpoints**: Full REST API for programmatic access

## Technology Stack

- **Backend**: Python FastAPI
- **Database**: SQLite (default) with SQLAlchemy ORM
- **Frontend**: HTML templates with Jinja2, modern CSS, vanilla JavaScript
- **Email**: SMTP with aiosmtplib for async email sending

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example configuration file and update it with your settings:

```bash
cp config.env.example .env
```

Edit `.env` with your email configuration:

```env
# Email Configuration (Required for date change requests)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
MANAGER_EMAIL=manager@company.com
SENDER_EMAIL=noreply@risktracker.com
```

### 3. Run the Application

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The application will be available at: http://localhost:8000

## Usage

### Dashboard
- View overview of all epics
- Quick stats on epic statuses
- Access to create new epics

### Epic Management
- **Create Epic**: Fill in title, description, target launch date, and status
- **View Epic**: See all details including associated risks
- **Edit Epic**: Update any epic information
- **Delete Epic**: Remove epic and all associated risks

### Risk Management
- **Add Risk**: Create risks associated with specific epics
- **Edit Risk**: Update risk description, mitigation plan, or status
- **Risk Updates**: Add timestamped progress updates to risks
- **View Updates**: See chronological history of risk updates

### Date Change Requests
- **Request Date Change**: Send formatted email to manager with:
  - Epic details
  - Current and proposed dates
  - Reason for change
  - Associated risks and their statuses

## API Endpoints

### Epics
- `GET /api/epics` - List all epics
- `POST /api/epics` - Create new epic
- `GET /api/epics/{id}` - Get epic details
- `PUT /api/epics/{id}` - Update epic
- `DELETE /api/epics/{id}` - Delete epic
- `POST /api/epics/{id}/request-date-change` - Send date change request

### Risks
- `POST /api/epics/{id}/risks` - Add risk to epic
- `GET /api/risks/{id}` - Get risk details
- `PUT /api/risks/{id}` - Update risk
- `DELETE /api/risks/{id}` - Delete risk
- `POST /api/risks/{id}/updates` - Add update to risk

## Email Configuration

### Gmail Setup
1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password: Google Account → Security → App passwords
3. Use the app password in the `SMTP_PASSWORD` field

### Other Email Providers
Update the SMTP settings according to your email provider:

- **Outlook**: smtp-mail.outlook.com, port 587
- **Yahoo**: smtp.mail.yahoo.com, port 587
- **Custom SMTP**: Set your server details

## Data Model

### Epic
- Title, Description, Target Launch Date, Actual Launch Date, Status
- Relationships: Has many Risks

### Risk
- Description, Mitigation Plan, Date Added, Status
- Relationships: Belongs to Epic, Has many Risk Updates

### Risk Update
- Update Text, Date Added
- Relationships: Belongs to Risk

## Status Values

### Epic Statuses
- Planned
- In Progress
- Blocked
- Delayed
- Launched
- Cancelled

### Risk Statuses
- Open
- Mitigating
- Mitigated
- Accepted
- Closed

## Development

### Project Structure
```
app/
├── main.py           # FastAPI application
├── models.py         # SQLAlchemy models
├── schemas.py        # Pydantic schemas
├── crud.py          # Database operations
├── database.py      # Database configuration
├── email_service.py # Email functionality
├── static/
│   └── style.css    # Application styles
└── templates/       # HTML templates
    ├── base.html
    ├── index.html
    ├── epic_detail.html
    └── epics_list.html
```

### Running in Development
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Database
The application uses SQLite by default, which creates a file-based database (`risk_tracker.db`) in the project root. For production, you can configure a different database by updating the `DATABASE_URL` environment variable.

## License

This project is part of an MVP implementation for risk tracking and management.

## Contributing

This is an MVP implementation. Future enhancements may include:
- User authentication and authorization
- Jira integration for automatic epic import
- Advanced reporting and dashboards
- File attachments
- Notification systems
- Multi-user support 