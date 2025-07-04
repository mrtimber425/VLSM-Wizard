#!/bin/bash

echo "🔧 Checking for Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install it first."
    exit 1
fi

echo "🔧 Creating virtual environment..."
[ ! -d venv ] && python3 -m venv venv

echo "✅ Activating environment..."
source venv/bin/activate

echo "📦 Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install pyqt5 numpy > /dev/null 2>&1

echo "🚀 Launching Subnet Calculator..."
if [ ! -f vlsmwiz.py ]; then
    echo "❌ subnet_calculator.py not found in the current directory."
    exit 1
fi

python vlsmwiz.py
