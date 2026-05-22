#!/bin/bash
# B2B Due Diligence Agent — Quick Setup

set -e

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  B2B Due Diligence Verification Agent — Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "✕ Python 3 not found. Install Python 3.9+ first."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "  ✓ Python $PYTHON_VERSION found"

# Check pip
if ! command -v pip3 &> /dev/null && ! python3 -m pip --version &> /dev/null; then
    echo "✕ pip not found. Install pip first."
    exit 1
fi

echo "  ✓ pip found"

# Install dependencies
echo ""
echo "  Installing dependencies..."
pip3 install -r requirements.txt --quiet

echo "  ✓ Dependencies installed"

# Check API key
echo ""
if [ -z "$OPENAI_API_KEY" ]; then
    echo "  ⚠ OPENAI_API_KEY not set."
    echo ""
    echo "  Set it before running:"
    echo "    export OPENAI_API_KEY=sk-your-openai-key-here"
else
    echo "  ✓ OPENAI_API_KEY found"
fi

# Create directories
mkdir -p reports logs
echo "  ✓ Output directories created"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Setup complete. Run the agent:"
echo ""
echo "    python3 main.py                        # Interactive"
echo "    python3 main.py --file examples/acme.json  # From file"
echo "    python3 main.py --help                 # All options"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
