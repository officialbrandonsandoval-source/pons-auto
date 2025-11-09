#!/bin/bash
# Shiftly Auto - Quick Start Script

echo "🚗 Starting Shiftly Auto Dashboard"
echo "=================================="
echo ""

# Check if requirements are installed
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

echo "🚀 Launching dashboard..."
echo ""
echo "📱 Access on this device: http://localhost:8501"
echo "📱 Access on mobile:"
echo "   1. Make sure your phone is on the same WiFi"
echo "   2. Find your IP: ifconfig | grep 'inet '"
echo "   3. Visit: http://YOUR-IP:8501 on your phone"
echo ""
echo "=================================="

streamlit run app.py
