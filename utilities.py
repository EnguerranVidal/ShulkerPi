import requests


def getServerStatus(serverIp):
    apiUrl = f'https://api.mcstatus.io/v2/status/java/{serverIp}'
    try:
        response = requests.get(apiUrl)
        data = response.json()
        return data
    except Exception as e:
        print(f"Error checking server status: {e}")
        return None