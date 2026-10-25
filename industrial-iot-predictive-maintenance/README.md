# Industrial IoT Predictive Maintenance & Anomaly Analytics

A Python DBMS project that simulates industrial machine sensor readings, stores telemetry in InfluxDB 3 Core, analyzes abnormal readings, reports machine health, and presents a Streamlit dashboard.

## Technology stack

- Python
- InfluxDB 3 Core
- SQL queries through the InfluxDB 3 Python client
- Streamlit, Pandas, and Plotly
- streamlit-autorefresh

## Project files

| File | Purpose | Owner |
|---|---|---|
| `sensor_simulator.py` | Generates simulated telemetry for a motor, pump, and compressor and writes it to InfluxDB | Person 1 |
| `anomaly_analytics.py` | Aggregates readings, calculates anomaly percentages, ranks risk, and prints recommendations | Person 2 |
| `trend_analysis.py` | Reports historical temperature, vibration, pressure, and anomaly statistics | Person 2 |
| `maintenance_monitor.py` | Reports the latest reading and health classification for each machine | Person 2 |
| `dashboard.py` | Streamlit dashboard with metrics, filters, trends, comparisons, and recommendations | Person 3 |

## Requirements

1. Python 3.10 or newer is recommended.
2. InfluxDB 3 Core must be installed and running locally.
3. The InfluxDB endpoint expected by the supplied scripts is `http://localhost:8181`.
4. The scripts use the database name `industrial_iot`. Create/configure it in your InfluxDB 3 Core environment before running the scripts, following the setup instructions for your installed InfluxDB version.

The supplied scripts currently use a local endpoint and the token value `unused`. This is suitable only if it matches your local development setup. Do not commit real credentials or tokens.

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Nirlepb/industrial-iot-predictive-maintenance.git
cd industrial-iot-predictive-maintenance
```

### 2. Create and activate a virtual environment

**Windows (PowerShell):**

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Python dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Start InfluxDB 3 Core

Start your local InfluxDB 3 Core service and verify that it is reachable at `http://localhost:8181`. Ensure the `industrial_iot` database is available before running the Python scripts.

### 5. Run the sensor simulator

```bash
python sensor_simulator.py
```

It writes simulated readings for three machines in a loop. Press `Ctrl+C` to stop it. Keep this terminal running while testing the dashboard or reports.

### 6. Run the dashboard

In another terminal, with the virtual environment activated:

```bash
streamlit run dashboard.py
```

Follow the local URL printed by Streamlit.

### 7. Run the reports

After sensor readings have been written, run any report in a separate terminal:

```bash
python anomaly_analytics.py
python trend_analysis.py
python maintenance_monitor.py
```

Run each report separately. They query the same `machine_telemetry` measurement.

## Current anomaly rules

The supplied code uses illustrative rule-based thresholds:

- Warning: temperature above 80°C or vibration above 7 mm/s.
- Critical: temperature above 90°C or vibration above 9 mm/s.

These are project demonstration thresholds, not universal industrial safety limits. The current implementation uses threshold-based classification, not a trained machine-learning model.

## Three-person Git collaboration

Use `main` as the stable integrated branch. Each person works on a separate feature branch and opens a pull request before merging.

- Person 1: `feature/sensor-database`
- Person 2: `feature/analytics`
- Person 3: `feature/dashboard`

See [`docs/TEAM_WORKFLOW.md`](docs/TEAM_WORKFLOW.md) for commands and integration rules.

## Known implementation notes

- The scripts expect the InfluxDB endpoint, database name, and measurement schema described above.
- The simulator writes one reading for each of three machines every five seconds.
- `trend_analysis.py` reports aggregate historical statistics; it does not establish that a metric is increasing or decreasing over time.
- Validate database setup, dependency compatibility, and queries against the version of InfluxDB 3 Core installed on each teammate's computer.
