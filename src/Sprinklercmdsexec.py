import subprocess

# Directory where certificates are stored
certs_dir = "/Users/snbaskarraj/Documents/IITCapstone/AgriTech-WaterManagement/src/certificates"
# IoT endpoint
endpoint = "a1p6hkr6e7u1ac-ats.iot.us-east-1.amazonaws.com"

# Path to the file containing commands
commands_file_path = '/Users/snbaskarraj/Documents/IITCapstone/AgriTech-WaterManagement/src/Sprinklercommands.txt'


def execute_commands_from_file(file_path, certs_dir, endpoint):
    try:
        # Open and read the commands from the file
        with open(file_path, 'r') as file:
            commands = file.readlines()

        # Execute each command
        for command in commands:
            # Strip newline characters from the command
            command = command.strip()
            if command:  # Ensure the command is not empty
                # Replace placeholders with actual certificate paths and endpoint
                command_formatted = command.format(
                    certs_dir=certs_dir,
                    endpoint=endpoint,
                    root_ca=f"{certs_dir}/AmazonRootCA1.pem",
                    certificate=f"{certs_dir}/{command.split(' ')[-4].split('/')[-1]}",
                    private_key=f"{certs_dir}/{command.split(' ')[-2].split('/')[-1]}"
                )
                print(f"Executing: {command_formatted}")
                # Execute command using Bash
                process = subprocess.Popen(command_formatted, shell=True, stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE)
                # Wait for the command to complete
                stdout, stderr = process.communicate()
                # Check if the command was executed successfully
                if process.returncode == 0:
                    print("Command executed successfully.")
                else:
                    print(f"Error executing command: {stderr.decode()}")
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


# Call the function with the path to the commands file
execute_commands_from_file(commands_file_path, certs_dir, endpoint)
