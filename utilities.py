import requests

def editEnvFile(envPath, lineName, content):
    with open(envPath, 'r') as envFile:
        lines = envFile.readlines()
    with open(envPath, 'w') as envFile:
        for line in lines:
            if line.startswith(f'{lineName}='):
                envFile.write(f"{lineName}={content}\n")
            else:
                envFile.write(line)