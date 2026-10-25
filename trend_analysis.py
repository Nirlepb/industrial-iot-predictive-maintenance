from influxdb_client_3 import InfluxDBClient3

client = InfluxDBClient3(
    host="http://localhost:8181",
    token="unused",
    database="industrial_iot"
)

query = """
SELECT
    machine_id,
    COUNT(*) AS total_readings,
    AVG(temperature) AS avg_temperature,
    MIN(temperature) AS min_temperature,
    MAX(temperature) AS max_temperature,
    AVG(vibration) AS avg_vibration,
    MAX(vibration) AS max_vibration,
    AVG(pressure) AS avg_pressure,
    MAX(time) AS latest_reading,
    SUM(
        CASE
            WHEN temperature > 80 OR vibration > 7
            THEN 1 ELSE 0
        END
    ) AS abnormal_readings,
    SUM(
        CASE
            WHEN temperature > 90 OR vibration > 9
            THEN 1 ELSE 0
        END
    ) AS critical_readings
FROM machine_telemetry
GROUP BY machine_id
"""

try:
    result = client.query(query=query, language="sql")
    rows = result.to_pylist()

    print("=" * 85)
    print("          INDUSTRIAL IoT - HISTORICAL TREND ANALYSIS")
    print("=" * 85)

    if not rows:
        print("\nNo data available. Run sensor_simulator.py first.")

    else:
        for row in sorted(rows, key=lambda r: r["machine_id"]):
            machine = row["machine_id"]
            total = row["total_readings"] or 0
            abnormal = row["abnormal_readings"] or 0
            critical = row["critical_readings"] or 0

            anomaly_rate = (
                abnormal / total * 100 if total else 0
            )

            print(f"\nMACHINE: {machine}")
            print("-" * 85)
            print(f"Total readings          : {total}")
            print(f"Latest recorded time    : {row['latest_reading']}")
            print(f"Minimum temperature     : {row['min_temperature']:.2f} C")
            print(f"Average temperature     : {row['avg_temperature']:.2f} C")
            print(f"Maximum temperature     : {row['max_temperature']:.2f} C")
            print(f"Average vibration       : {row['avg_vibration']:.2f} mm/s")
            print(f"Maximum vibration       : {row['max_vibration']:.2f} mm/s")
            print(f"Average pressure        : {row['avg_pressure']:.2f} bar")
            print(f"Abnormal readings       : {abnormal}")
            print(f"Critical readings       : {critical}")
            print(f"Historical anomaly rate : {anomaly_rate:.2f}%")

            if critical > 0:
                print("Trend assessment       : Historical critical events recorded")
            elif abnormal > 0:
                print("Trend assessment       : Historical abnormal events recorded")
            else:
                print("Trend assessment       : No threshold violations recorded")

        print("\n" + "=" * 85)
        print("TREND ANALYSIS COMPLETED")
        print("=" * 85)
        print(
            "Note: These are aggregate historical statistics, "
            "not proof of an increasing or decreasing trend."
        )

finally:
    client.close()