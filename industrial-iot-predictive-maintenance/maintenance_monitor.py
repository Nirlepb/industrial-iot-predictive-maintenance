from influxdb_client_3 import InfluxDBClient3

# Connect to InfluxDB 3 Core
client = InfluxDBClient3(
    host="http://localhost:8181",
    token="unused",
    database="industrial_iot"
)


def classify_machine(temperature, vibration):
    """Determine machine health from its latest sensor readings."""

    if temperature > 90 or vibration > 9:
        return "CRITICAL", "Inspect machine immediately"

    elif temperature > 80 or vibration > 7:
        return "WARNING", "Schedule maintenance inspection"

    return "NORMAL", "Continue routine monitoring"


query = """
SELECT
    machine_id,
    time,
    temperature,
    vibration,
    pressure,
    rpm
FROM machine_telemetry
ORDER BY time DESC
"""

try:
    table = client.query(
        query=query,
        language="sql"
    )

    rows = table.to_pylist()

    print("=" * 80)
    print("          INDUSTRIAL IoT - LIVE MACHINE HEALTH REPORT")
    print("=" * 80)

    # Keep the newest reading for each machine
    latest_readings = {}

    for row in rows:
        machine_id = row["machine_id"]

        if machine_id not in latest_readings:
            latest_readings[machine_id] = row

    if not latest_readings:
        print("\nNo sensor data found.")
        print("Run sensor_simulator.py to generate readings.")

    else:
        critical_count = 0
        warning_count = 0
        normal_count = 0

        for machine_id, row in sorted(latest_readings.items()):

            temperature = row["temperature"]
            vibration = row["vibration"]
            pressure = row["pressure"]
            rpm = row["rpm"]

            status, recommendation = classify_machine(
                temperature,
                vibration
            )

            if status == "CRITICAL":
                critical_count += 1
            elif status == "WARNING":
                warning_count += 1
            else:
                normal_count += 1

            print(f"\nMachine ID      : {machine_id}")
            print(f"Latest reading  : {row['time']}")
            print(f"Temperature     : {temperature} C")
            print(f"Vibration       : {vibration} mm/s")
            print(f"Pressure        : {pressure} bar")
            print(f"RPM             : {rpm}")
            print(f"Health status   : {status}")
            print(f"Recommendation  : {recommendation}")
            print("-" * 80)

        # Overall system summary
        print("\n")
        print("=" * 80)
        print("                    SYSTEM HEALTH SUMMARY")
        print("=" * 80)
        print(f"Machines monitored : {len(latest_readings)}")
        print(f"NORMAL             : {normal_count}")
        print(f"WARNING            : {warning_count}")
        print(f"CRITICAL           : {critical_count}")

        if critical_count > 0:
            print("\nALERT: One or more machines require immediate inspection.")
        elif warning_count > 0:
            print("\nALERT: Some machines require a maintenance inspection.")
        else:
            print("\nAll monitored machines are currently within the defined thresholds.")

        print("\nReport generated successfully.")

finally:
    client.close()