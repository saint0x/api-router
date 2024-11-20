import { NextResponse } from 'next/server'

export async function GET() {
  return NextResponse.json({
    data: {
      id: 1,
      name: "test",
      timestamp: new Date().toISOString()
    }
  })
}
