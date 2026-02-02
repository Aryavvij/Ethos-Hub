# <p align="center">ETHOS HUB: PERSONAL OS</p>
<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white" />
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white" />
</p>

---

## THE ENGINEERING PHILOSOPHY
Ethos Hub is a **High-Availability Personal OS** engineered for the 4th-semester IT curriculum and beyond. Most productivity tools fail because they are "state-dependent"—if the browser closes, the data resets. Ethos Hub solves this through three industrial-grade pillars:

* **Stateless Resilience:** Utilizing **PostgreSQL** as a persistent source of truth. By moving logic (like active timers) from the browser's temporary memory to a persistent SQL database, the system survives crashes, logouts, and device swaps.
* **Modular Lab Architecture:** Isolated environments (Neural, Financial, Habit) that prevent cross-module failure and allow for independent scaling.
* **Automated Lifecycle:** A professional **CI/CD pipeline** that treats personal growth with the same technical rigor as a commercial software product.

---

## CORE MODULES (THE LABS)

### **Home Hub | Strategic Command**
The central nervous system of the project. It serves as a high-level aggregator that pulls data from every "Lab" to provide an instantaneous briefing.
* **Strategic Goals:** A persistent "North Star" section for Academic, Health, and Personal objectives.
* **Daily Briefing:** Automatically fetches today's tasks from the Planner and upcoming milestones from the Calendar.
* **Financial Snapshot:** Real-time container showing remaining budget and net debt status.

### **Neural Lock | Focus Engineering**
A high-stakes deep-work laboratory designed to eliminate "Session Fragmentation."
* **Persistent Stopwatch:** Solves the "Browser Refresh" problem by storing `start_time` timestamps in the DB.
* **Resume Logic:** `Elapsed Time = Current_Timestamp - DB_Stored_Start_Time`. This allows sessions to survive reboots or device changes.
* **Visual Momentum:** Interactive **Plotly** area charts that visualize focus density over 30-day windows.


### **Weekly Planner | Tactical Execution**
A 7-day tactical execution grid for managing high-priority objectives.
* **Boxed Design:** Each task is encapsulated in an isolated container for high scannability.
* **Dynamic Progress Rings:** SVG-based circular charts provide instant visual feedback on daily completion percentages.
* **Cleanup Protocol:** Automated maintenance to clear finished objectives and optimize the view.

### **Financial Lab | Resource Management**
A personal accounting system to maintain financial transparency and prevent debt accumulation.
* **Budgeting:** Track "Planned vs. Actual" spending for the current academic period.
* **Debt Ledger:** Integrated tracking of net debt and repayment status, essential for student life in Bangalore.

### **Habit & Gym Labs | Consistency Engines**
* **Trajectory Tracking:** Monitors long-term progress for physical goals (e.g., reaching a 70kg weight target).
* **Session Logs:** Stores granular data on workouts and habits to ensure meeting the "blueprint" set at the start of the semester.

---

## DEVOPS & INFRASTRUCTURE



| Stage | Technology | Purpose |
| :--- | :--- | :--- |
| **Linting** | `Flake8` | Static code analysis to ensure PEP8 compliance and prevent syntax errors. |
| **CI** | `GitHub Actions` | Automated builds that install dependencies and verify environment health. |
| **CD** | `Webhooks` | Post-success triggers that initiate atomic deployments to **Render**. |
| **Auth** | `Cookie Controller` | Persistent, encrypted browser cookies to prevent session-loss on cold restarts. |

---

## 🛠️ TECHNICAL SPECIFICATIONS
| Component | Description |
| :--- | :--- |
| **Backend** | Python 3.11 (Streamlit Framework) |
| **Database** | PostgreSQL with `psycopg2` connection pooling |
| **Styling** | Custom CSS injection for "Ethos Green" (#76b372) aesthetic |
| **Visuals** | Plotly Express & SVG Graphics |

---

## SETUP & DEPLOYMENT
1. **Repository Setup:**
   ```bash
   git clone [https://github.com/AryavVij/ethos-hub.git](https://github.com/AryavVij/ethos-hub.git)
   pip install -r requirements.txt
