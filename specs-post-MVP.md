Understood. This is a very logical next step after the MVP and aligns well with how Jira itself is structured. Introducing "Projects" as a way to organize and scope epics makes perfect sense for the Jira import feature.

Let's update the specifications to reflect this post-MVP vision for Jira integration and project-level navigation. I'll add a new section for Post-MVP features, detailing this.

---

## Risk Tracker Application - MVP & Post-MVP Vision

**Version:** 1.1
**Date:** October 26, 2023
**Focus (MVP):** Manual Epic, Risk, and Update Management with Email Notification for Date Change Requests.
**Focus (Post-MVP):** Jira Integration for Epic Import, Project-level Organization and Navigation.

**(Sections 1-5, 7-9 of the MVP Specification remain the same. I will reproduce section 6 (Data Model) and section 10 (Future Enhancements) with modifications and additions for clarity, and add a new section 11 detailing the Post-MVP Jira feature.)**

---

**6. Data Model (Database Schema)**

*   **6.1. `Projects` Table (Post-MVP Introduction):**
    *   `id` (INTEGER, Primary Key, Auto-incrementing)
    *   `jira_project_key` (VARCHAR(100), Unique, Nullable - to allow non-Jira specific projects if ever needed, or for initial manual projects before association)
    *   `name` (VARCHAR(255), Not Null)
    *   `description` (TEXT, Nullable)
    *   `created_at` (TIMESTAMP, Default CURRENT_TIMESTAMP)
    *   `updated_at` (TIMESTAMP, Default CURRENT_TIMESTAMP, On Update CURRENT_TIMESTAMP)

*   **6.2. `Epics` Table (MVP, with Post-MVP modification):**
    *   `id` (INTEGER, Primary Key, Auto-incrementing)
    *   `project_id` (INTEGER, Foreign Key referencing `Projects.id`, Nullable for MVP, **ideally Not Null Post-MVP for imported epics**)
    *   `jira_epic_key` (VARCHAR(100), Unique, Nullable - primarily for Post-MVP Jira imported epics)
    *   `title` (VARCHAR(255), Not Null)
    *   `description` (TEXT, Nullable)
    *   `target_launch_date` (DATE, Nullable)
    *   `actual_launch_date` (DATE, Nullable)
    *   `status` (VARCHAR(50), Not Null)
        *   *Suggested Values:* "Planned", "In Progress", "Blocked", "Delayed", "Launched", "Cancelled"
    *   `created_at` (TIMESTAMP, Default CURRENT_TIMESTAMP)
    *   `updated_at` (TIMESTAMP, Default CURRENT_TIMESTAMP, On Update CURRENT_TIMESTAMP)

*   **6.3. `Risks` Table (MVP - No changes from previous spec):**
    *   `id` (INTEGER, Primary Key, Auto-incrementing)
    *   `epic_id` (INTEGER, Foreign Key referencing `Epics.id`, Not Null, On Delete CASCADE)
    *   `description` (TEXT, Not Null)
    *   `mitigation_plan` (TEXT, Nullable)
    *   `date_added` (DATE, Not Null, Default CURRENT_DATE)
    *   `status` (VARCHAR(50), Not Null)
        *   *Suggested Values:* "Open", "Mitigating", "Mitigated", "Accepted", "Closed"
    *   `created_at` (TIMESTAMP, Default CURRENT_TIMESTAMP)
    *   `updated_at` (TIMESTAMP, Default CURRENT_TIMESTAMP, On Update CURRENT_TIMESTAMP)

*   **6.4. `RiskUpdates` Table (MVP - No changes from previous spec):**
    *   `id` (INTEGER, Primary Key, Auto-incrementing)
    *   `risk_id` (INTEGER, Foreign Key referencing `Risks.id`, Not Null, On Delete CASCADE)
    *   `update_text` (TEXT, Not Null)
    *   `date_added` (DATE, Not Null, Default CURRENT_DATE)
    *   `created_at` (TIMESTAMP, Default CURRENT_TIMESTAMP)

---

**10. Future Enhancements (Post-MVP Phase 1 and Beyond)**

This section is now split to detail the immediate Post-MVP phase (Jira Integration & Projects) and other potential future features.

**(Section 11 below details the primary Post-MVP Phase 1 feature. The following are other enhancements that could follow.)**

*   User Authentication & Roles
*   Advanced Filtering and Sorting of Epics/Risks (beyond project-level)
*   Dashboard/Reporting Features (e.g., risks by status, upcoming epic deadlines)
*   Notifications (in-app or other channels beyond initial email)
*   Customizable Fields for Epics or Risks
*   File Attachments to Risks/Epics
*   Rich Text Editing for descriptions/updates
*   Bi-directional Jira Sync (more complex: updating Jira from this tool)
*   User-configurable settings via UI (e.g., manager email, Jira connection details if not solely by admin)

**11. Post-MVP Phase 1: Jira Integration & Project Organization**

This will be the first major feature addition after the MVP is stable.

*   **11.1. Project Entity Implementation:**
    *   Implement the `Projects` table as defined in section 6.1.
    *   Modify the `Epics` table to include `project_id` and `jira_epic_key` as per section 6.2.
    *   Provide UI for viewing a list of Projects.
    *   Provide UI for viewing details of a Project (which would typically list its associated Epics).
    *   (Optional) Allow manual creation/editing of Projects in the Risk Tracker.

*   **11.2. Jira Integration for Epic Import:**
    *   **11.2.1. Configuration:**
        *   Secure mechanism to store Jira connection details (URL, API Token/Credentials). This might be admin-configured or user-specific depending on how user accounts are handled by then.
    *   **11.2.2. Import Process:**
        *   User Interface (UI) element (e.g., "Import from Jira" button).
        *   User specifies the Jira Project Key from which to import epics.
        *   Backend logic connects to the Jira API and fetches epics for the specified Jira Project.
        *   For each fetched Jira epic:
            1.  **Project Matching/Creation:**
                *   The system checks if a `Project` entity already exists in the local database matching the Jira Project Key.
                *   If not, a new `Project` record is created in the Risk Tracker (using Jira Project Key and Name).
            2.  **Epic Upsert:**
                *   The system checks if the Jira epic (identified by `jira_epic_key`) already exists in the Risk Tracker's `Epics` table.
                *   If it exists, update its details (Title, Description, Status, Target Launch Date if available/mapped from Jira). Handle potential conflicts or provide options (e.g., overwrite, skip).
                *   If it does not exist, create a new `Epic` record, linking it to the corresponding `Project` (from step 11.2.2.1) and storing its `jira_epic_key`.
                *   Map relevant Jira epic fields (e.g., Summary -> Title, Description -> Description, Due Date -> Target Launch Date, Status -> Status).
    *   **11.2.3. User Feedback:** Provide clear feedback on the import process (e.g., "X epics imported/updated from project Y", error messages for failures).

*   **11.3. UI Enhancements for Project Navigation:**
    *   **11.3.1. Project Selection/Filtering:**
        *   Allow users to view all epics or filter/navigate to epics belonging to a specific project. This could be a dropdown, a sidebar list of projects, or a dedicated "Projects" page leading to epic lists.
    *   **11.3.2. Linking Manual Epics to Projects (Migration/Utility):**
        *   Provide a mechanism for users to associate manually created MVP epics (which initially won't have a `project_id`) with existing or newly created Projects.

**Impact of Project Introduction:**

*   The primary view of epics might change from a single flat list to a project-scoped list or a list filterable by project.
*   The "Request Date Change" email might also benefit from including the Project Name for context.

---

**Assumption & Knowledge Gap Register (Updated):**

*   **Key Assumptions Made:**
    1.  The MVP is successfully built and stable before starting Post-MVP work.
    2.  For Post-MVP Jira import, a Project in the Risk Tracker will typically map 1:1 to a Jira Project.
    3.  Users will have the necessary Jira API access and permissions to fetch epics from their Jira projects.
    4.  The primary goal of projects in the Risk Tracker is organization and scoping of epics, especially those from Jira.
*   **Critical Knowledge Gaps Remaining (for Post-MVP planning):**
    1.  **Jira Instance Details:** Specifics of the Jira instance (Cloud/Server, API version) will influence library choice and API call details.
    2.  **Jira Field Mapping:** Precise mapping required between Jira epic fields and Risk Tracker epic fields (e.g., how Jira statuses map to local statuses).
    3.  **Conflict Resolution Strategy for Import:** How to handle cases where an epic from Jira already exists locally – overwrite, skip, or merge?
    4.  **Handling of Epics Not in Jira:** If the tool will continue to support "standalone" epics not tied to a Jira project, or if all epics must eventually be linked to some project (even a "General" or "Internal" one). The current schema allows `project_id` to be nullable, supporting this flexibility initially.

This expanded specification now clearly outlines the MVP and the immediate, significant Post-MVP feature of Jira import with project organization. This iterative approach (MVP first, then major features) is key to managing complexity and delivering value incrementally (**Iterative Development**, **Divide and Conquer**).

**Confidence:** High. The Post-MVP vision described clearly builds upon the MVP and addresses the Jira import requirement with project context.