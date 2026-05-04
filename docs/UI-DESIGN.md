# User Flow — Zeus

---

[Back to main README](../README.md#date-sprint-backlog)

---

## 🎯 Purpose of This Document

This document describes the complete flow of the **Zeus** application — ANEEL Data Analysis Platform — detailing each screen, its components, available actions and associated business rules.

---

## 🗺️ Flow Overview

```
Login
  ├── First Access (new user)
  │     ├── Step 1 — Set Password
  │     └── Step 2 — Accept Terms
  └── Existing user
        └── Dashboard
              ├── Heatmap
              ├── DEC/FEC Indicators
              │     ├── DEC/FEC Tab
              │     └── Losses Tab
              ├── Network Structure
              ├── User Management
              │     ├── Create User
              │     ├── Edit User
              │     └── Delete User
              ├── Terms Management
              │     ├── Create Term
              │     ├── Edit Term
              │     └── Delete Draft
              └── My Profile
```

---

## 1. Login

**Route:** `/login`  
**Access:** Public

### Description

The platform's initial screen. The user enters their credentials to access the system.

![Login](/image/figma/login.png)

### Components

| Element | Description |
|:--------|:------------|
| Logo + Name | Centered Zeus icon with subtitle "ANEEL Data Analysis Platform" |
| Email Field | Text input with placeholder `your@email.com` |
| Password Field | Password input with visibility toggle (eye icon) |
| "Remember me" Checkbox | Keeps the session active between accesses |
| "Forgot password?" Link | Redirects to the password recovery flow |
| "Sign In" Button | Submits credentials for authentication |
| Footer | "Tecsys do Brasil - All rights reserved" |

### User Actions

- Fill in email and password and click **Sign In**
- Check "Remember me" for a persistent session
- Click "Forgot password?" to recover access

### Business Rules

- Credentials validated via PostgreSQL (sensitive data/LGPD)
- If it is the user's **first access**, redirects to the First Access flow
- If credentials are valid and the user has completed registration, redirects to the **Dashboard**

---

## 2. First Access

**Route:** `/first-access`  
**Access:** Users with pending registration (created by the administrator)

**2 mandatory steps** before accessing the system.

---

### 2.1 Step 1 — Set Password

### Description

The user sets their access password. The system displays the requirements in real time as the password is typed.

![First Access - Step 1](/image/figma/first-access-1.png)

### Components

| Element | Description |
|:--------|:------------|
| Stepper (1 → 2) | Progress indicator with step 1 active |
| "New Password" Field | Password input with visibility toggle |
| Requirements Checklist | Real-time validation: minimum 8 characters, lowercase letter, uppercase letter, number, special character |
| "Confirm Password" Field | Password confirmation with visibility toggle |
| "Continue" Button | Advances to Step 2 (enabled only when all requirements are met) |

### Business Rules

- The "Continue" button remains disabled until all 5 password requirements are met and the passwords match
- The password is stored encrypted in PostgreSQL

---

### 2.2 Step 2 — Accept Terms

### Description

The user reads and accepts the mandatory terms before completing registration.

![First Access - Step 2](/image/figma/first-access-2.png)

### Components

| Element | Description |
|:--------|:------------|
| Stepper (✓ → 2) | Step 1 marked as complete, step 2 active |
| "Terms of Use" Accordion | Expandable for full document reading |
| "I have read and accept the Terms of Use" Checkbox | Mandatory confirmation |
| "Privacy Policy (LGPD)" Accordion | Expandable for full document reading |
| "I have read and accept the Privacy Policy" Checkbox | Mandatory confirmation |
| "Back" Button | Returns to Step 1 |
| "Complete Registration" Button | Finishes onboarding and redirects to Dashboard (enabled only when both checkboxes are checked) |

### Business Rules

- The terms displayed are from the most recent **active** version registered in Terms Management
- Acceptance is recorded with date/time and linked to the user (LGPD audit)
- The "Complete Registration" button is only enabled when **both** documents have been accepted
- After completion, the user is redirected to the **Dashboard**

---

## 3. Dashboard

**Route:** `/dashboard`  
**Access:** All authenticated profiles

### Description

Consolidated overview of the system's main indicators. First destination after login.

![Dashboard](/image/figma/dashboard-1.png)
![Dashboard](/image/figma/dashboard-2.png)

### Components

| Element | Description |
|:--------|:------------|
| "Total Distributors" Card | Total number of active distributors with variation vs. previous period |
| "Average DEC Index" Card | National average DEC in hours with percentage variation |
| "Average FEC Index" Card | National average FEC in interruptions/consumer with percentage variation |
| "Critical Areas" Card | Number of regions in critical state with variation vs. previous period |
| "Recent Activity" Panel | List of the latest occurrences recorded by region with status (Critical / Alert / Normal) |
| "Top Regions" Panel | Ranking of regions with the highest number of distributors showing DEC and FEC per region |
| Side menu | Global navigation: Dashboard, Heatmap, DEC/FEC Indicators, Network Structure, User Management, Terms Management |
| Avatar + username | Top right corner with profile menu |

### User Actions

- View general indicators
- Navigate to any module via the side menu
- Access "My Profile" via the avatar in the top right corner

---

## 4. Heatmap

**Route:** `/heatmap`  
**Access:** All authenticated profiles

### Description

Geographic visualization of quality indicators by Brazilian state, with an interactive map colored by criticality level.

![Heatmap](/image/figma/heatmap.png)

### Components

| Element | Description |
|:--------|:------------|
| Indicator tabs | View filters: **DEC**, **FEC**, **Losses**, **Criticality** |
| Brazil Map | Interactive map with states colored by level: 🔴 High, 🟠 Medium, 🟢 Low |
| Criticality legend | Displayed over the map |
| Hover tooltip | Shows state, region, DEC, FEC and criticality level on mouse over |
| Side panel — Selected state | Shows details of the clicked state: Region, Criticality, DEC, FEC and "View Details" button |
| "All States" List | Scrollable side panel listing all states with their DEC values |
| "Advanced Filters" Button | Opens additional filters |
| "Export" Button | Exports the current visualization |
| Zoom controls | `+` and `–` buttons on the map |

### User Actions

- Switch between DEC / FEC / Losses / Criticality tabs
- Click on a state to see its details in the side panel
- Hover over a state to see a quick tooltip
- Click "View Details" to deepen the analysis
- Use advanced filters to segment the visualization
- Export the displayed data

---

## 5. DEC/FEC Indicators

**Route:** `/indicators`  
**Access:** All authenticated profiles

Page with **2 tabs**: DEC/FEC and Losses.

---

### 5.1 DEC/FEC Tab

### Description

Detailed analysis of electricity continuity indicators with history and distributor ranking.

![DEC/FEC Indicators](/image/figma/indicators-1.png)
![DEC/FEC Indicators - Ranking](/image/figma/indicators-2.png)

### Components

| Element | Description |
|:--------|:------------|
| Period selector | Quick filters: 7 days, 30 days, 90 days, 1 year, Custom |
| "National Average DEC" Card | Current value in hours with variation vs. previous period |
| "National Average FEC" Card | Current value with variation vs. previous period |
| "Compliant Distributors" Card | Number within the target (e.g. 38/53) with variation |
| "Active Alerts" Card | Number of red alerts with variation |
| "DEC/FEC Evolution" Chart | Dual line chart (DEC in blue, FEC in green) with last 6 months history |
| "Distribution by Status" Chart | Donut chart with total distributors and legend: Compliant (blue), Alert (orange), Critical (red) |
| "Distributor Ranking" Table | Columns: Distributor, DEC, DEC Target, FEC, FEC Target, Status — sortable and filterable |
| "Filter" Button | Filters on the ranking table |
| "Export" Button | Exports the displayed data |

### User Actions

- Select analysis period
- Analyze temporal evolution via the line chart
- Filter and sort the distributor ranking
- Export data

---

### 5.2 Losses Tab

### Description

Analysis of technical and non-technical losses from distributors compared to regulatory targets.

![Indicators - Losses](/image/figma/loss-indicators.png)

### Components

| Element | Description |
|:--------|:------------|
| Period selector | Same behavior as the DEC/FEC tab |
| "Technical Losses" Card | Current percentage with target and progress bar (blue = below target ✅) |
| "Non-Technical Losses" Card | Current percentage with target and progress bar (red = above target ⚠️) |
| "Total Losses" Card | Percentage sum with target and status indicator |
| "Loss Evolution" Chart | Dual line (Technical Losses in blue, Non-Technical in red) with monthly history |
| "Export" Button | Exports the displayed data |

### Business Rules

- Losses calculated from BDGD layers `CTMT`, `UNTRAT` and `UNTRMT`
- Progress bar colors indicate compliance: blue = below target, red = above target

---

## 6. Network Structure

**Route:** `/network-structure`  
**Access:** All authenticated profiles

### Description

Visualization of the physical electrical grid infrastructure by region, with an asset list and a details panel when selecting an item.

![Network Structure](/image/figma/networks-1.png)
![Network Structure - Details](/image/figma/networks-2.png)

### Components

| Element | Description |
|:--------|:------------|
| "Substations" Card | Total registered substations |
| "Transformers" Card | Total registered transformers |
| "Operational" Card | Total assets with operational status |
| "On Alert" Card | Total assets in alert state |
| Search bar | Search by asset name or code |
| "All Regions" Filter | Dropdown to filter by geographic region |
| "All Types" Filter | Dropdown to filter by asset type (Substation, Transformer) |
| "All Status" Filter | Dropdown to filter by status (Operational, Maintenance, Alert) |
| "Network Assets" Table | Columns: Asset, Region, Voltage, Status (colored badge), Load (progress bar + %) |
| Details side panel | Opens on asset click: Status, Location, Voltage, MVA, Current Load, Temperature, Transformers, Feeders, Maintenance (last and next) |
| "View History" Button | Accesses the asset's maintenance history |
| "View on Map" Button | Opens the asset location on the Heatmap |
| "Refresh" Button | Reloads the listing data |
| "Export" Button | Exports the asset listing |

### User Actions

- Search for an asset by name or code
- Filter by region, type and status
- Click on an asset to open the details panel
- Close the panel with the `×` button
- View history or location on the map from the details panel

### Business Rules

- Data sourced from BDGD layers `SUB`, `UNTRAT`, `UNTRMT` and `SSDAT`
- Status displayed with badges: 🔵 Operational, 🟡 Under Maintenance, 🔴 Alert
- Load displayed as a color-coded progress bar (green → yellow → red based on value)

---

## 7. User Management

**Route:** `/user-management`  
**Access:** **Administrator** profile only (restricted)

### Description

Complete user management with LGPD compliance.

---

### 7.1 User Listing

### Components

![User Management](/image/figma/user.png)

| Element | Description |
|:--------|:------------|
| "Total Users" Card | Total count of registered users |
| "Active Users" Card | Count of users with Active status |
| "Inactive Users" Card | Count of users with Inactive status |
| Search bar | Search by name or email |
| "User List" Table | Columns: Avatar+Name, Email, Profile (badge), Status (badge), Last Access, Actions (edit/delete) |
| "+ New User" Button | Opens the registration modal |

### Available Access Profiles

| Profile | Badge |
|:--------|:------|
| Administrator | Dark blue |
| Analyst | Green |
| Viewer | Gray |

---

### 7.2 Create User (Modal)

### Components

![Create User](/image/figma/user-registration.png)

| Element | Description |
|:--------|:------------|
| "Full Name" Field | Required text input |
| "Email" Field | Required email input |
| "Access Profile" Dropdown | Profile selection: Administrator, Analyst or Viewer |
| "Cancel" Button | Closes the modal without saving |
| "Create User" Button | Saves the new user |

### Business Rules

- The created user receives an email with a first access link
- Registration does not include a password — it will be set by the user during **First Access**
- Data stored in PostgreSQL

---

### 7.3 Edit User (Modal)

### Components

![Edit User](/image/figma/user-edit.png)

| Element | Description |
|:--------|:------------|
| "Full Name" Field | Pre-filled, editable |
| "Email" Field | Pre-filled, editable |
| "Access Profile" Dropdown | Profile change |
| "Status" Dropdown | Status change: Active / Inactive |
| "Cancel" Button | Closes without saving |
| "Save Changes" Button | Persists the changes |

---

### 7.4 Delete User (Confirmation Modal)

### Components

![Delete User](/image/figma/user-delete.png)

| Element | Description |
|:--------|:------------|
| Warning icon | Red warning triangle |
| Confirmation message | Displays the name of the user to be deleted and a warning that all associated data will be permanently removed |
| "Cancel" Button | Closes without deleting |
| "Delete User" Button | Confirms and performs the permanent deletion |

### Business Rules

- Deletion is permanent and irreversible
- All data associated with the user is removed

---

## 8. Terms Management

**Route:** `/terms-management`  
**Access:** **Administrator** profile only (restricted)

### Description

Management of terms of use and privacy policies displayed in the First Access flow and re-displayed to users when active versions are updated.

---

### 8.1 Terms Listing

### Components

![Terms Management](/image/figma/terms-1.png)
![Terms Management - Acceptance History](/image/figma/terms-2.png)

| Element | Description |
|:--------|:------------|
| "Active Terms" Card | Number of published and active terms |
| "Drafts" Card | Number of terms saved as draft |
| "Inactive" Card | Number of deactivated terms |
| "Users Who Accepted" Card | Total accumulated acceptances recorded |
| Filter tabs | All / Active / Inactive / Drafts |
| Search bar | Search by type or description |
| Terms table | Columns: Type, Version, Status (badge), Required (badge), Publication Date, Description, Actions (view / edit / delete) |
| "Recent Acceptance History" Panel | List of the latest users who accepted terms with email, accepted version and date/time |
| "+ New Term" Button | Opens the registration modal |

### Term Statuses

| Status | Badge | Available Actions |
|:-------|:------|:-----------------|
| Active | 🔵 Active | View, Edit |
| Inactive | ⚫ Inactive | View |
| Draft | 🟡 Draft | View, Edit, Delete |

---

### 8.2 Create Term (Modal)

### Components

![Create Term](/image/figma/terms-register.png)

| Element | Description |
|:--------|:------------|
| "Type" Field | Pre-selected: "Terms of Use" or "Privacy Policy (LGPD)" |
| "Version" Field | Text input (e.g. 1.0, 2.0) |
| "Description" Field | Brief description of changes |
| "Term Acceptance" | Radio button: **Required** (user must accept to continue) or **Optional** (user may decline) |
| "Term Content" Field | Textarea for the full document content |
| "Cancel" Button | Closes without saving |
| "Save Draft" Button | Saves as draft (not yet shown to users) |
| "Publish Term" Button | Publishes the term as active (previous version is automatically deactivated) |

---

### 8.3 Edit Term (Modal)

Same layout as the creation modal, with fields pre-filled. Available only for terms with **Draft** or **Active** status.

![Edit Term](/image/figma/user-edit.png)

| Button | Action |
|:-------|:-------|
| Cancel | Closes without saving |
| Save Changes | Persists the modifications |

---

### 8.4 Delete Draft (Confirmation Modal)

> ⚠️ Only drafts can be deleted. Active and inactive terms do not have the delete option.

### Components

![Delete Draft](/image/figma/terms-delete.png)

| Element | Description |
|:--------|:------------|
| Warning icon | Red warning circle |
| Confirmation message | Displays the type and version of the draft to be deleted ("This action cannot be undone") |
| "Cancel" Button | Closes without deleting |
| "Delete" Button | Confirms and permanently removes the draft |

---

## 9. My Profile

**Route:** `/profile`  
**Access:** All authenticated profiles

### Description

Allows the user to view and update their personal data. Accessed via the avatar/name in the top right corner of the navigation bar.

![My Profile](/image/figma/profile.png)

### Components

| Element | Description |
|:--------|:------------|
| Avatar with initials | Displayed with the user's name initials |
| Full name | Displayed below the avatar |
| Email | User's email |
| Profile badge | User's access type (e.g. Administrator) |
| "Full Name" Field | Editable |
| "Email" Field | Editable |
| "Phone" Field | Editable |
| "Job Title" Field | Editable |
| "Department" Field | Editable |
| "Access Profile" Field | Read-only (managed by the Administrator) |
| "Account created on" Info | Account creation date |
| "Last access on" Info | Date and time of the last recorded login |
| "Save Changes" Button | Persists the edited information |

### Business Rules

- The **Access Profile** field is read-only — profile changes can only be made by an Administrator via User Management
- Data saved in PostgreSQL

---

## 📎 General Notes

- **System:** Zeus — ANEEL Data Analysis Platform
- **Company:** Tecsys do Brasil
- **Navigation:** Fixed side menu available on all authenticated screens
- **Responsiveness:** Interface compatible with modern browsers (RNF03)
- **LGPD:** User data (credentials, acceptances, profiles) stored exclusively in PostgreSQL; BDGD operational data in MongoDB
- **Existing access profiles:** Administrator, Analyst, Viewer

---

*Last updated: 03/17/2026*