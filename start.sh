#!/bin/sh
echo "Starting backend script..."
echo "Current directory: $(pwd)"
# Re-apply PYTHONPATH just in case, though relative imports should work now.
export PYTHONPATH=$PYTHONPATH:$(pwd):$(pwd)/fitness_app
echo "PYTHONPATH set to: $PYTHONPATH"

# Detect entry point
if [ -f "fitness_app/main.py" ]; then
    echo "Found fitness_app/main.py, running as module usage."
    exec uvicorn fitness_app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
elif [ -f "main.py" ]; then
    echo "Found main.py in root, running direct usage."
    exec uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}"
else
    echo "ERROR: Could not find main.py"
    ls -R
    exit 1
fi
