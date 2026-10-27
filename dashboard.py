import streamlit as st
import pandas as pd
import plotly.express as px

from influxdb_client_3 import InfluxDBClient3
from streamlit_autorefresh import st_autorefresh

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Industrial IoT Predictive Maintenance",
    page_icon="🏭",
    layout="wide"
)

# Refresh dashboard every 10 seconds
st_autorefresh(
    interval=10_000,
    key="industrial_iot_refresh"
)

# Thresholds used for this project
WARNING_TEMP = 80
CRITICAL_TEMP = 90
WARNING_VIBRATION = 7
CRITICAL_VIBRATION = 9

# =========================================================
# HEADER
# =========================================================

st.title("🏭 Industrial IoT Predictive Maintenance")
st.caption(
    "Real-Time Sensor Monitoring | Anomaly Analytics | Machine Health"
)

st.caption(
    f"Last dashboard refresh: "
    f"{pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}"
)

# =========================================================
# DATABASE CONNECTION AND DATA RETRIEVAL
# =========================================================

@st.cache_data(ttl=5)
def load_data():
    client = InfluxDBClient3(
        host="http://localhost:8181",
        token="unused",
        database="industrial_iot"
    )

    query = """
    SELECT
        time,
        machine_id,
        machine_type,
        temperature,
        vibration,
        pressure,
        rpm
    FROM machine_telemetry
    ORDER BY time DESC
    """

    try:
        result = client.query(
            query=query,
            language="sql"
        )

        rows = result.to_pylist()

    finally:
        client.close()

    df = pd.DataFrame(rows)

    if not df.empty:
        df["time"] = pd.to_datetime(
            df["time"],
            utc=True
        )

        df = df.sort_values("time")

    return df


try:
    df = load_data()

except Exception as error:
    st.error("Unable to connect to InfluxDB.")
    st.code(str(error))

    st.info(
        "Ensure the InfluxDB server is running on "
        "http://localhost:8181."
    )

    st.stop()


if df.empty:
    st.warning(
        "No sensor readings found. Start sensor_simulator.py "
        "to generate data."
    )
    st.stop()


# =========================================================
# HEALTH CLASSIFICATION
# =========================================================

def classify_machine(row):
    temperature = row["temperature"]
    vibration = row["vibration"]

    if (
        temperature > CRITICAL_TEMP
        or vibration > CRITICAL_VIBRATION
    ):
        return "CRITICAL"

    if (
        temperature > WARNING_TEMP
        or vibration > WARNING_VIBRATION
    ):
        return "WARNING"

    return "NORMAL"


# Latest reading for every machine
latest = (
    df.sort_values("time", ascending=False)
      .drop_duplicates(subset=["machine_id"])
      .copy()
)

latest["health_status"] = latest.apply(
    classify_machine,
    axis=1
)

# Historical anomaly flags
df["is_abnormal"] = (
    (df["temperature"] > WARNING_TEMP)
    | (df["vibration"] > WARNING_VIBRATION)
)

df["is_critical"] = (
    (df["temperature"] > CRITICAL_TEMP)
    | (df["vibration"] > CRITICAL_VIBRATION)
)


# =========================================================
# SIDEBAR CONTROLS
# =========================================================

st.sidebar.header("Dashboard Controls")

machine_options = sorted(
    df["machine_id"].dropna().unique().tolist()
)

selected_machines = st.sidebar.multiselect(
    "Select machines",
    options=machine_options,
    default=machine_options
)

if st.sidebar.button("Refresh data"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.caption(
    "Automatic refresh: every 10 seconds"
)

st.sidebar.caption(
    "Data source: InfluxDB 3 Core"
)

if not selected_machines:
    st.warning(
        "Select at least one machine from the sidebar."
    )
    st.stop()


filtered_df = df[
    df["machine_id"].isin(selected_machines)
].copy()

filtered_latest = latest[
    latest["machine_id"].isin(selected_machines)
].copy()


# =========================================================
# SYSTEM OVERVIEW
# =========================================================

st.header("📊 System Overview")

total_readings = len(filtered_df)

machine_count = filtered_latest[
    "machine_id"
].nunique()

abnormal_count = int(
    filtered_df["is_abnormal"].sum()
)

critical_reading_count = int(
    filtered_df["is_critical"].sum()
)

anomaly_rate = (
    abnormal_count / total_readings * 100
    if total_readings > 0
    else 0
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Machines Monitored",
    machine_count
)

col2.metric(
    "Total Sensor Readings",
    total_readings
)

col3.metric(
    "Historical Anomalies",
    abnormal_count
)

col4.metric(
    "Historical Anomaly Rate",
    f"{anomaly_rate:.2f}%"
)

st.divider()


# =========================================================
# CURRENT MACHINE HEALTH
# =========================================================

st.header("🩺 Latest Machine Health")

normal_count = int(
    (filtered_latest["health_status"] == "NORMAL").sum()
)

warning_count = int(
    (filtered_latest["health_status"] == "WARNING").sum()
)

critical_machine_count = int(
    (filtered_latest["health_status"] == "CRITICAL").sum()
)

health1, health2, health3 = st.columns(3)

health1.metric(
    "🟢 Normal Machines",
    normal_count
)

health2.metric(
    "🟠 Warning Machines",
    warning_count
)

health3.metric(
    "🔴 Critical Machines",
    critical_machine_count
)

display_latest = filtered_latest[
    [
        "machine_id",
        "time",
        "temperature",
        "vibration",
        "pressure",
        "rpm",
        "health_status"
    ]
].copy()

display_latest = display_latest.rename(
    columns={
        "machine_id": "Machine",
        "time": "Latest Reading (UTC)",
        "temperature": "Temperature (°C)",
        "vibration": "Vibration (mm/s)",
        "pressure": "Pressure (bar)",
        "rpm": "RPM",
        "health_status": "Health Status"
    }
)

display_latest["Latest Reading (UTC)"] = (
    display_latest["Latest Reading (UTC)"]
    .dt.strftime("%Y-%m-%d %H:%M:%S UTC")
)

st.dataframe(
    display_latest.sort_values("Machine"),
    width="stretch",
    hide_index=True
)

st.divider()


# =========================================================
# TEMPERATURE TREND
# =========================================================

st.header("🌡️ Temperature Trend Analysis")

temperature_fig = px.line(
    filtered_df,
    x="time",
    y="temperature",
    color="machine_id",
    markers=True,
    title="Machine Temperature Over Time",
    labels={
        "time": "Timestamp",
        "temperature": "Temperature (°C)",
        "machine_id": "Machine"
    }
)

temperature_fig.add_hline(
    y=WARNING_TEMP,
    line_dash="dash",
    annotation_text="Warning: 80°C"
)

temperature_fig.add_hline(
    y=CRITICAL_TEMP,
    line_dash="dot",
    annotation_text="Critical: 90°C"
)

temperature_fig.update_layout(
    hovermode="x unified",
    legend_title_text="Machine"
)

st.plotly_chart(
    temperature_fig,
    width="stretch"
)


# =========================================================
# VIBRATION TREND
# =========================================================

st.header("📳 Vibration Trend Analysis")

vibration_fig = px.line(
    filtered_df,
    x="time",
    y="vibration",
    color="machine_id",
    markers=True,
    title="Machine Vibration Over Time",
    labels={
        "time": "Timestamp",
        "vibration": "Vibration (mm/s)",
        "machine_id": "Machine"
    }
)

vibration_fig.add_hline(
    y=WARNING_VIBRATION,
    line_dash="dash",
    annotation_text="Warning: 7 mm/s"
)

vibration_fig.add_hline(
    y=CRITICAL_VIBRATION,
    line_dash="dot",
    annotation_text="Critical: 9 mm/s"
)

vibration_fig.update_layout(
    hovermode="x unified",
    legend_title_text="Machine"
)

st.plotly_chart(
    vibration_fig,
    width="stretch"
)

st.divider()


# =========================================================
# HISTORICAL MACHINE COMPARISON
# =========================================================

st.header("📈 Historical Machine Comparison")

comparison = (
    filtered_df.groupby("machine_id")
    .agg(
        average_temperature=("temperature", "mean"),
        maximum_temperature=("temperature", "max"),
        average_vibration=("vibration", "mean"),
        maximum_vibration=("vibration", "max"),
        total_readings=("temperature", "count"),
        abnormal_readings=("is_abnormal", "sum"),
        critical_readings=("is_critical", "sum")
    )
    .reset_index()
)

comparison["anomaly_rate_percent"] = (
    comparison["abnormal_readings"]
    / comparison["total_readings"]
    * 100
)

comparison = comparison.sort_values(
    "anomaly_rate_percent",
    ascending=False
)

st.dataframe(
    comparison.round(2),
    width="stretch",
    hide_index=True
)


# =========================================================
# ANOMALY RATE CHART
# =========================================================

st.subheader("Anomaly Rate by Machine")

anomaly_fig = px.bar(
    comparison,
    x="machine_id",
    y="anomaly_rate_percent",
    text="anomaly_rate_percent",
    color="anomaly_rate_percent",
    color_continuous_scale="Reds",
    title="Percentage of Historical Abnormal Readings",
    labels={
        "machine_id": "Machine",
        "anomaly_rate_percent": "Anomaly Rate (%)"
    }
)

anomaly_fig.update_traces(
    texttemplate="%{text:.2f}%",
    textposition="outside"
)

st.plotly_chart(
    anomaly_fig,
    width="stretch"
)


# =========================================================
# MAINTENANCE RECOMMENDATIONS
# =========================================================

st.header("🛠️ Maintenance Recommendations")

for _, row in filtered_latest.sort_values(
    "machine_id"
).iterrows():

    machine_id = row["machine_id"]
    status = row["health_status"]

    temperature = row["temperature"]
    vibration = row["vibration"]

    if status == "CRITICAL":
        st.error(
            f"🔴 {machine_id}: CRITICAL — "
            f"Temperature: {temperature:.2f}°C, "
            f"Vibration: {vibration:.2f} mm/s. "
            "Prioritize machine inspection."
        )

    elif status == "WARNING":
        st.warning(
            f"🟠 {machine_id}: WARNING — "
            f"Temperature: {temperature:.2f}°C, "
            f"Vibration: {vibration:.2f} mm/s. "
            "Schedule a maintenance inspection."
        )

    else:
        st.success(
            f"🟢 {machine_id}: NORMAL — "
            "Latest sensor readings are within "
            "the configured thresholds."
        )


# =========================================================
# HISTORICAL ALERT SUMMARY
# =========================================================

st.divider()

st.header("🚨 Historical Alert Summary")

summary1, summary2, summary3 = st.columns(3)

summary1.metric(
    "Historical Abnormal Readings",
    abnormal_count
)

summary2.metric(
    "Historical Critical Readings",
    critical_reading_count
)

summary3.metric(
    "Machines Currently Critical",
    critical_machine_count
)

st.caption(
    "Historical anomaly counts describe past readings. "
    "Current machine status is based on the latest reading "
    "for each machine."
)

st.caption(
    "Thresholds are illustrative project settings, not "
    "universal industrial safety limits. This dashboard "
    "uses rule-based anomaly detection, not a trained "
    "machine-learning failure prediction model."
)

st.divider()

st.caption(
    "Industrial IoT Predictive Maintenance & Anomaly Analytics | "
    "InfluxDB 3 Core • Python • Streamlit • Plotly"
)
