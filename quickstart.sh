#!/bin/bash
# Quick start script for ChainSight AI

set -e

echo "=============================================="
echo "ChainSight AI - Quick Start"
echo "=============================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Check if pip is installed
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo "Error: pip is not installed"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Run component tests
echo "🧪 Running component tests..."
python test_components.py
echo ""

# Generate sample events
echo "📊 Generating sample supply chain events..."
python main.py --batch 10
echo ""

# Instructions for dashboard
echo "=============================================="
echo "✓ Setup Complete!"
echo "=============================================="
echo ""
echo "To view the live dashboard, run:"
echo "  streamlit run src/visualization/dashboard.py"
echo ""
echo "For continuous event generation:"
echo "  python main.py --continuous --batch 5 --interval 10"
echo ""
echo "For cloud-enabled mode (requires GCP setup):"
echo "  1. Copy .env.example to .env"
echo "  2. Add your GCP credentials"
echo "  3. Run: python main.py --setup --all"
echo "  4. Run: python main.py --batch 20 --all"
echo ""
