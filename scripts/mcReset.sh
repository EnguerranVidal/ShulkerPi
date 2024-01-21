#!/bin/bash

# Check if correct number of arguments are provided
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <server_directory> <server_jar_file> <memory_allocation>"
    exit 1
fi

server_directory="$1"
server_jar="$2"
memory_allocation="$3"

# Stop the running server if it's currently running
if pgrep -f "java -Xmx${memory_allocation} -Xms${memory_allocation} -jar $server_jar" >/dev/null; then
    echo "Stopping the Minecraft server..."
    pkill -f "java -Xmx${memory_allocation} -Xms${memory_allocation} -jar $server_jar"
    sleep 5  # Wait for the server to shut down (adjust as needed)
    echo "Server stopped. The server will now automatically restart."
fi


