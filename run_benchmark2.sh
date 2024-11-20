#!/bin/bash

# Function to kill process using a port
kill_port() {
    port=$1
    pid=$(lsof -t -i:$port)
    if [ ! -z "$pid" ]; then
        echo "Killing process using port $port"
        kill -9 $pid 2>/dev/null || true
    fi
}

# Kill any existing processes on the required ports
echo "Cleaning up existing processes..."
kill_port 3000
kill_port 3001
kill_port 3002
kill_port 3003

# Wait a moment for ports to be freed
sleep 2

# Install Python dependencies for benchmark
echo "Installing Python benchmark dependencies..."
pip install aiohttp asyncio psutil rich tabulate

# Install Python router dependencies
echo "Installing Python router dependencies..."
cd python-router
pip install -r requirements.txt
cd ..

# Build Go router
echo "Building Go router..."
cd go-router
go build -o router cmd/main.go
if [ $? -ne 0 ]; then
    echo "Failed to build Go router"
    exit 1
fi
cd ..

# Build Rust router
echo "Building Rust router..."
cd rust-router
cargo build --release
if [ $? -ne 0 ]; then
    echo "Failed to build Rust router"
    exit 1
fi
cd ..

# Build Next.js router
echo "Building Next.js router..."
cd next-router
npm install
npm run build
if [ $? -ne 0 ]; then
    echo "Failed to build Next.js router"
    exit 1
fi
cd ..

# Start all servers in background
echo "Starting all servers..."

# Start Go router
./go-router/router &
GO_PID=$!

# Start Rust router
./rust-router/target/release/rust-router &
RUST_PID=$!

# Start Python router
cd python-router
uvicorn main:app --host 0.0.0.0 --port 3002 --workers 4 &
PYTHON_PID=$!
cd ..

# Start Next.js router
cd next-router
npm start &
NEXTJS_PID=$!
cd ..

# Wait for servers to initialize
echo "Waiting for servers to initialize..."
sleep 5

# Run benchmark
echo "Running benchmark..."
python3 benchmark2.py $GO_PID $RUST_PID $PYTHON_PID $NEXTJS_PID

# Cleanup
echo "Cleaning up..."
kill $GO_PID 2>/dev/null || true
kill $RUST_PID 2>/dev/null || true
kill $PYTHON_PID 2>/dev/null || true
kill $NEXTJS_PID 2>/dev/null || true

# Kill any remaining processes on the ports
kill_port 3000
kill_port 3001
kill_port 3002
kill_port 3003

echo "Benchmark complete! Check results2.md for detailed results."
