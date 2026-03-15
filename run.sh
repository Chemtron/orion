#!/bin/bash
cd "$(dirname "${BASH_SOURCE[0]}")"
mkdir -p data/logs
echo "==============================="
echo " ORION — Starting server..."
echo " Open: http://127.0.0.1:5000"
echo " Ctrl+C to stop"
echo "==============================="
python orion.py
