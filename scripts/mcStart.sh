#!/bin/bash

# Check if correct number of arguments are provided
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <server_directory> <server_jar_file> <memory_allocation>"
    exit 1
fi

server_directory="$1"
server_jar="$2"
memory_allocation="$3"

cd "$server_directory" || exit 1  # Exit if changing directory fails

# Remove the stop_flag file, if it exists
if [ -e "stop_flag" ]; then
    echo "Removing existing stop_flag file."
    rm "stop_flag"
fi

while true
do
    # Check for the stop flag before restarting
    if [ -e "stop_flag" ]; then
        echo "Stop flag found. Exiting without restarting the server."
        exit 0
    fi

    java -Xmx"${memory_allocation}" -Xms"${memory_allocation}" -jar "$server_jar"
    sleep 10
done