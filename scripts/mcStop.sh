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
fi

# Create the stop_flag file to prevent automatic restarts
cd "$server_directory"
touch stop_flag

echo "Server stopped, and stop flag created. The server will not automatically restart."
