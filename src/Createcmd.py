import os

# Directory where certificates are stored
certs_dir = "/Users/snbaskarraj/Documents/IITCapstone/AgriTech-WaterManagement/src/certificates"
endpoint = "a3afaswqeqldkp-ats.iot.us-east-1.amazonaws.com"

# Path to the Amazon Root CA 1 file
root_ca_path = os.path.join(certs_dir, "AmazonRootCA1.pem")

# Topics for publishing messages
topic = "iot/agritech_raw"
sprinkler_topic = "iot/sprinkler"

# List all certificate files in the certs directory
cert_files = os.listdir(certs_dir)

for cert_file in cert_files:
    if cert_file.endswith('-certificate.pem.crt'):
        # Extract device ID or name from the certificate file name
        device_id = cert_file.split('-')[0]

        # Construct file paths for the certificate and keys
        cert_path = os.path.join(certs_dir, cert_file)
        key_path = os.path.join(certs_dir, f"{device_id}-private.pem.key")

        # Check if the device is a sprinkler based on its ID (SP1 to SP5)
        if device_id.startswith("SP"):
            # Generate command for sprinkler
            print(f"python3 SprinklerController.py -e {endpoint} -r {root_ca_path} -c {cert_path} -k {key_path} -t {sprinkler_topic}")
        else:
            # Assume any other device is a soil sensor and generate the appropriate command
            print(f"python3 SoilSensorDataSimulator.py -e {endpoint} -r {root_ca_path} -c {cert_path} -k {key_path} -t {topic} -d Temperature")
