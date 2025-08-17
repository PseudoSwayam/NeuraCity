# 🏛️ NeuraCity Admin Dashboard: The Command Center

> This document is the official technical specification and developer guide for the NeuraCity Admin Dashboard frontend application.

---

## 1. **Project Vision & Purpose**

The NeuraCity Admin Dashboard is the **"single pane of glass"** for campus administrators and security personnel. It is a secure, real-time web application that provides complete situational awareness and control over the entire NeuraCity ecosystem.

This dashboard will consume data from all backend modules (`UserHub`, `InsightCloud`, `Alerts & Notifications`) to create a powerful, intuitive, and visually breathtaking command center.

## 2. **Core Architectural Requirements**

*   **Technology Stack**: `Vue.js 3` (or `React`/`Angular`) with `Vite` for the build system.
*   **Authentication**: The entire application must be protected. All data-fetching must be done using a **JWT Bearer Token** obtained from the `UserHub` login endpoint.
*   **Real-Time by Default**: The dashboard must feel alive. It will establish a persistent, authenticated **WebSocket** connection to the `alerts_and_notifications` service to receive and display events the instant they occur.
*   **Role-Based Access Control (RBAC)**: The UI itself must be "role-aware." Components, pages, or even specific buttons should be hidden or disabled based on the logged-in user's role (e.g., a `security` user cannot see user management settings).

---

## 3. **Step-by-Step Feature Implementation Guide**

This section breaks down the dashboard into its core pages and features, detailing the backend integrations required for each.

### **Page 1: The Login Screen**

*   **UI Components:**
    *   Email Input Field
    *   Password Input Field
    *   "Login" Button
*   **Core Logic:**
    1.  On form submission, make a `POST` request to the **`UserHub`** service at `http://localhost:8005/auth/token`.
    2.  The request body should be `application/x-www-form-urlencoded` with `username` and `password` fields.
    3.  On a successful (`200 OK`) response, the frontend will receive a JSON object containing an `access_token`.
    4.  **Crucially, this `access_token` must be securely stored** in the browser's local storage or a secure state management store (like Pinia/Vuex).
    5.  The user should then be redirected to the main dashboard `/`.
    6.  On a failed (`401 Unauthorized`) response, an "Invalid credentials" error should be displayed.

---

### **Page 2: The Main Dashboard / Live View (`NeuroMap`)**

This is the default view after login. It is dominated by the `NeuroMap`, which is the visual cortex of the platform.

#### **Feature 2.1: Real-Time WebSocket Connection**

*   **Core Logic:**
    1.  Immediately after the user is authenticated, the frontend application must establish a WebSocket connection.
    2.  The URL for the connection is `ws://localhost:8003/ws/alerts`.
    3.  **Crucially, the JWT `access_token` must be passed as a query parameter** to authenticate the connection:
        `ws://localhost:8003/ws/alerts?token=eyJhbGciOiJIUzI1Ni...`
    4.  A status indicator on the UI should show a "Connecting..." state, which turns to a green "Live" when the connection is successful (`onopen` event).
    5.  Robust reconnection logic (`onclose` event) must be implemented to automatically re-establish the connection if it drops.

#### **Feature 2.2: The Interactive `NeuroMap`**
*   This feature is already a complete, standalone module in `modules/neuromap/`. The dashboard will essentially be the "shell" that contains this map.
*   **Core Logic:**
    1.  The dashboard will render the `App.vue` component from the `neuromap` project.
    2.  The `onmessage` handler for the WebSocket will receive incoming alert payloads.
    3.  The frontend logic (as defined in `neuromap/frontend/src/App.vue`) will:
        *   Check if the `event_type` is on the "map-worthy" whitelist.
        *   If it is, it will use the `location` data to place a new, animated, pulsing marker on the Leaflet map.
        *   The map's camera will smoothly "fly to" the location of the new event.

#### **Feature 2.3: The Live Alert Banner & Feed**
*   **UI Components:**
    *   A persistent "toast" or banner at the bottom/top of the screen.
    *   (Optional) A sidebar or scrollable list showing the last 10-20 alerts.
*   **Core Logic:**
    1.  The WebSocket `onmessage` handler will take the `human_readable_message` from the alert payload.
    2.  This message will be displayed in the live alert banner for a few seconds.
    3.  The same message will be added to the top of the persistent alert feed.

---

### **Page 3: The Analytics Dashboard (`InsightCloud`)**

This page is dedicated to historical data, charts, and system health. All API calls to this page must include the `Authorization: Bearer <token>` header.

#### **Feature 3.1: System Health Overview**
*   **UI Components:** A simple status panel showing a list of all backend modules (`neuranlp_agent`, `cv_watchtower`, etc.) with a colored dot (Green for Healthy, Red for Unhealthy, Grey for Unknown) next to each.
*   **Core Logic:**
    1.  The frontend will make a `GET` request to the **`InsightCloud`** service at `http://localhost:8002/stats/module_health`.
    2.  This call should be made on page load and then **repeated on a timer** (e.g., every 30 seconds) to keep the status live.
    3.  The UI will dynamically update the color of the status dots based on the `"status"` field in the JSON response.

#### **Feature 3.2: Event Analytics Charts**
*   **UI Components:**
    *   A bar chart titled "Events Per Day".
    *   A pie chart titled "Events by Source Module".
*   **Core Logic (Events Per Day):**
    1.  Make a `GET` request to `http://localhost:8002/stats/events_per_day`.
    2.  The response will be a JSON object like `{"2025-08-12": 50, "2025-08-13": 75}`.
    3.  Use a charting library (like Chart.js or ECharts) to render this data as a bar chart.
*   **Core Logic (Events by Module):**
    1.  Make a `GET` request to `http://localhost:8002/stats/events_by_module`.
    2.  The response will be a JSON object like `{"cv_watchtower": 310, "reflex_system": 303}`.
    3.  Use a charting library to render this data as a pie chart.

#### **Feature 3.3: Anomaly Feed**
*   **UI Components:** A simple list or feed showing any detected system anomalies.
*   **Core Logic:**
    1.  Make a `GET` request to `http://localhost:8002/stats/anomalies`.
    2.  Display the results, which will highlight time periods with unusually high event traffic.

---

### **Page 4: User Management (Superadmin Only)**

This page demonstrates the RBAC functionality of `UserHub`.

*   **UI Components:** A table displaying all users, a "Create New User" form.
*   **Core Logic:**
    1.  **RBAC Check:** The frontend will first check the logged-in user's token. If the user's role is not `superadmin`, this page/link in the navigation bar **should not be visible at all.**
    2.  **Fetch Users:** If the user is a superadmin, make a `GET` request to `http://localhost:8005/users/` (with the Auth header) to get the list of all users and populate the table.
    3.  **Create User:** The "Create User" form will make a `POST` request to `http://localhost:8005/users/` with the new user's details.

This guide provides a complete, feature-by-feature roadmap for building a spectacular and fully functional frontend that perfectly leverages the power of your NeuraCity backend.
