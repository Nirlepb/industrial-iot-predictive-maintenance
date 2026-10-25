# Industrial IoT Predictive Maintenance

This project is an Industrial IoT (IIoT) predictive maintenance and anomaly analytics system. It monitors simulated machine sensors in real-time, classifies machine health, and provides a dashboard for trend analysis.

## Features & Team Contributions

*   **Sensor Simulation & Data Generation (Nirlep):** Simulates live telemetry data for industrial machines (motors, pumps, compressors), including temperature, vibration, pressure, and RPM, and injects anomalies to simulate failing equipment.
*   **Trend & Anomaly Analytics (Abhijith):** Analyzes historical sensor data to calculate anomaly rates, identify threshold violations, and rank machines by risk level.
*   **Maintenance Monitoring & Dashboard (Rajneesh):** Provides a real-time Streamlit dashboard for visualizing system health, monitoring live sensor readings against safety thresholds, and generating maintenance recommendations based on machine status.

## Technologies Used

*   Python
*   InfluxDB 3 Core
*   Streamlit
*   Plotly
*   Pandas

## Setup and Installation

1.  **Start InfluxDB:** Ensure your InfluxDB 3 Core instance is running locally on `http://localhost:8181`. The project uses a database named `industrial_iot`.
2.  **Install Requirements:**
    ```bash
    pip install influxdb-client-3 streamlit pandas plotly streamlit-autorefresh
    ```

## Usage

You should run the scripts in the following order:

1.  **Start the Sensor Simulator (Nirlep's module):**
    Run this script continuously to generate live telemetry data.
    ```bash
    python sensor_simulator_2.py
    ```

2.  **Run Analytics (Abhijith's modules):**
    Execute these scripts to evaluate historical data and identify trends.
    ```bash
    python anomaly_analytics_2.py
    python trend_analysis_2.py
    ```

3.  **View the Dashboard & Maintenance Monitor (Rajneesh's modules):**
    You can run the terminal-based live monitor or start the interactive web dashboard.
    ```bash
    # Terminal-based health report
    python maintenance_monitor_2.py
    
    # Interactive web dashboard
    streamlit run dashboard_2.py
    ```

## System Thresholds

The system uses the following illustrative thresholds to classify machine health:
*   **WARNING:** Temperature > 80°C OR Vibration > 7 mm/s
*   **CRITICAL:** Temperature > 90°C OR Vibration > 9 mm/s
