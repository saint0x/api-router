import { NextResponse } from 'next/server'

export async function POST(request: Request) {
  const data = await request.json()
  
  // Simulate processing
  await new Promise(resolve => setTimeout(resolve, 1))
  
  return NextResponse.json({
    processed: true,
    input: data,
    timestamp: new Date().toISOString()
  })
}
