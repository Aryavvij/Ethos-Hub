# Ethos Hub: Integrated Life Operating System

## The Purpose: The "All-in-One" Life Operating System
The **Ethos System** was engineered to eliminate **App Fatigue** and **Data Fragmentation**. Most people lose time and mental energy toggling between separate apps for fitness, finance, tasks, and notes. This system consolidates those silos into a single, high-performance ecosystem.

### 1. Centralized Efficiency
The website serves as a **Unified Command Center**. By housing every life domain—from **Iron Clad** (Physical) to **Neural Lock** (Cognitive)—under one authentication layer, it eliminates the "context-switching" cost that kills productivity.

### 2. Integrated Intelligence
Unlike siloed apps, this system allows different data points to talk to each other. The **Ethos Hub** (Dashboard) pulls real-time insights from across the entire platform, providing a **"Single Source of Truth."** Users no longer need to hunt for information; the information is presented exactly where and when they need it.

### 3. Frictionless Execution
The UI is optimized for speed. Through **Custom SVG Progress Rings** and **Synchronized Data Editors**, the system turns complex data entry into a 5-second task. It’s designed so the user spends less time *managing* their life and more time *living* it.

**The Bottom Line:** I made this to prove that **complexity can be managed simply.** It provides a professional-grade service that makes work easier, data clearer, and execution more efficient by keeping everything in one place.

---

## Technical Implementation Summary

* **Relational Database Integrity:** Powered by a **PostgreSQL** backend. The developer implemented a normalized schema that supports multi-user partitioning through unique identifier keys, ensuring data persistence and secure concurrent sessions.
* **Stateful Multi-Page Routing:** Leveraging **Streamlit’s session state**, the developer engineered a secure authentication layer (SHA-256) and a persistent global sidebar, maintaining user identity across nine independent modules.
* **Custom UI/UX Engineering:** The system utilizes **CSS Injection (Flexbox/Grid)** and **Raw SVG Rendering** to overcome framework limitations. Examples include custom-coded circular progress gauges and absolute-lock grids for visual stability.
* **Asynchronous Data Synchronization:** Advanced **"Upsert" logic** in the performance and habit modules allows multiple dataframes to be processed and committed in a single transaction, optimizing server-side latency.
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
