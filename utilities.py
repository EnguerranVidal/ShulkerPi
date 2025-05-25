import csv
import json
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
        return pd.read_csv(csvPath)

def saveUsernameCsv(usernames: DataFrame, csvPath):
    usernames.to_csv(csvPath, index=False)

def retrievePlayerStats(levelStatsFolderPath, mcUuid, mcUsername):
    playerInfo = {}
    for filename in os.listdir(levelStatsFolderPath):
        if filename[:-5].replace('-', '') == mcUuid:
            playerInfo['NAME'] = mcUsername
            with open(os.path.join(levelStatsFolderPath, filename), 'r') as file:
                playerStats = json.load(file)
            if playerStats['stats'].get('minecraft:custom', None) is not None:
                # DEATH STATISTICS
                playerInfo['DEATHS'] = playerStats['stats']['minecraft:custom'].get('minecraft:deaths', '0')
                playerInfo['MOB_KILLS'] = playerStats['stats']['minecraft:custom'].get('minecraft:mob_kills', '0')
                playerInfo['PLAYER_KILLS'] = playerStats['stats']['minecraft:custom'].get('minecraft:player_kills', '0')
                playerInfo['DAMAGE_TAKEN'] = playerStats['stats']['minecraft:custom'].get('minecraft:damage_taken', '0')
                playerInfo['DAMAGE_DEALT'] = playerStats['stats']['minecraft:custom'].get('minecraft:damage_dealt', '0')
                # TIME STATISTICS
                playTime = playerStats['stats']['minecraft:custom'].get('minecraft:play_time', 0)
                lastDeath = playerStats['stats']['minecraft:custom'].get('minecraft:time_since_death', 0)
                worldTime = playerStats['stats']['minecraft:custom'].get('minecraft:total_world_time', 0)
                playerInfo['PLAY_TIME'] = formatTimeDuration(int(playTime) / 20)
                playerInfo['WORLD_TIME'] = formatTimeDuration(int(worldTime) / 20)
                playerInfo['LAST_DEATH'] = formatTimeDuration(int(lastDeath) / 20)
                # MOVEMENT STATISTICS
                walkDistance = playerStats['stats']['minecraft:custom'].get('minecraft:walk_one_cm', 0)
                swimDistance = playerStats['stats']['minecraft:custom'].get('minecraft:swim_one_cm', 0)
                fallDistance = playerStats['stats']['minecraft:custom'].get('minecraft:fall_one_cm', 0)
                boatDistance = playerStats['stats']['minecraft:custom'].get('minecraft:boat_one_cm', 0)
                elytraDistance = playerStats['stats']['minecraft:custom'].get('minecraft:aviate_one_cm', 0)
                horseDistance = playerStats['stats']['minecraft:custom'].get('minecraft:horse_one_cm', 0)
                minecartDistance = playerStats['stats']['minecraft:custom'].get('minecraft:minecart_one_cm', 0)
                playerInfo['WALK_DISTANCE'] = formatDistance(int(walkDistance) / 100)
                playerInfo['SWIM_DISTANCE'] = formatDistance(int(swimDistance) / 100)
                playerInfo['FALL_DISTANCE'] = formatDistance(int(fallDistance) / 100)
                playerInfo['BOAT_DISTANCE'] = formatDistance(int(boatDistance) / 100)
                playerInfo['ELYTRA_DISTANCE'] = formatDistance(int(elytraDistance) / 100)
                playerInfo['HORSE_DISTANCE'] = formatDistance(int(horseDistance) / 100)
                playerInfo['MINECART_DISTANCE'] = formatDistance(int(minecartDistance) / 100)
                # "MOST" STATISTICS
                playerInfo['MOST_MINED'] = getMinecraftMost(playerStats['stats'].get('minecraft:mined', None))
                playerInfo['MOST_USED'] = getMinecraftMost(playerStats['stats'].get('minecraft:used', None))
                playerInfo['MOST_CRAFTED'] = getMinecraftMost(playerStats['stats'].get('minecraft:crafted', None))
                playerInfo['MOST_KILLED'] = getMinecraftMost(playerStats['stats'].get('minecraft:killed', None))
                playerInfo['MOST_KILLED_BY'] = getMinecraftMost(playerStats['stats'].get('minecraft:killed_by', None))
                playerInfo['MOST_BROKEN'] = getMinecraftMost(playerStats['stats'].get('minecraft:broken', None))
            return playerInfo
    return None


def formatTimeDuration(seconds):
    units, parts = [('y', 31536000), ('mo', 2592000), ('d', 86400), ('h', 3600), ('min', 60), ('s', 1)], []
    for name, unit_seconds in units:
        value, seconds = divmod(seconds, unit_seconds)
        if value > 0 or (name == 's' and not parts):
            parts.append(f"{int(value)}{name}")
    return ', '.join(parts)

def formatDistance(meters):
    if meters >= 1000:
        return f"{meters / 1000 :.2f} km"
    else:
        return f"{meters} m"

def getMinecraftMost(minecraftDict):
    if minecraftDict is not None:
        mostKey = max(minecraftDict, key=minecraftDict.get).split(':')[1]
        mostKey = mostKey.replace('_', '').capitalize()
        return mostKey
    else:
        return 'N/A'