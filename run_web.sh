#!/bin/bash
# GrillRadar Web Server Launcher

echo "=================================="
echo "🔥 GrillRadar Web Server"
echo "=================================="
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found"
    echo "   Creating from template..."
    cp .env.example .env
    echo "   ✓ Created .env file"
    echo "   ⚠️  Please edit .env and add your API keys before generating reports"
    echo ""
fi

# Check if dependencies are installed
echo "📦 Checking dependencies..."
python3 -c "import fastapi, anthropic, pydantic" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "   ⚠️  Some dependencies are missing"
    echo "   Installing requirements..."
    pip install -r requirements.txt
fi
echo "   ✓ Dependencies OK"
echo ""

# Start server
echo "🚀 Starting GrillRadar web server..."
echo ""
echo "   Server will be available at:"
echo "   👉 http://localhost:8000"
echo ""
echo "   Press CTRL+C to stop"
echo ""
echo "=================================="
echo ""

# Run with uvicorn
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
