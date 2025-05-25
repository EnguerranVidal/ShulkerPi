import csv
import os
import pandas as pd
from mcstatus import JavaServer
from pandas import DataFrame


def editEnvFile(envPath, lineName, content):
    with open(envPath, 'r') as envFile:
        lines = envFile.readlines()
    with open(envPath, 'w') as envFile:
        for line in lines:
            if line.startswith(f'{lineName}='):
                envFile.write(f"{lineName}={content}\n")
            else:
                envFile.write(line)

async def isServerOnline(serverIp: str):
    try:
        server = JavaServer.lookup(serverIp)
        await server.async_status()
        return True
    except:
        return False

def initializeUsernameCsv(csvPath):
    if not os.path.isfile(csvPath):
        with open(csvPath, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['DISCORD_NAME', 'DISCORD_ID', 'MINECRAFT_USERNAME', 'MINECRAFT_UUID'])


def readUsernamesCsv(csvPath):
    columns = ['DISCORD_NAME', 'DISCORD_ID', 'MINECRAFT_USERNAME', 'MINECRAFT_UUID']
    if not os.path.exists(csvPath):
        return pd.DataFrame(columns=columns)
    else:
        return pd.DataFrame(columns=['DISCORD_NAME', 'DISCORD_ID', 'MINECRAFT_USERNAME', 'MINECRAFT_UUID'])

def saveUsernameCsv(usernames: DataFrame, csvPath):
    usernames.to_csv(csvPath, index=False)
