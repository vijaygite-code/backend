#!/bin/sh
# Debug info
echo "Starting application with start.sh..."
echo "Current directory: $(pwd)"

# Handle PORT variable (default to 8000)
PORT="${PORT:-8000}"

# Check if main.py is in the current directory (flattened) or in fitness_app
if [ -f "main.py" ]; then
    echo "Found main.py in root. Running directly."
    exec uvicorn main:app --host 0.0.0.0 --port "$PORT"
elif [ -d "fitness_app" ]; then
    echo "Found fitness_app directory. Running as module."
    exec uvicorn fitness_app.main:app --host 0.0.0.0 --port "$PORT"
else
    echo "Could not find main.py or fitness_app directory!"
    ls -la
    exit 1
fi
