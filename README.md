# <p align="center">🛡️ ETHOS HUB: NEURAL COMMAND OS</p>
<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white" />
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white" />
  <img src="https://img.shields.io/badge/Architecture-Decoupled-76b372?style=for-the-badge" />
</p>

---

## THE ENGINEERING PHILOSOPHY
Ethos Hub is a **High-Availability Personal OS** engineered for the 4th-semester IT curriculum and beyond. Version 3.0 solves the "State-Dependency" trap through three industrial-grade pillars:

* **Stateless Resilience:** Utilizing **PostgreSQL** as a persistent source of truth. By moving logic (like active timers) from the browser's temporary memory to a persistent SQL shard, the system survives crashes, logouts, and device swaps.
* **Modular Lab Architecture:** Isolated environments (Neural, Financial, Habit) decoupled via **Lazy Loading** to prevent cross-module failure and circular import deadlocks.
* **Automated Observability:** Real-time telemetry monitoring that treats personal growth with the same technical rigor as a commercial software product.

---



## CORE MODULES (THE LABS)

### **Home Hub | Strategic Command**
The central nervous system. It serves as a high-speed aggregator designed for "Zero-Eternity" loading through state-first rendering.
* **Neural Interface:** Instant-state authentication using **JWT tokens** and session escalation.
* **Strategic Command:** A persistent "North Star" for Academic, Health, and Personal objectives.
* **Real-time Shards:** Parallel column rendering for today's protocols, future blueprints, and financial status.

### **Neural Lock | Focus Engineering**
A high-stakes deep-work laboratory designed to eliminate "Session Fragmentation."
* **Persistent Stopwatch:** Stores `start_time` timestamps in the DB, allowing sessions to survive reboots.
* **Resume Logic:** `Elapsed Time = Current_Timestamp - DB_Stored_Start_Time`. 
* **Visual Momentum:** Interactive **Plotly** area charts that visualize focus density and daily output metrics ($m/day$).

### **Weekly Planner | Tactical Execution**
A 7-day tactical grid for managing high-priority objectives.
* **Boxed Design:** Each task is encapsulated in an isolated container for high scannability.
* **Dynamic Progress Rings:** SVG-based circular charts provide instant visual feedback on daily completion percentages.
* **Cleanup Protocol:** Automated maintenance to clear finished objectives and optimize database views.

### **Financial Lab | Resource Management**
A personal accounting system to maintain financial transparency and prevent debt accumulation.
* **Neural Ledger:** Real-time "Planned vs. Actual" spending metrics intersecting `finances` and `expense_logs`.
* **Debt Shard:** Integrated tracking of net debt and repayment status, essential for managing life in Bangalore.

---

## DEVOPS & INFRASTRUCTURE



| Stage | Technology | Purpose |
| :--- | :--- | :--- |
| **Telemetry** | `Custom Logger` | Real-time tracking of DB latency and "Neural Glitches" (Errors). |
| **Persistence** | `Port 6543` | **Transaction-level pooling** to prevent connection leaks and TCP hangs. |
| **CI/CD** | `GitHub Actions` | Automated builds verifying environment health and dependency integrity. |
| **Auth** | `JWT + Cookies` | Persistent, 30-day encrypted tokens via the `Cookie Controller`. |

---

## 🛠️ TECHNICAL SPECIFICATIONS
| Component | Description |
| :--- | :--- |
| **Backend** | Python 3.11 (Streamlit Framework) |
| **Database** | PostgreSQL with `psycopg2` **Singleton Pooling** |
| **Architecture** | Decoupled modular design with **Lazy Loading** imports |
| **Styling** | Custom CSS injection for "Ethos Green" (#76b372) aesthetic |
| **Security** | Rate limiting, XSS Sanitization (`html.escape`), and JWT validation |

---

## 🚀 SETUP & RECOVERY
**Neural Link:**
   ```bash
   git clone [https://github.com/AryavVij/ethos-hub.git](https://github.com/AryavVij/ethos-hub.git)
   pip install -r requirements.txt
