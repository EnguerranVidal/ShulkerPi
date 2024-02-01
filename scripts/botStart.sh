#!/bin/bash

# Set default sleep time (in seconds)
WAIT_TIME=20

# Define the base directory
SHULKER_PI_DIR={shulkerpi-directory}

# Check if a command-line argument is provided for sleep time
if [ "$#" -gt 0 ]; then
    WAIT_TIME=$1
fi

# Sleep for the specified time
sleep "$WAIT_TIME"

# Set permissions for scripts
chmod +x "$SHULKER_PI_DIR/scripts/mcStop.sh"
chmod +x "$SHULKER_PI_DIR/scripts/mcStart.sh"
chmod +x "$SHULKER_PI_DIR/scripts/mcStatus.sh"
chmod +x "$SHULKER_PI_DIR/scripts/mcReset.sh"

# Activate virtual environment and run the Python script
source {conda-activate-path} {environment name}
cd "$SHULKER_PI_DIR"
python3 main.py