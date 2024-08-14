#!/bin/bash

# Define the log file
LOG_FILE="squeue_log.csv"

# Function to run the squeue command and append the result to the log file
log_squeue() {
    squeue --me --format="%.10i %.7P %.50j %.8u %.2t %.10M %E" >> "$LOG_FILE"
}

# Infinite loop to run the command every 10 seconds
while true; do
    log_squeue
    sleep 5
done
