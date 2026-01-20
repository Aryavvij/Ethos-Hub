# Ethos Hub: Integrated Life Operating System

### Executive Summary
The Ethos System is a full-stack personal resource planning (PRP) application developed to integrate disparate life-management data into a single, cohesive ecosystem. The developer utilized a modern Python-based stack combined with relational database management to solve the problem of "data fragmentation" in personal productivity. By bridging the gap between backend data architecture and frontend user experience, the system provides a unified interface for health, finance, academics, and deep work.

---

## Technical Implementation Summary

* **Relational Database Integrity:** Powered by a **PostgreSQL** backend. The developer implemented a normalized schema that supports multi-user partitioning through unique identifier keys, ensuring data persistence and secure concurrent sessions.
* **Stateful Multi-Page Routing:** Leveraging **Streamlit’s session state**, the developer engineered a secure authentication layer (SHA-256) and a persistent global sidebar, maintaining user identity across nine independent modules.
* **Custom UI/UX Engineering:** The system utilizes **CSS Injection (Flexbox/Grid)** and **Raw SVG Rendering** to overcome framework limitations. Examples include custom-coded circular progress gauges and absolute-lock grids for visual stability.
* **Asynchronous Data Synchronization:** Advanced "Upsert" logic in the performance and habit modules allows multiple dataframes to be processed and committed in a single transaction, optimizing server-side latency.
* **Advanced Analytics:** Integration of the **Plotly engine** renders interactive sunburst hierarchies and area charts, customized with a unified brand identity for a premium user experience.

---

## System Module Directory

### 1. Ethos Hub (The Dashboard)
* **Purpose:** Serves as the high-level command center and data aggregator.
* **Mechanics:** Uses relational SQL queries to pull "snapshots" of data from other modules based on the current date.
* **Main Feature:** The **Today’s Briefing** box, providing a filtered view of classes, gym splits, and focus goals in one glance.

### 2. Iron Clad (Performance Lab)
* **Purpose:** Tracks physical strength development and progressive overload.
* **Mechanics:** Implements a dual-table architecture: `exercise_library` for Personal Bests and `workout_logs` for session history.
* **Main Feature:** The **Work Capacity Trend**, visualizing "Total Tonnage" (Weight × Reps × Sets) to measure true muscular endurance.



### 3. Neural Lock (Deep Work)
* **Purpose:** Facilitates high-intensity, distraction-free focus sessions.
* **Mechanics:** Utilizes a Python-based stopwatch engine that calculates elapsed time in the app cache before committing to the database.
* **Main Feature:** The **Neural Momentum Graph**, displaying a 30-day area chart of focus minutes to identify peak productivity patterns.

### 4. Academic Trajectory (The Blueprint)
* **Purpose:** Manages long-term strategic initiatives and project milestones.
* **Mechanics:** Uses a hierarchical data structure to organize tasks by Category, Priority, and Timeframe.
* **Main Feature:** The **Interactive Sunburst Map**, providing a 360-degree view of project completion percentages across life domains.



### 5. Weekly Planner (Execution Grid)
* **Purpose:** Handles micro-task management and daily accountability.
* **Mechanics:** Features a 7-column grid with "Absolute Grid Locking" via CSS for symmetrical UI across devices.
* **Main Feature:** **Custom SVG Progress Rings** that dynamically fill as tasks are completed, providing immediate psychological feedback.

### 6. Monthly Events (Calendar)
* **Purpose:** Tracks fixed-date commitments, deadlines, and social obligations.
* **Mechanics:** Generates a dynamic date matrix using the Python `calendar` module to pull events assigned to specific timestamps.
* **Main Feature:** **Status-Based Highlighting**, where pending events are flagged in Red and completed events in Green for a clear visual heat-map.



### 7. Habit Lab (Consistency Tracker)
* **Purpose:** Monitors daily recurring behaviors and atomic habits.
* **Mechanics:** Pivots row-based SQL data into a horizontal monthly grid for efficient mass-updates in a single view.
* **Main Feature:** The **Performance Matrix**, which calculates a daily percentage score of habit completion to visualize "winning" days.

### 8. Financial Hub (Capital Management)
* **Purpose:** Orchestrates personal budgeting, spending analysis, and debt reduction.
* **Mechanics:** Employs aggregate SQL functions (`SUM`, `COALESCE`) to calculate the delta between planned and actual expenditures.
* **Main Feature:** The **Net Debt Tracker**, providing a specialized interface to monitor loan repayments and total financial liability.



### 9. The Pantheon (Knowledge Repository)
* **Purpose:** Acts as a dual-mode archive for structured comparisons and deep-form note-taking.
* **Mechanics:** Features a "Dual-Input" tab system for creating either dynamic ranking tables or markdown-supported text blocks.
* **Main Feature:** The **Universal Search Engine**, which filters through all categories and note titles to find stored knowledge instantly.
