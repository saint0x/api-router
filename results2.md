# API Router Performance Comparison

## System Information

- OS: Linux 6.5.0-1025-azure
- CPU: x86_64
- Python Version: 3.12.1
- Timestamp: 2024-11-20T17:20:42.686099

## Overall Performance

| Metric | Go | Rust | Python | Next.js |
|--------|----|----|--------|----------|
| Throughput (req/s) | 2463.07 | 2914.51 | 927.90 | 1234.72 |

## Detailed Performance Metrics

### Ping Endpoint

| Metric | Go | Rust | Python | Next.js |
|--------|----|----|--------|----------|
| Mean Latency (ms) | 1501.96 | 1077.51 | 5038.12 | 4100.23 |
| Median Latency (ms) | 1509.55 | 1112.06 | 5126.41 | 4206.54 |
| P95 Latency (ms) | 2411.17 | 1447.81 | 8932.98 | 6310.53 |
| P99 Latency (ms) | 2484.39 | 1486.62 | 9342.80 | 6476.77 |
| Min Latency (ms) | 440.75 | 577.56 | 643.09 | 688.14 |
| Max Latency (ms) | 2492.39 | 1490.24 | 9397.71 | 6536.83 |
| Memory Usage (MB) | 0.00 | 0.00 | 0.00 | 0.00 |
| CPU Usage (%) | 0.00 | 0.00 | 0.00 | 0.00 |
| Errors | 0.00 | 0.00 | 0.00 | 0.00 |

### Data Endpoint

| Metric | Go | Rust | Python | Next.js |
|--------|----|----|--------|----------|
| Mean Latency (ms) | 1511.56 | 1044.20 | 5017.11 | 2803.17 |
| Median Latency (ms) | 1539.80 | 1034.77 | 5111.52 | 2758.59 |
| P95 Latency (ms) | 2427.27 | 1609.68 | 8926.75 | 4997.17 |
| P99 Latency (ms) | 2503.92 | 1659.82 | 9410.49 | 5165.99 |
| Min Latency (ms) | 478.09 | 409.07 | 503.95 | 451.12 |
| Max Latency (ms) | 2517.03 | 1669.51 | 9502.06 | 5189.39 |
| Memory Usage (MB) | 0.00 | 0.00 | 0.00 | 0.00 |
| CPU Usage (%) | 0.00 | 0.00 | 0.00 | 0.00 |
| Errors | 0.00 | 0.00 | 0.00 | 0.00 |

### Process Endpoint

| Metric | Go | Rust | Python | Next.js |
|--------|----|----|--------|----------|
| Mean Latency (ms) | 2996.72 | 3021.42 | 6143.78 | 5847.64 |
| Median Latency (ms) | 2950.76 | 3029.24 | 6286.83 | 5878.41 |
| P95 Latency (ms) | 5184.44 | 5021.33 | 10881.87 | 10116.20 |
| P99 Latency (ms) | 5377.53 | 5168.34 | 11311.02 | 10569.93 |
| Min Latency (ms) | 670.23 | 772.36 | 898.79 | 866.20 |
| Max Latency (ms) | 5422.81 | 5214.98 | 11366.94 | 10612.21 |
| Memory Usage (MB) | 0.00 | 0.00 | 0.00 | 0.00 |
| CPU Usage (%) | 0.00 | 0.00 | 0.00 | 0.00 |
| Errors | 0.00 | 0.00 | 0.00 | 0.00 |

