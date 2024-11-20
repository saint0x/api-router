"use client"

import { useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { cn } from "@/lib/utils"

const overallPerformance = [
  { metric: 'Throughput (req/s)', Go: 2117.00, Rust: 2494.39, difference: 17.8 }
]

type EndpointDataType = {
  metric: string
  Go: number
  Rust: number
  difference: number
}

type EndpointType = 'ping' | 'data' | 'process'

const endpointData: Record<EndpointType, EndpointDataType[]> = {
  ping: [
    { metric: 'Mean Latency (ms)', Go: 1747.35, Rust: 1679.92, difference: -3.9 },
    { metric: 'Median Latency (ms)', Go: 1787.81, Rust: 1758.71, difference: -1.6 },
    { metric: 'P95 Latency (ms)', Go: 2839.14, Rust: 2673.05, difference: -5.8 },
    { metric: 'P99 Latency (ms)', Go: 2970.45, Rust: 2744.32, difference: -7.6 },
    { metric: 'Min Latency (ms)', Go: 501.64, Rust: 475.06, difference: -5.3 },
    { metric: 'Max Latency (ms)', Go: 2981.54, Rust: 2754.45, difference: -7.6 },
    { metric: 'Memory Usage (MB)', Go: 12.41, Rust: 6.21, difference: -50.0 },
  ],
  data: [
    { metric: 'Mean Latency (ms)', Go: 2071.92, Rust: 1347.12, difference: -35.0 },
    { metric: 'Median Latency (ms)', Go: 2075.57, Rust: 1373.03, difference: -33.8 },
    { metric: 'P95 Latency (ms)', Go: 3305.88, Rust: 2116.20, difference: -36.0 },
    { metric: 'P99 Latency (ms)', Go: 3411.34, Rust: 2191.24, difference: -35.8 },
    { metric: 'Min Latency (ms)', Go: 554.21, Rust: 433.33, difference: -21.8 },
    { metric: 'Max Latency (ms)', Go: 3427.85, Rust: 2204.75, difference: -35.7 },
    { metric: 'Memory Usage (MB)', Go: 13.46, Rust: 6.98, difference: -48.1 },
  ],
  process: [
    { metric: 'Mean Latency (ms)', Go: 3232.10, Rust: 3071.32, difference: -5.0 },
    { metric: 'Median Latency (ms)', Go: 3106.42, Rust: 3097.98, difference: -0.3 },
    { metric: 'P95 Latency (ms)', Go: 5387.03, Rust: 5076.93, difference: -5.8 },
    { metric: 'P99 Latency (ms)', Go: 5580.99, Rust: 5220.85, difference: -6.5 },
    { metric: 'Min Latency (ms)', Go: 910.88, Rust: 748.67, difference: -17.8 },
    { metric: 'Max Latency (ms)', Go: 5628.19, Rust: 5268.64, difference: -6.4 },
    { metric: 'Memory Usage (MB)', Go: 13.83, Rust: 9.02, difference: -34.8 },
  ]
}

const AsciiArt = () => (
  <pre className={cn("text-xs sm:text-sm md:text-base lg:text-lg xl:text-xl font-mono text-primary")}>
    {`
     _____  _____ _____   _____             _            
    |  __ \\|  __ \\_   _| |  __ \\           | |           
    | |__) | |__) || |   | |__) |___  _   _| |_ ___ _ __ 
    |  ___/|  ___/ | |   |  _  // _ \\| | | | __/ _ \\ '__|
    | |    | |    _| |_  | | \\ \\ (_) | |_| | ||  __/ |   
    |_|    |_|   |_____| |_|  \\_\\___/ \\__,_|\\__\\___|_|   
                                                         
    `}
  </pre>
)

export default function Dashboard() {
  const [selectedEndpoint, setSelectedEndpoint] = useState<EndpointType>('ping')

  return (
    <div className={cn("container mx-auto p-4 space-y-8")}>
      <Card className={cn("overflow-hidden")}>
        <CardHeader className="pb-0">
          <AsciiArt />
          <CardTitle className={cn("text-3xl font-bold text-center")}>API Router Performance Comparison</CardTitle>
          <CardDescription className="text-center">
            Comparing high-performance API routers in Go and Rust
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className={cn("grid grid-cols-1 md:grid-cols-2 gap-4 mt-4")}>
            <div>
              <h3 className={cn("text-lg font-semibold mb-2")}>Project Overview</h3>
              <ul className={cn("list-disc list-inside space-y-1")}>
                <li>Developed and benchmarked two high-performance API routers</li>
                <li>Provides crucial insights for scalable web services</li>
                <li>Comprehensive testing with 10 concurrent connections</li>
                <li>1000 requests per endpoint</li>
              </ul>
            </div>
            <div>
              <h3 className={cn("text-lg font-semibold mb-2")}>Key Findings</h3>
              <ul className={cn("list-disc list-inside space-y-1")}>
                <li>17.8% higher overall throughput in Rust</li>
                <li>Up to 35% lower latency for data operations</li>
                <li>50% lower memory footprint</li>
                <li>Consistent performance across all percentiles</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Overall Performance</CardTitle>
        </CardHeader>
        <CardContent>
          <ChartContainer
            config={{
              Go: {
                label: "Go",
                color: "hsl(var(--chart-1))",
              },
              Rust: {
                label: "Rust",
                color: "hsl(var(--chart-2))",
              },
            }}
            className="h-[300px]"
          >
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={overallPerformance}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="metric" />
                <YAxis />
                <ChartTooltip content={<ChartTooltipContent />} />
                <Legend />
                <Bar dataKey="Go" fill="var(--color-Go)" />
                <Bar dataKey="Rust" fill="var(--color-Rust)" />
              </BarChart>
            </ResponsiveContainer>
          </ChartContainer>
          <div className={cn("mt-4 text-center")}>
            <Badge variant="secondary" className={cn("text-lg")}>
              Rust outperforms Go by 17.8% in overall throughput
            </Badge>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Detailed Metrics Comparison</CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="ping" onValueChange={(value) => setSelectedEndpoint(value as EndpointType)}>
            <TabsList>
              <TabsTrigger value="ping">Ping Endpoint</TabsTrigger>
              <TabsTrigger value="data">Data Endpoint</TabsTrigger>
              <TabsTrigger value="process">Process Endpoint</TabsTrigger>
            </TabsList>
            <TabsContent value={selectedEndpoint}>
              <ChartContainer
                config={{
                  Go: {
                    label: "Go",
                    color: "hsl(var(--chart-1))",
                  },
                  Rust: {
                    label: "Rust",
                    color: "hsl(var(--chart-2))",
                  },
                }}
                className="h-[400px]"
              >
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={endpointData[selectedEndpoint]} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" />
                    <YAxis dataKey="metric" type="category" width={150} />
                    <ChartTooltip content={<ChartTooltipContent />} />
                    <Legend />
                    <Bar dataKey="Go" fill="var(--color-Go)" />
                    <Bar dataKey="Rust" fill="var(--color-Rust)" />
                  </BarChart>
                </ResponsiveContainer>
              </ChartContainer>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Performance by Endpoint</CardTitle>
        </CardHeader>
        <CardContent>
          <ChartContainer
            config={{
              Go: {
                label: "Go",
                color: "hsl(var(--chart-1))",
              },
              Rust: {
                label: "Rust",
                color: "hsl(var(--chart-2))",
              },
            }}
            className="h-[300px]"
          >
            <ResponsiveContainer width="100%" height="100%">
              <LineChart>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="metric" type="category" allowDuplicatedCategory={false} />
                <YAxis />
                <ChartTooltip content={<ChartTooltipContent />} />
                <Legend />
                <Line dataKey="Go" data={endpointData.ping} name="Go - Ping" stroke="var(--color-Go)" />
                <Line dataKey="Rust" data={endpointData.ping} name="Rust - Ping" stroke="var(--color-Rust)" />
                <Line dataKey="Go" data={endpointData.data} name="Go - Data" stroke="var(--color-Go)" strokeDasharray="5 5" />
                <Line dataKey="Rust" data={endpointData.data} name="Rust - Data" stroke="var(--color-Rust)" strokeDasharray="5 5" />
                <Line dataKey="Go" data={endpointData.process} name="Go - Process" stroke="var(--color-Go)" strokeDasharray="3 3" />
                <Line dataKey="Rust" data={endpointData.process} name="Rust - Process" stroke="var(--color-Rust)" strokeDasharray="3 3" />
              </LineChart>
            </ResponsiveContainer>
          </ChartContainer>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Business Impact</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className={cn("list-disc list-inside space-y-2")}>
            <li>Infrastructure cost reduction through lower memory usage</li>
            <li>Higher throughput enables serving more users with fewer servers</li>
            <li>Better user experience with faster response times</li>
            <li>More predictable performance under load</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  )
}
