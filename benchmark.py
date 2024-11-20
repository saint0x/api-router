#!/usr/bin/env python3
import asyncio
import aiohttp
import time
import statistics
from datetime import datetime
import psutil
import sys
import platform
from tabulate import tabulate
from rich.console import Console
from rich.table import Table
from rich import print as rprint

console = Console()

class BenchmarkResults:
    def __init__(self):
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

    results = BenchmarkResults()
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

def generate_markdown_report(go_results, rust_results):
    with open('results.md', 'w') as f:
        f.write('# API Router Performance Comparison\n\n')
        
        # System Information
        f.write('## System Information\n\n')
        f.write(f'- OS: {platform.system()} {platform.release()}\n')
        f.write(f'- CPU: {platform.processor()}\n')
        f.write(f'- Python Version: {platform.python_version()}\n')
        f.write(f'- Timestamp: {datetime.now().isoformat()}\n\n')

        # Overall Results
        f.write('## Overall Performance\n\n')
        go_throughput = go_results.calculate_throughput()
        rust_throughput = rust_results.calculate_throughput()
        
        f.write('| Metric | Go | Rust | Difference |\n')
        f.write('|--------|----|----|------------|\n')
        f.write(f'| Throughput (req/s) | {go_throughput:.2f} | {rust_throughput:.2f} | {((rust_throughput/go_throughput)-1)*100:.1f}% |\n\n')

        # Detailed Results
        f.write('## Detailed Performance Metrics\n\n')
        go_stats = go_results.calculate_stats()
        rust_stats = rust_results.calculate_stats()

        for endpoint in ['ping', 'data', 'process']:
            f.write(f'### {endpoint.capitalize()} Endpoint\n\n')
            f.write('| Metric | Go | Rust | Difference |\n')
            f.write('|--------|----|----|------------|\n')
            
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
                go_value = go_stats[endpoint][metric_key]
                rust_value = rust_stats[endpoint][metric_key]
                if metric_key.endswith('ms'):
                    diff = ((rust_value/go_value)-1)*100 if go_value != 0 else float('inf')
                    f.write(f'| {metric_name} | {go_value:.2f} | {rust_value:.2f} | {diff:.1f}% |\n')
                else:
                    diff = rust_value - go_value
                    f.write(f'| {metric_name} | {go_value:.2f} | {rust_value:.2f} | {diff:+.2f} |\n')
            
            f.write('\n')

def print_results(go_results, rust_results):
    console.print("\n[bold cyan]Benchmark Results[/bold cyan]\n")
    
    # Create overall results table
    table = Table(title="Overall Performance")
    table.add_column("Metric")
    table.add_column("Go")
    table.add_column("Rust")
    table.add_column("Difference")

    go_throughput = go_results.calculate_throughput()
    rust_throughput = rust_results.calculate_throughput()
    
    table.add_row(
        "Throughput (req/s)",
        f"{go_throughput:.2f}",
        f"{rust_throughput:.2f}",
        f"{((rust_throughput/go_throughput)-1)*100:+.1f}%"
    )
    
    console.print(table)
    
    # Print detailed results for each endpoint
    go_stats = go_results.calculate_stats()
    rust_stats = rust_results.calculate_stats()
    
    for endpoint in ['ping', 'data', 'process']:
        table = Table(title=f"{endpoint.capitalize()} Endpoint Performance")
        table.add_column("Metric")
        table.add_column("Go")
        table.add_column("Rust")
        table.add_column("Difference")
        
        metrics = [
            ('Mean Latency', 'mean_ms', 'ms'),
            ('Median Latency', 'median_ms', 'ms'),
            ('P95 Latency', 'p95_ms', 'ms'),
            ('P99 Latency', 'p99_ms', 'ms'),
            ('Memory Usage', 'avg_memory_mb', 'MB'),
            ('CPU Usage', 'avg_cpu_percent', '%'),
            ('Errors', 'errors', '')
        ]
        
        for metric_name, metric_key, unit in metrics:
            go_value = go_stats[endpoint][metric_key]
            rust_value = rust_stats[endpoint][metric_key]
            
            if unit in ['ms', 'MB', '%']:
                diff = ((rust_value/go_value)-1)*100 if go_value != 0 else float('inf')
                diff_str = f"{diff:+.1f}%"
            else:
                diff = rust_value - go_value
                diff_str = f"{diff:+.0f}"
                
            table.add_row(
                f"{metric_name}",
                f"{go_value:.2f}{unit}",
                f"{rust_value:.2f}{unit}",
                diff_str
            )
        
        console.print(table)
        console.print("")

async def main():
    concurrency = 10
    requests_per_endpoint = 1000
    
    console.print("[bold green]Starting Go router benchmark...")
    go_pid = int(sys.argv[1])
    go_results = await run_benchmark("Go", 3000, go_pid, concurrency, requests_per_endpoint)
    
    console.print("[bold green]Starting Rust router benchmark...")
    rust_pid = int(sys.argv[2])
    rust_results = await run_benchmark("Rust", 3001, rust_pid, concurrency, requests_per_endpoint)
    
    print_results(go_results, rust_results)
    generate_markdown_report(go_results, rust_results)
    console.print("\n[bold green]Detailed results saved to results.md[/bold green]")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        console.print("[red]Usage: ./benchmark.py <go_pid> <rust_pid>[/red]")
        sys.exit(1)
    asyncio.run(main())
