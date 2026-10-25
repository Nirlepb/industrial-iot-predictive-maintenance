import random
import time
from influxdb_client_3 import InfluxDBClient3, Point

# Connect to InfluxDB 3 Core
client = InfluxDBClient3(
    host="http://localhost:8181",
    token="unused",
    database="industrial_iot"
)

# Machines being monitored
machines = [
    {"id": "M001", "type": "motor"},
    {"id": "M002", "type": "pump"},
    {"id": "M003", "type": "compressor"}
]

print("=" * 75)
print("       INDUSTRIAL IoT PREDICTIVE MAINTENANCE SYSTEM")
print("=" * 75)
print("Database: industrial_iot")
print("Monitoring 3 machines...")
print("Anomaly injection: 30% probability per reading")
print("Press Ctrl+C to stop.\n")

try:
    while True:
        for machine in machines:

            # Generate normal sensor readings
            temperature = round(random.uniform(50, 75), 2)
            vibration = round(random.uniform(1, 5), 2)
            pressure = round(random.uniform(4, 8), 2)
            rpm = float(random.randint(1200, 1800))

            # Inject simulated abnormal readings
            if random.random() < 0.30:
                temperature = round(random.uniform(85, 100), 2)
                vibration = round(random.uniform(7, 10), 2)

            # Classify machine health
            if temperature > 90 or vibration > 9:
                status = "CRITICAL"
            elif temperature > 80 or vibration > 7:
                status = "WARNING"
            else:
                status = "NORMAL"

            # Build telemetry point
            point = (
                Point("machine_telemetry")
                .tag("machine_id", machine["id"])
                .tag("machine_type", machine["type"])
                .field("temperature", temperature)
                .field("vibration", vibration)
                .field("pressure", pressure)
                .field("rpm", rpm)
                .field("status", status)
            )

            # Write data to InfluxDB
            try:
                client.write(point)

                print(
                    f'{machine["id"]} ({machine["type"]}) | '
                    f'Temp: {temperature} C | '
                    f'Vibration: {vibration} mm/s | '
                    f'Pressure: {pressure} bar | '
                    f'RPM: {rpm:.0f} | '
                    f'Status: {status}'
                )

            except Exception as error:
                print(
                    f'Write failed for {machine["id"]}: {error}'
                )

        print("-" * 75)

        # Wait before the next collection cycle
        time.sleep(5)

except KeyboardInterrupt:
    print("\nSensor simulation stopped.")

finally:
    client.close()
    print("Database connection closed.")