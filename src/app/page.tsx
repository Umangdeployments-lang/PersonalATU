"use client";

import { useEffect, useState } from "react";

interface DashboardState {
  equity: number;
  allocation_mode: string;
  amt_regime: string;
  gex_regime: string;
  ws_latency_p99: number;
  critic_gate_status: string;
  critic_score: number;
  pillars: Record<string, { name: string; pass_1: boolean; pass_2: boolean; pass_3: boolean }>;
  triple_check: { t0: boolean; t100: boolean; t250: boolean };
  vpin_toxicity: number;
  lpsr_score: number;
  dom_depth: Array<{ price: number; size: number; side: "bid" | "ask" }>;
  trades: Array<{ time: string; side: string; symbol: string; price: number; pnl: number }>;
  critic_scores: Record<string, number>;
}

export default function Dashboard() {
  const [state, setState] = useState<DashboardState | null>(null);

  useEffect(() => {
    const fetchState = async () => {
      try {
        const res = await fetch("/api/state");
        const data = await res.json();
        setState(data);
      } catch (e) {
        console.error(e);
      }
    };

    fetchState();
    const interval = setInterval(fetchState, 500);
    return () => clearInterval(interval);
  }, []);

  if (!state) return <div className="flex h-screen items-center justify-center mono">Loading AEGIS-9...</div>;

  return (
    <div className="h-screen w-screen flex flex-col bg-[#090D16] text-[#E5E7EB] font-['Inter']">
      {/* Top Telemetry Bar */}
      <div className="h-12 flex items-center justify-between px-4 border-b border-[#1F2937] bg-[#111827]">
        <div className="flex items-center gap-6">
          <span className="mono text-lg font-semibold">AEGIS-9</span>
          <span className="mono text-xl">${state.equity.toFixed(2)}</span>
          <select
            id="mode"
            className="bg-[#090D16] border border-[#1F2937] rounded px-2 py-1 text-sm mono"
            value={state.allocation_mode}
            onChange={(e) => fetch("/api/set_mode", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ mode: e.target.value }) })}
          >
            <option value="FULL_100">Full 100%</option>
            <option value="HALF_50">Half 50%</option>
            <option value="KELLY_25">Kelly 25%</option>
          </select>
          <span className="px-2 py-0.5 rounded text-xs mono bg-[#F59E0B]/20 text-[#F59E0B]">{state.amt_regime}</span>
          <span className="px-2 py-0.5 rounded text-xs mono bg-[#00F5D4]/20 text-[#00F5D4]">{state.gex_regime}</span>
        </div>
        <div className="flex items-center gap-4">
          <span className="mono text-sm">WS p99: <span className="text-[#00F5D4]">{state.ws_latency_p99.toFixed(1)}</span>ms</span>
          <span className={`px-3 py-1 rounded mono text-sm ${state.critic_gate_status === "UNLOCKED" ? "bg-[#00F5D4] text-[#090D16]" : "bg-[#FF2A85] text-white"}`}>
            {state.critic_gate_status} {state.critic_score.toFixed(1)}/10
          </span>
          <button
            id="kill-switch"
            className="bg-[#FF2A85] hover:bg-[#FF2A85]/80 px-4 py-1 rounded mono text-sm"
            onClick={() => fetch("/api/emergency_flatten", { method: "POST" })}
          >
            EMERGENCY FLATTEN
          </button>
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        {/* Left Structural Ladder */}
        <div className="w-1/5 border-r border-[#1F2937] bg-[#111827] p-3 overflow-y-auto">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-[#F59E0B] mb-3">VOLUME PROFILE</h3>
          <div className="space-y-1 text-xs mono text-[#9CA3AF]">Developing POC: --<br />VAH: --<br />VAL: --<br />HVN: --<br />LVN: --</div>
          <h3 className="text-xs font-semibold uppercase tracking-wider text-[#F59E0B] mt-4 mb-3">NET GEX</h3>
          <div className="space-y-1 text-xs mono text-[#9CA3AF]">Zero-Gamma: --<br />Call Wall: --<br />Put Wall: --<br />Net GEX: --</div>
        </div>

        {/* Center WebGL Canvas */}
        <div className="w-11/20 bg-[#111827] relative">
          <div className="absolute inset-0 flex items-center justify-center text-[#6B7280]">
            <span className="mono">WebGL Canvas (Heatmap + Footprint + VWAP ±1..3σ)</span>
          </div>
        </div>

        {/* Right Confluence Radar & DOM */}
        <div className="w-1/4 border-l border-[#1F2937] bg-[#111827] p-3 overflow-y-auto">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-[#F59E0B] mb-3">CONFLUENCE RADAR</h3>
          <div className="space-y-1 text-xs">
            {Object.entries(state.pillars).map(([k, v]) => (
              <div key={k} className={v.pass_1 && v.pass_2 && v.pass_3 ? "text-[#00F5D4]" : "text-[#FF2A85]"}>{k} [{v.pass_1 ? "✓" : "✗"}{v.pass_2 ? "✓" : "✗"}{v.pass_3 ? "✓" : "✗"}] {v.name}</div>
            ))}
          </div>
          <div className="mt-4">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-[#F59E0B] mb-2">TRIPLE-CHECK</h3>
            <div className="space-y-1 text-xs mono">
              <div>T+0ms: {state.triple_check.t0 ? <span className="text-[#00F5D4]">PASS</span> : <span className="text-[#FF2A85]">WAIT</span>}</div>
              <div>T+100ms: {state.triple_check.t100 ? <span className="text-[#00F5D4]">PASS</span> : <span className="text-[#FF2A85]">WAIT</span>}</div>
              <div>T+250ms: {state.triple_check.t250 ? <span className="text-[#00F5D4]">PASS</span> : <span className="text-[#FF2A85]">WAIT</span>}</div>
            </div>
          </div>
          <div className="mt-4">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-[#F59E0B] mb-2">L2 DOM (Top 20)</h3>
            <div className="space-y-0.5 text-xs mono">
              {state.dom_depth.slice(0, 20).map((d, i) => (
                <div key={i} className={d.side === "bid" ? "text-[#00F5D4]" : "text-[#FF2A85]"}>{d.price.toFixed(2)} {d.size.toFixed(4)}</div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Analytics & Critic Dock */}
      <div className="h-[232px] border-t border-[#1F2937] bg-[#111827] p-4 overflow-y-auto">
        <div className="grid grid-cols-3 gap-4">
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-[#F59E0B] mb-2">LIVE EXECUTION LOG</h4>
            <div className="text-xs mono space-y-1">
              {state.trades.length > 0 ? state.trades.slice(-5).reverse().map((t, i) => (
                <div key={i}>{t.time} {t.side} {t.symbol} @ {t.price} PnL: <span className={t.pnl >= 0 ? "text-[#00F5D4]" : "text-[#FF2A85]"}>{t.pnl.toFixed(2)}</span></div>
              )) : <div className="text-[#6B7280]">No trades</div>}
            </div>
          </div>
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-[#F59E0B] mb-2">OOS EQUITY CURVE</h4>
            <div className="text-xs mono">${state.equity.toFixed(2)}</div>
          </div>
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-[#F59E0B] mb-2">CRITIC SCORECARD</h4>
            <div className="text-xs mono space-y-1">
              {Object.entries(state.critic_scores).map(([mod, score]) => (
                <div key={mod}>{mod}: {score.toFixed(1)}/10</div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}