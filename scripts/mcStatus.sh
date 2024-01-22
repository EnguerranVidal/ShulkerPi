#!/bin/bash

# Check if correct number of arguments are provided
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <server_directory> <server_jar_file> <memory_allocation>"
    exit 2
fi

server_directory="$1"
server_jar="$2"
memory_allocation="$3"

# Check if the server is running
if pgrep -f "java -Xmx${memory_allocation} -Xms${memory_allocation} -jar $server_jar" >/dev/null; then
    echo "Server is running."
    exit 0
else
    echo "Server is not running."
    exit 1
fi