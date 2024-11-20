#!/bin/bash

# Install Python dependencies
echo "Installing Python dependencies..."
pip install aiohttp asyncio psutil rich tabulate

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

# Start Go router in background
echo "Starting Go router..."
./go-router/router &
GO_PID=$!

# Start Rust router in background
echo "Starting Rust router..."
./rust-router/target/release/rust-router &
RUST_PID=$!

# Wait for servers to start
echo "Waiting for servers to initialize..."
sleep 2

# Run benchmark
echo "Running benchmark..."
python3 benchmark.py $GO_PID $RUST_PID

# Cleanup
echo "Cleaning up..."
kill $GO_PID
kill $RUST_PID

echo "Benchmark complete! Check results.md for detailed results."
