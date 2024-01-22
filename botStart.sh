#!/bin/bash

# Set default sleep time (in seconds)
WAIT_TIME=20

# Define the base directory
SHULKERPI_DIR={shulkerpi-directory}

# Check if a command-line argument is provided for sleep time
if [ "$#" -gt 0 ]; then
    WAIT_TIME=$1
fi

# Sleep for the specified time
sleep "$WAIT_TIME"

# Set permissions for scripts
chmod +x "$SHULKERPI_DIR/scripts/mcStop.sh"
chmod +x "$SHULKERPI_DIR/scripts/mcStart.sh"
chmod +x "$SHULKERPI_DIR/scripts/mcStatus.sh"
chmod +x "$SHULKERPI_DIR/scripts/mcReset.sh"

# Activate virtual environment and run the Python script
source {conda-activate-path} {environment name}
cd "$SHULKERPI_DIR"
python3 main.py # 2>>"$SHULKERPI_DIR/error_log.txt"