import * as React from "react"

interface ChartProps extends React.HTMLAttributes<HTMLDivElement> {
  config: Record<string, { label: string; color: string }>
}

export function ChartContainer({
  config,
  className,
  children,
  ...props
}: ChartProps) {
  React.useEffect(() => {
    const root = document.documentElement
    for (const [key, value] of Object.entries(config)) {
      root.style.setProperty(`--color-${key}`, value.color)
    }
  }, [config])

  return (
    <div className={`relative ${className}`} {...props}>
      {children}
    </div>
  )
}

export function ChartTooltip({ active, payload, label }: any) {
  if (active && payload && payload.length) {
    return (
      <div className="rounded-lg border bg-background p-2 shadow-sm">
        <div className="grid grid-cols-2 gap-2">
          {payload.map((entry: any) => (
            <div key={entry.name} className="flex flex-col">
              <span className="text-[0.70rem] uppercase text-muted-foreground">
                {entry.name}
              </span>
              <span className="font-bold text-muted-foreground">
                {entry.value}
              </span>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return null
}

export const ChartTooltipContent = ChartTooltip
