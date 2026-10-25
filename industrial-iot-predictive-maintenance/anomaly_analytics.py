from influxdb_client_3 import InfluxDBClient3

# --------------------------------------------------
# INDUSTRIAL IoT - ANOMALY ANALYTICS
# --------------------------------------------------

client = InfluxDBClient3(
    host="http://localhost:8181",
    token="unused",
    database="industrial_iot"
)

# Thresholds used for this simulated project
WARNING_TEMP = 80
CRITICAL_TEMP = 90
WARNING_VIBRATION = 7
CRITICAL_VIBRATION = 9

query = """
SELECT
    machine_id,
    COUNT(*) AS total_readings,
    AVG(temperature) AS avg_temperature,
    MAX(temperature) AS max_temperature,
    AVG(vibration) AS avg_vibration,
    MAX(vibration) AS max_vibration,
    SUM(
        CASE
            WHEN temperature > 80 OR vibration > 7 THEN 1
            ELSE 0
        END
    ) AS abnormal_readings,
    SUM(
        CASE
            WHEN temperature > 90 OR vibration > 9 THEN 1
            ELSE 0
        END
    ) AS critical_readings
FROM machine_telemetry
GROUP BY machine_id
"""

try:
    result = client.query(query=query, language="sql")
    rows = result.to_pylist()

    print("=" * 90)
    print("             INDUSTRIAL IoT - ANOMALY ANALYTICS REPORT")
    print("=" * 90)

    if not rows:
        print("\nNo sensor data found.")
        print("Run sensor_simulator.py to generate data.")

    else:
        reports = []

        for row in rows:
            total = row["total_readings"] or 0
            abnormal = row["abnormal_readings"] or 0
            critical = row["critical_readings"] or 0

            anomaly_percentage = (
                abnormal / total * 100 if total else 0
            )

            # Rank risk using observed simulated readings.
            if critical > 0:
                risk = "HIGH"
                recommendation = "Prioritize machine inspection"
            elif abnormal > 0:
                risk = "MEDIUM"
                recommendation = "Review abnormal readings"
            else:
                risk = "LOW"
                recommendation = "Continue routine monitoring"

            reports.append({
                "machine_id": row["machine_id"],
                "total": total,
                "avg_temp": row["avg_temperature"],
                "max_temp": row["max_temperature"],
                "avg_vibration": row["avg_vibration"],
                "max_vibration": row["max_vibration"],
                "abnormal": abnormal,
                "critical": critical,
                "anomaly_percentage": anomaly_percentage,
                "risk": risk,
                "recommendation": recommendation
            })

        # Highest risk first, then anomaly percentage.
        risk_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}

        reports.sort(
            key=lambda item: (
                risk_order[item["risk"]],
                -item["anomaly_percentage"],
                -item["critical"]
            )
        )

        for index, report in enumerate(reports, start=1):
            print(f"\nRISK RANK: #{index}")
            print(f"Machine ID            : {report['machine_id']}")
            print(f"Total readings        : {report['total']}")
            print(
                f"Average temperature   : "
                f"{report['avg_temp']:.2f} C"
            )
            print(
                f"Maximum temperature   : "
                f"{report['max_temp']:.2f} C"
            )
            print(
                f"Average vibration     : "
                f"{report['avg_vibration']:.2f} mm/s"
            )
            print(
                f"Maximum vibration     : "
                f"{report['max_vibration']:.2f} mm/s"
            )
            print(
                f"Abnormal readings     : "
                f"{report['abnormal']}"
            )
            print(
                f"Critical readings     : "
                f"{report['critical']}"
            )
            print(
                f"Anomaly percentage    : "
                f"{report['anomaly_percentage']:.2f}%"
            )
            print(f"Risk category         : {report['risk']}")
            print(f"Recommendation        : {report['recommendation']}")
            print("-" * 90)

        # Overall analytics summary
        total_machines = len(reports)
        total_readings = sum(r["total"] for r in reports)
        total_abnormal = sum(r["abnormal"] for r in reports)
        total_critical = sum(r["critical"] for r in reports)

        print("\n" + "=" * 90)
        print("                         OVERALL SUMMARY")
        print("=" * 90)
        print(f"Machines analyzed     : {total_machines}")
        print(f"Total sensor readings : {total_readings}")
        print(f"Abnormal readings     : {total_abnormal}")
        print(f"Critical readings     : {total_critical}")

        overall_percentage = (
            total_abnormal / total_readings * 100
            if total_readings else 0
        )

        print(f"Overall anomaly rate  : {overall_percentage:.2f}%")

        if reports:
            highest_risk = reports[0]
            print(f"Highest-ranked machine: {highest_risk['machine_id']}")
            print(f"Risk category         : {highest_risk['risk']}")

        print("\nAnalytics completed successfully.")

finally:
    client.close()