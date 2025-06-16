Okay, let's consolidate this into a specification document for the **Risk Tracker Application - MVP (Minimum Viable Product)**.

**Model Activation Profile:** Greenfield Design Profile
**Primary Mental Models:** Jobs To Be Done (JTBD), Systems Thinking, Occam's Razor

---

## Risk Tracker Application - MVP Specification

**Version:** 1.0
**Date:** October 26, 2023
**Focus:** Manual Epic, Risk, and Update Management with Email Notification for Date Change Requests.

**1. Introduction & Purpose**

The Risk Tracker Application (MVP) aims to provide a centralized, simple tool for manually tracking project epics, their associated risks, mitigation plans, and updates. A key feature is the ability to generate and send an email request to a manager for epic launch date changes, including relevant risk information and justification.

This MVP focuses on core manual data entry and tracking to validate the fundamental utility of the tool before incorporating more complex integrations like Jira.

**2. Guiding Principles for MVP**

*   **Simplicity:** Prioritize ease of use and a straightforward workflow.
*   **Core Value First:** Focus on delivering the essential features for manual risk tracking and date change requests.
*   **Iterative Development:** This MVP serves as a foundation for future enhancements (e.g., Jira integration).

**3. Jobs To Be Done (JTBD) - MVP Focus**

*   **JTBD 1 (Epic Tracking):** "When I'm managing projects, I want to manually create and maintain a list of my key epics, including their descriptions, target launch dates, and statuses, so I can have a clear overview of my project roadmap."
*   **JTBD 2 (Risk Logging):** "When new risks emerge for an epic, I want to easily log these risks with their descriptions, mitigation plans, and current status against the relevant epic, so I can keep track of potential impediments."
*   **JTBD 3 (Risk Updates):** "When there's progress or new information regarding a risk, I want to add dated updates to that risk, so I have a chronological record of how the risk is being managed."
*   **JTBD 4 (Date Change Request):** "When an epic's timeline is threatened, I want to quickly compose and send a formal email request for a launch date change to my manager, automatically including epic details, associated risks, and my justification, so that informed decisions can be made efficiently."

**4. Core Features (MVP Scope)**

*   **4.1. Manual Epic Management:**
    *   **4.1.1. Create Epic:**
        *   Input fields: Title (required), Description, Target Launch Date, Status.
        *   System: Saves the new epic to the database.
    *   **4.1.2. View Epic List:**
        *   Display: A list of all created epics, showing key details (e.g., Title, Target Launch Date, Status).
    *   **4.1.3. View Epic Details:**
        *   Display: All information for a selected epic. This view will also serve as the container for associated risks and the "Request Date Change" button.
    *   **4.1.4. Edit Epic:**
        *   Ability to modify all fields of an existing epic.
    *   **4.1.5. Delete Epic:** (Considered essential for MVP for data management)
        *   Ability to remove an epic. Soft delete is preferred if feasible within MVP timeframe, otherwise hard delete.

*   **4.2. Risk Management (per Epic):**
    *   **4.2.1. Add Risk to Epic:**
        *   Context: Within the details view of a specific epic.
        *   Input fields: Description (required), Mitigation Plan, Status.
        *   System: Associates the new risk with the parent epic. `date_added` is automatically set to the current date.
    *   **4.2.2. View Risks for Epic:**
        *   Display: A list of all risks associated with the currently viewed epic (e.g., Description, Status, Date Added).
    *   **4.2.3. Edit Risk:**
        *   Ability to modify all fields of an existing risk.
    *   **4.2.4. Delete Risk:** (Considered essential for MVP)
        *   Ability to remove a risk from an epic.

*   **4.3. Risk Update Logging:**
    *   **4.3.1. Add Update to Risk:**
        *   Context: Within the details/view of a specific risk.
        *   Input fields: Update Text (required).
        *   System: Associates the new update with the parent risk. `date_added` is automatically set to the current date.
    *   **4.3.2. View Updates for Risk:**
        *   Display: A chronological list of all updates for the selected risk (Update Text, Date Added).

*   **4.4. "Request Date Change" Email Functionality:**
    *   **4.4.1. Initiation:** A button/link available on the Epic Details view.
    *   **4.4.2. User Input:**
        *   Field for "Reason for date change request" (required).
        *   (Optional, but recommended) Field for "Proposed New Target Launch Date."
    *   **4.4.3. Email Generation & Sending:**
        *   Recipient: Manager's email address (configured via an environment variable).
        *   Sender: A configured system email address (e.g., `noreply@risktracker.com`).
        *   Subject: Example: "Date Change Request for Epic: [Epic Title]"
        *   Body Content:
            *   Epic Title: [Epic.title]
            *   Current Target Launch Date: [Epic.target_launch_date]
            *   Proposed New Target Launch Date: [User Input, if provided]
            *   Reason for Change: [User Input]
            *   Associated Risks (list format, showing at least Description and Status for each open/relevant risk):
                *   Risk: [Risk.description] - Status: [Risk.status]
                *   Risk: [Risk.description] - Status: [Risk.status]
        *   System: Sends the composed email. Provide feedback to the user (e.g., "Email sent successfully" or "Failed to send email").

**5. Out of Scope for MVP**

*   **Jira Integration:** Fetching epics from Jira.
*   **User Authentication/Authorization:** The MVP assumes a single-user context or a trusted environment.
*   **Advanced Reporting/Dashboards.**
*   **Bi-directional Sync with any external system.**
*   **File Attachments.**
*   **Rich Text Editing for descriptions/updates.**
*   **User-configurable settings (beyond environment variables for email).**

**6. Data Model (Database Schema)**

*   **6.1. `Epics` Table:**
    *   `id` (INTEGER, Primary Key, Auto-incrementing)
    *   `title` (VARCHAR(255), Not Null)
    *   `description` (TEXT, Nullable)
    *   `target_launch_date` (DATE, Nullable)
    *   `actual_launch_date` (DATE, Nullable)
    *   `status` (VARCHAR(50), Not Null)
        *   *Suggested Values:* "Planned", "In Progress", "Blocked", "Delayed", "Launched", "Cancelled" (to be confirmed)
    *   `created_at` (TIMESTAMP, Default CURRENT_TIMESTAMP)
    *   `updated_at` (TIMESTAMP, Default CURRENT_TIMESTAMP, On Update CURRENT_TIMESTAMP)

*   **6.2. `Risks` Table:**
    *   `id` (INTEGER, Primary Key, Auto-incrementing)
    *   `epic_id` (INTEGER, Foreign Key referencing `Epics.id`, Not Null, On Delete CASCADE)
    *   `description` (TEXT, Not Null)
    *   `mitigation_plan` (TEXT, Nullable)
    *   `date_added` (DATE, Not Null, Default CURRENT_DATE)
    *   `status` (VARCHAR(50), Not Null)
        *   *Suggested Values:* "Open", "Mitigating", "Mitigated", "Accepted", "Closed" (to be confirmed)
    *   `created_at` (TIMESTAMP, Default CURRENT_TIMESTAMP)
    *   `updated_at` (TIMESTAMP, Default CURRENT_TIMESTAMP, On Update CURRENT_TIMESTAMP)

*   **6.3. `RiskUpdates` Table:**
    *   `id` (INTEGER, Primary Key, Auto-incrementing)
    *   `risk_id` (INTEGER, Foreign Key referencing `Risks.id`, Not Null, On Delete CASCADE)
    *   `update_text` (TEXT, Not Null)
    *   `date_added` (DATE, Not Null, Default CURRENT_DATE)
    *   `created_at` (TIMESTAMP, Default CURRENT_TIMESTAMP)

**7. High-Level System Design (MVP)**

*   **Frontend (User Interface):** Web-based interface. Can be simple server-rendered HTML pages or a lightweight JavaScript frontend.
*   **Backend (API Server):** Handles all business logic, data persistence, and email sending. Exposes API endpoints for the frontend.
*   **Database:** Relational database (e.g., SQLite for simplicity in MVP, PostgreSQL/MySQL for future growth).
*   **Email Sending Service:** Uses SMTP to send emails. Configuration for SMTP server and credentials will be needed (can be via environment variables).

**8. Technology Stack Considerations (MVP)**

*   A simple, rapidly developable stack is recommended. Examples:
    *   **Python:** Flask or FastAPI with SQLAlchemy (for DB) and Jinja2 (for templating) or a separate JS frontend.
    *   **Node.js:** Express.js with a simple ORM (like Sequelize or Prisma) and EJS (for templating) or a separate JS frontend.
    *   **Ruby:** Ruby on Rails (convention over configuration, good for rapid dev).
    *   **Database:** SQLite is excellent for MVP due to its simplicity (file-based, no separate server needed).
*   The choice should align with developer familiarity and ease of setup.

**9. Key Considerations & Potential Challenges (MVP)**

*   **Email Configuration:** Ensure SMTP settings are correctly configured and securely managed (environment variables are suitable for MVP).
*   **Data Validation:** Implement server-side validation for all inputs (e.g., required fields, date formats).
*   **Error Handling:** Basic error handling for database operations and email sending (e.g., display user-friendly messages).
*   **User Experience (UX):** Even for an MVP, the flow should be intuitive for manual data entry.
*   **Date Handling:** Be consistent with date formats and timezones (if relevant, though for MVP, simple date might suffice).
*   **Security (Basic):** While full authentication is out of scope, basic web security practices (e.g., protection against XSS if rendering user input, CSRF for forms) should be considered if the app is exposed beyond a local machine. For a truly local MVP, this is less critical.

**10. Future Enhancements (Post-MVP)**

*   Jira Integration (Import Epics)
*   User Authentication & Roles
*   Advanced Filtering and Sorting of Epics/Risks
*   Dashboard/Reporting Features
*   Notifications (in-app or other channels)
*   Customizable Fields
*   File Attachments to Risks/Epics

---

**Assumption & Knowledge Gap Register:**

*   **Key Assumptions Made:**
    1.  The MVP is intended for local development/use or a very controlled environment, deferring complex security/user management.
    2.  SQLite is an acceptable database choice for the MVP for simplicity.
    3.  Manager's email and SMTP configuration will be provided via environment variables.
    4.  The suggested `status` values for Epics and Risks are acceptable starting points.
*   **Critical Knowledge Gaps Remaining:**
    1.  **Definitive Technology Stack:** Confirmation of the preferred backend/frontend technologies.
    2.  **Confirmation of Status Values:** Final agreement on the list of allowed string values for `Epic.status` and `Risk.status`.
    3.  **Hosting/Deployment Context (if any for MVP):** If this needs to be accessible beyond the local machine for the MVP phase.

This specification should provide a clear roadmap for developing the MVP of your Risk Tracker application.

**Confidence:** High. This specification clearly defines the MVP based on our discussion.