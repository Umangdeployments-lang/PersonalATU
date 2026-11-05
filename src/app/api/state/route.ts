import { NextResponse } from "next/server";

const mockState = {
  equity: 100.0,
  allocation_mode: "FULL_100",
  amt_regime: "BALANCE",
  gex_regime: "POSITIVE_GAMMA",
  ws_latency_p99: 1.2,
  critic_gate_status: "LOCKED",
  critic_score: 0.0,
  pillars: {
    P1: { name: "Order Flow (L2/L3 DOM)", pass_1: false, pass_2: false, pass_3: false },
    P2: { name: "Volume Profile", pass_1: false, pass_2: false, pass_3: false },
    P3: { name: "Net Gamma Exposure (GEX)", pass_1: false, pass_2: false, pass_3: false },
    P4: { name: "Footprint Chart", pass_1: false, pass_2: false, pass_3: false },
    P5: { name: "Liquidity Heatmaps", pass_1: false, pass_2: false, pass_3: false },
    P6: { name: "Big Trades (Block/Sweep)", pass_1: false, pass_2: false, pass_3: false },
    P7: { name: "Delta & CVD", pass_1: false, pass_2: false, pass_3: false },
    P8: { name: "VWAP Suite", pass_1: false, pass_2: false, pass_3: false },
    P9: { name: "Auction Market Theory", pass_1: false, pass_2: false, pass_3: false },
    E1: { name: "VPIN Toxicity", pass_1: false, pass_2: false, pass_3: false },
    E2: { name: "LPSR Anti-Spoof", pass_1: false, pass_2: false, pass_3: false },
    E3: { name: "Vanna/Charm Flow", pass_1: false, pass_2: false, pass_3: false },
    E4: { name: "Iceberg Detector", pass_1: false, pass_2: false, pass_3: false },
    E5: { name: "EV Queue Gate", pass_1: false, pass_2: false, pass_3: false },
  },
  triple_check: { t0: false, t100: false, t250: false },
  vpin_toxicity: 0.0,
  lpsr_score: 0.0,
  dom_depth: [
    { price: 50000.00, size: 1.234, side: "bid" },
    { price: 50000.01, size: 0.567, side: "ask" },
    { price: 49999.99, size: 2.345, side: "bid" },
    { price: 50000.02, size: 1.111, side: "ask" },
    { price: 49999.98, size: 3.456, side: "bid" },
    { price: 50000.03, size: 0.789, side: "ask" },
    { price: 49999.97, size: 1.234, side: "bid" },
    { price: 50000.04, size: 2.345, side: "ask" },
    { price: 49999.96, size: 0.567, side: "bid" },
    { price: 50000.05, size: 1.111, side: "ask" },
    { price: 49999.95, size: 3.456, side: "bid" },
    { price: 50000.06, size: 0.789, side: "ask" },
    { price: 49999.94, size: 1.234, side: "bid" },
    { price: 50000.07, size: 2.345, side: "ask" },
    { price: 49999.93, size: 0.567, side: "bid" },
    { price: 50000.08, size: 1.111, side: "ask" },
    { price: 49999.92, size: 3.456, side: "bid" },
    { price: 50000.09, size: 0.789, side: "ask" },
    { price: 49999.91, size: 1.234, side: "bid" },
    { price: 50000.10, size: 2.345, side: "ask" },
  ],
  trades: [],
  critic_scores: {
    "CORE-01": 0.0,
    "CORE-02": 0.0,
    "DATA-01": 0.0,
    "P1": 0.0,
    "P2": 0.0,
    "P3": 0.0,
    "P4": 0.0,
    "P5": 0.0,
    "P6": 0.0,
    "P7": 0.0,
    "P8": 0.0,
    "P9": 0.0,
    "E1-E5": 0.0,
    "CONF-01": 0.0,
    "EXEC-01": 0.0,
    "UI-01": 0.0,
    "MASTER": 0.0,
  },
};

export async function GET() {
  return NextResponse.json(mockState);
}

export async function POST(request: Request) {
  const body = await request.json();
  if (body.mode) {
    mockState.allocation_mode = body.mode;
  }
  return NextResponse.json({ success: true });
}