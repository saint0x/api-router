#!/usr/bin/env python3
import asyncio
import aiohttp
import time
import statistics
from datetime import datetime
import psutil
import sys
import platform
from rich.console import Console
from tabulate import tabulate

console = Console()

class BenchmarkResults:
    def __init__(self, name):
        self.name = name
        self.latencies = {}
        self.errors = {}
        self.memory_usage = {}
        self.cpu_usage = {}
        self.start_time = None
        self.end_time = None
        self.requests_completed = 0
        
        for endpoint in ['ping', 'data', 'process']:
            self.latencies[endpoint] = []
            self.errors[endpoint] = 0
            self.memory_usage[endpoint] = []
            self.cpu_usage[endpoint] = []

    def add_latency(self, endpoint, latency, memory, cpu):
        self.latencies[endpoint].append(latency)
        self.memory_usage[endpoint].append(memory)
        self.cpu_usage[endpoint].append(cpu)
        self.requests_completed += 1

    def add_error(self, endpoint):
        self.errors[endpoint] += 1
        self.requests_completed += 1

    def calculate_stats(self):
        stats = {}
        for endpoint, latencies in self.latencies.items():
            if latencies:
                sorted_latencies = sorted(latencies)
                stats[endpoint] = {
                    'min_ms': min(latencies) * 1000,
                    'max_ms': max(latencies) * 1000,
                    'mean_ms': statistics.mean(latencies) * 1000,
                    'median_ms': statistics.median(latencies) * 1000,
                    'p95_ms': sorted_latencies[int(len(latencies) * 0.95)] * 1000,
                    'p99_ms': sorted_latencies[int(len(latencies) * 0.99)] * 1000,
                    'requests': len(latencies),
                    'errors': self.errors[endpoint],
                    'avg_memory_mb': statistics.mean(self.memory_usage[endpoint]),
                    'avg_cpu_percent': statistics.mean(self.cpu_usage[endpoint])
                }
        return stats

    def calculate_throughput(self):
        duration = self.end_time - self.start_time
        return self.requests_completed / duration

async def get_process_metrics(pid):
    try:
        process = psutil.Process(pid)
        memory = process.memory_info().rss / 1024 / 1024  # MB
        cpu = process.cpu_percent()
        return memory, cpu
    except:
        return 0, 0

async def make_request(session, url, method='GET', data=None, pid=None):
    start_time = time.time()
    try:
        async with session.request(method, url, json=data) as response:
            await response.read()
            duration = time.time() - start_time
            memory, cpu = await get_process_metrics(pid)
            return duration, memory, cpu
    except Exception as e:
        console.print(f"[red]Error making request to {url}: {e}[/red]")
        return None, 0, 0

async def run_benchmark(name, port, pid, concurrency, requests_per_endpoint):
    urls = {
        'ping': f'http://localhost:{port}/ping',
        'data': f'http://localhost:{port}/api/v1/data',
        'process': f'http://localhost:{port}/api/v1/process'
    }

    results = BenchmarkResults(name)
    results.start_time = time.time()

    async with aiohttp.ClientSession() as session:
        for endpoint, url in urls.items():
            console.print(f"[bold green]Running {endpoint} benchmark for {name}...")
            method = 'POST' if endpoint == 'process' else 'GET'
            data = {'test': 'data'} if endpoint == 'process' else None
            
            tasks = []
            for _ in range(requests_per_endpoint):
                tasks.extend([make_request(session, url, method, data, pid) for _ in range(concurrency)])
            
            responses = await asyncio.gather(*tasks)
            
            for response in responses:
                if response[0] is not None:
                    results.add_latency(endpoint, response[0], response[1], response[2])
                else:
                    results.add_error(endpoint)

    results.end_time = time.time()
    return results

def calculate_difference(base_value, compare_value):
    if base_value == 0:
        return float('inf')
    return ((compare_value/base_value)-1)*100

def generate_markdown_report(results_dict):
    with open('results2.md', 'w') as f:
        f.write('# API Router Performance Comparison\n\n')
        
        # System Information
        f.write('## System Information\n\n')
        f.write(f'- OS: {platform.system()} {platform.release()}\n')
        f.write(f'- CPU: {platform.processor()}\n')
        f.write(f'- Python Version: {platform.python_version()}\n')
        f.write(f'- Timestamp: {datetime.now().isoformat()}\n\n')

        # Overall Results
        f.write('## Overall Performance\n\n')
        f.write('| Metric | Go | Rust | Python | Next.js |\n')
        f.write('|--------|----|----|--------|----------|\n')
        
        go_throughput = results_dict['Go'].calculate_throughput()
        throughputs = {name: result.calculate_throughput() for name, result in results_dict.items()}
        
        f.write(f'| Throughput (req/s) | {throughputs["Go"]:.2f} | {throughputs["Rust"]:.2f} | {throughputs["Python"]:.2f} | {throughputs["Next.js"]:.2f} |\n\n')

        # Detailed Results
        f.write('## Detailed Performance Metrics\n\n')
        stats = {name: result.calculate_stats() for name, result in results_dict.items()}

        for endpoint in ['ping', 'data', 'process']:
            f.write(f'### {endpoint.capitalize()} Endpoint\n\n')
            f.write('| Metric | Go | Rust | Python | Next.js |\n')
            f.write('|--------|----|----|--------|----------|\n')
            
            metrics = [
                ('Mean Latency (ms)', 'mean_ms'),
                ('Median Latency (ms)', 'median_ms'),
                ('P95 Latency (ms)', 'p95_ms'),
                ('P99 Latency (ms)', 'p99_ms'),
                ('Min Latency (ms)', 'min_ms'),
                ('Max Latency (ms)', 'max_ms'),
                ('Memory Usage (MB)', 'avg_memory_mb'),
                ('CPU Usage (%)', 'avg_cpu_percent'),
                ('Errors', 'errors')
            ]
            
            for metric_name, metric_key in metrics:
                values = [stats[impl][endpoint][metric_key] for impl in ['Go', 'Rust', 'Python', 'Next.js']]
                f.write(f'| {metric_name} | {values[0]:.2f} | {values[1]:.2f} | {values[2]:.2f} | {values[3]:.2f} |\n')
            
            f.write('\n')

async def main():
    concurrency = 10
    requests_per_endpoint = 1000
    
    implementations = {
        'Go': (3000, int(sys.argv[1])),
        'Rust': (3001, int(sys.argv[2])),
        'Python': (3002, int(sys.argv[3])),
        'Next.js': (3003, int(sys.argv[4]))
    }
    
    results = {}
    for name, (port, pid) in implementations.items():
        console.print(f"[bold green]Starting {name} router benchmark...")
        results[name] = await run_benchmark(name, port, pid, concurrency, requests_per_endpoint)
    
    generate_markdown_report(results)
    console.print("\n[bold green]Detailed results saved to results2.md[/bold green]")

if __name__ == '__main__':
    if len(sys.argv) != 5:
        console.print("[red]Usage: ./benchmark2.py <go_pid> <rust_pid> <python_pid> <nextjs_pid>[/red]")
        sys.exit(1)
    asyncio.run(main())
