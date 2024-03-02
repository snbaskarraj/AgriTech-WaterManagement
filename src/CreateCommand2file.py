import os

# Directory where certificates are stored
certs_dir = "/Users/snbaskarraj/Documents/IITCapstone/AgriTech-WaterManagement/src/certificates"
endpoint = "a1p6hkr6e7u1ac-ats.iot.us-east-1.amazonaws.com"

# Path to the Amazon Root CA 1 file
root_ca_path = os.path.join(certs_dir, "AmazonRootCA1.pem")

# Topics for publishing messages
topic = "iot/agritech_raw"
sprinkler_topic = "iot/sprinkler"

# Assuming device_type is only relevant for soil sensors in this context
#device_type = "Temperature"  # Use "Moisture" for soil moisture sensors
device_type = "Moisture"  # Use "Moisture" for soil moisture sensors

# List all certificate files in the certs directory
cert_files = os.listdir(certs_dir)

# List to store commands
commands = []

for cert_file in cert_files:
    if cert_file.endswith('-certificate.pem.crt'):
        # Extract device ID or name from the certificate file name
        device_id = cert_file.split('-')[0]

        # Construct file paths for the certificate and keys
        cert_path = os.path.join(certs_dir, cert_file)
        key_path = os.path.join(certs_dir, f"{device_id}-private.pem.key")
        # The public key is not used in the MQTT connect command

        # Check if the device is a Soil Sensor or a Sprinkler based on its ID and generate the appropriate command
        if "SoilSensor" in device_id:
            command = f"python3 SoilSensorDataSimulator.py -e {endpoint} -r {root_ca_path} -c {cert_path} -k {key_path} -t {topic} -d {device_type}"
            commands.append(command)
        elif "Sprinkler" in device_id:
            command = f"python3 SprinklerController.py -e {endpoint} -r {root_ca_path} -c {cert_path} -k {key_path} -t {sprinkler_topic}"
            commands.append(command)

# Write commands to a file
with open("commands.txt", "w") as f:
    for command in commands:
        f.write(command + "\n")

# Execute commands from the file
os.system("bash commands.txt")
