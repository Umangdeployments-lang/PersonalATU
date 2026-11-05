from flask import Flask, jsonify, render_template_string, request
import json
import time
import threading
from datetime import datetime

app = Flask(__name__)

# In-memory state for the dashboard
dashboard_state = {
    "equity": 100.0,
    "allocation_mode": "FULL_100",
    "amt_regime": "BALANCE",
    "gex_regime": "POSITIVE_GAMMA",
    "ws_latency_p99": 0.0,
    "critic_gate_status": "LOCKED",
    "critic_score": 0.0,
    "pillars": {
        "P1": {"name": "Order Flow (L2/L3 DOM)", "pass_1": False, "pass_2": False, "pass_3": False},
        "P2": {"name": "Volume Profile", "pass_1": False, "pass_2": False, "pass_3": False},
        "P3": {"name": "Net Gamma Exposure (GEX)", "pass_1": False, "pass_2": False, "pass_3": False},
        "P4": {"name": "Footprint Chart", "pass_1": False, "pass_2": False, "pass_3": False},
        "P5": {"name": "Liquidity Heatmaps", "pass_1": False, "pass_2": False, "pass_3": False},
        "P6": {"name": "Big Trades (Block/Sweep)", "pass_1": False, "pass_2": False, "pass_3": False},
        "P7": {"name": "Delta & CVD", "pass_1": False, "pass_2": False, "pass_3": False},
        "P8": {"name": "VWAP Suite", "pass_1": False, "pass_2": False, "pass_3": False},
        "P9": {"name": "Auction Market Theory", "pass_1": False, "pass_2": False, "pass_3": False},
        "E1": {"name": "VPIN Toxicity", "pass_1": False, "pass_2": False, "pass_3": False},
        "E2": {"name": "LPSR Anti-Spoof", "pass_1": False, "pass_2": False, "pass_3": False},
        "E3": {"name": "Vanna/Charm Flow", "pass_1": False, "pass_2": False, "pass_3": False},
        "E4": {"name": "Iceberg Detector", "pass_1": False, "pass_2": False, "pass_3": False},
        "E5": {"name": "EV Queue Gate", "pass_1": False, "pass_2": False, "pass_3": False},
    },
    "triple_check": {"t0": False, "t100": False, "t250": False},
    "vpin_toxicity": 0.0,
    "lpsr_score": 0.0,
    "dom_depth": [],
    "trades": [],
    "last_update": datetime.now().isoformat()
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AEGIS-9 Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        :root {
            --obsidian: #090D16;
            --slate: #111827;
            --border: #1F2937;
            --cyan: #00F5D4;
            --coral: #FF2A85;
            --amber: #F59E0B;
        }
        body { background: var(--obsidian); color: #E5E7EB; font-family: 'Inter', sans-serif; }
        .mono { font-family: 'JetBrains Mono', monospace; font-variant-numeric: tabular-nums; }
        .panel { background: var(--slate); border: 1px solid var(--border); }
        .pillar-pass { color: var(--cyan); }
        .pillar-fail { color: var(--coral); }
        .badge-unlocked { background: var(--cyan); color: var(--obsidian); }
        .badge-locked { background: var(--coral); color: white; }
    </style>
</head>
<body class="h-screen w-screen overflow-hidden flex flex-col">
    <!-- Top Telemetry Bar -->
    <div class="h-12 flex items-center justify-between px-4 panel border-b border-border">
        <div class="flex items-center gap-6">
            <span class="mono text-lg font-semibold">AEGIS-9</span>
            <span class="mono text-xl" id="equity">$100.00</span>
            <select id="mode" class="bg-obsidian border border-border rounded px-2 py-1 text-sm mono">
                <option value="FULL_100">Full 100%</option>
                <option value="HALF_50">Half 50%</option>
                <option value="KELLY_25">Kelly 25%</option>
            </select>
            <span id="amt-badge" class="px-2 py-0.5 rounded text-xs mono bg-amber/20 text-amber">BALANCE</span>
            <span id="gex-badge" class="px-2 py-0.5 rounded text-xs mono bg-cyan/20 text-cyan">+GEX</span>
        </div>
        <div class="flex items-center gap-4">
            <span class="mono text-sm">WS p99: <span id="ws-latency">0.0</span>ms</span>
            <span id="critic-badge" class="badge-locked px-3 py-1 rounded mono text-sm">LOCKED 0.0/10</span>
            <button id="kill-switch" class="bg-coral hover:bg-coral/80 px-4 py-1 rounded mono text-sm">EMERGENCY FLATTEN</button>
        </div>
    </div>

    <div class="flex-1 flex overflow-hidden">
        <!-- Left Structural Ladder -->
        <div class="w-1/5 panel border-r border-border p-3 overflow-y-auto">
            <h3 class="text-xs font-semibold uppercase tracking-wider text-amber mb-3">VOLUME PROFILE</h3>
            <div class="space-y-1 text-xs mono" id="vp-data">Loading...</div>
            <h3 class="text-xs font-semibold uppercase tracking-wider text-amber mt-4 mb-3">NET GEX</h3>
            <div class="space-y-1 text-xs mono" id="gex-data">Loading...</div>
        </div>

        <!-- Center WebGL Canvas -->
        <div class="w-11/20 panel relative">
            <div class="absolute inset-0 flex items-center justify-center text-400">
                <span class="mono">WebGL Canvas (Heatmap + Footprint + VWAP Bands)</span>
            </div>
        </div>

        <!-- Right Confluence Radar & DOM -->
        <div class="w-1/4 panel border-l border-border p-3 overflow-y-auto">
            <h3 class="text-xs font-semibold uppercase tracking-wider text-amber mb-3">CONFLUENCE RADAR</h3>
            <div class="space-y-1 text-xs" id="radar">Loading...</div>
            <div class="mt-4">
                <h3 class="text-xs font-semibold uppercase tracking-wider text-amber mb-2">TRIPLE-CHECK</h3>
                <div class="space-y-1 text-xs mono" id="triple-check">Loading...</div>
            </div>
            <div class="mt-4">
                <h3 class="text-xs font-semibold uppercase tracking-wider text-amber mb-2">L2 DOM</h3>
                <div class="space-y-0.5 text-xs mono" id="dom">Loading...</div>
            </div>
        </div>
    </div>

    <!-- Bottom Analytics & Critic Dock -->
    <div class="h-[232px] panel border-t border-border p-4 overflow-y-auto">
        <div class="grid grid-cols-3 gap-4">
            <div>
                <h4 class="text-xs font-semibold uppercase tracking-wider text-amber mb-2">LIVE EXECUTION LOG</h4>
                <div class="text-xs mono space-y-1" id="exec-log">No trades</div>
            </div>
            <div>
                <h4 class="text-xs font-semibold uppercase tracking-wider text-amber mb-2">OOS EQUITY CURVE</h4>
                <div class="text-xs mono" id="equity-curve">$100.00 → $100.00</div>
            </div>
            <div>
                <h4 class="text-xs font-semibold uppercase tracking-wider text-amber mb-2">CRITIC SCORECARD</h4>
                <div class="text-xs mono space-y-1" id="critic-scorecard">Loading...</div>
            </div>
        </div>
    </div>

    <script>
        async function fetchState() {
            try {
                const res = await fetch('/api/state');
                return await res.json();
            } catch (e) {
                console.error(e);
                return null;
            }
        }

        function renderState(s) {
            if (!s) return;
            document.getElementById('equity').textContent = '$' + s.equity.toFixed(2);
            document.getElementById('mode').value = s.allocation_mode;
            document.getElementById('amt-badge').textContent = s.amt_regime;
            document.getElementById('gex-badge').textContent = s.gex_regime;
            document.getElementById('ws-latency').textContent = s.ws_latency_p99.toFixed(1);
            
            const criticBadge = document.getElementById('critic-badge');
            criticBadge.textContent = (s.critic_gate_status === 'UNLOCKED' ? 'UNLOCKED ' : 'LOCKED ') + s.critic_score.toFixed(1) + '/10';
            criticBadge.className = s.critic_gate_status === 'UNLOCKED' ? 'badge-unlocked px-3 py-1 rounded mono text-sm' : 'badge-locked px-3 py-1 rounded mono text-sm';

            // Confluence Radar
            const radarHtml = Object.entries(s.pillars).map(([k, v]) => {
                const p1 = v.pass_1 ? '✓' : '✗';
                const p2 = v.pass_2 ? '✓' : '✗';
                const p3 = v.pass_3 ? '✓' : '✗';
                const pass = v.pass_1 && v.pass_2 && v.pass_3;
                return `<span class="${pass ? 'pillar-pass' : 'pillar-fail'}">${k} <span class="mono">[${p1}${p2}${p3}]</span></span> ${v.name}`;
            }).join('<br>');
            document.getElementById('radar').innerHTML = radarHtml;

            // Triple Check
            document.getElementById('triple-check').innerHTML = 
                `T+0ms: ${s.triple_check.t0 ? '<span class="pillar-pass">PASS</span>' : '<span class="pillar-fail">WAIT</span>'}<br>` +
                `T+100ms: ${s.triple_check.t100 ? '<span class="pillar-pass">PASS</span>' : '<span class="pillar-fail">WAIT</span>'}<br>` +
                `T+250ms: ${s.triple_check.t250 ? '<span class="pillar-pass">PASS</span>' : '<span class="pillar-fail">WAIT</span>'}`;

            // DOM
            if (s.dom_depth.length > 0) {
                document.getElementById('dom').innerHTML = s.dom_depth.slice(0, 20).map(d => 
                    `<span class="${d.side === 'bid' ? 'pillar-pass' : 'pillar-fail'}">${d.price.toFixed(2)} ${d.size.toFixed(4)}</span>`
                ).join('<br>');
            }

            // Execution log
            if (s.trades.length > 0) {
                document.getElementById('exec-log').innerHTML = s.trades.slice(-5).reverse().map(t => 
                    `${t.time} ${t.side} ${t.symbol} @ ${t.price} PnL: ${t.pnl >= 0 ? '<span class="pillar-pass">+' : '<span class="pillar-fail">'}${t.pnl.toFixed(2)}</span>`
                ).join('<br>');
            }

            // Equity curve
            document.getElementById('equity-curve').textContent = `$${s.equity.toFixed(2)}`;

            // Critic scorecard
            const criticHtml = Object.entries(s.critic_scores || {}).map(([mod, score]) => 
                `${mod}: ${score.toFixed(1)}/10`
            ).join('<br>');
            document.getElementById('critic-scorecard').innerHTML = criticHtml || 'No scores yet';
        }

        async function updateLoop() {
            const state = await fetchState();
            renderState(state);
            setTimeout(updateLoop, 500);
        }
        updateLoop();

        document.getElementById('mode').addEventListener('change', async (e) => {
            await fetch('/api/set_mode', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({mode: e.target.value})});
        });

        document.getElementById('kill-switch').addEventListener('click', async () => {
            await fetch('/api/emergency_flatten', {method: 'POST'});
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/state')
def get_state():
    return jsonify(dashboard_state)

@app.route('/api/set_mode', methods=['POST'])
def set_mode():
    data = request.get_json()
    dashboard_state['allocation_mode'] = data.get('mode', 'FULL_100')
    return jsonify({"success": True})

@app.route('/api/emergency_flatten', methods=['POST'])
def emergency_flatten():
    # Trigger emergency flatten logic
    return jsonify({"success": True, "message": "Emergency flatten triggered"})

def update_dashboard(equity=None, mode=None, **kwargs):
    if equity is not None:
        dashboard_state['equity'] = equity
    if mode is not None:
        dashboard_state['allocation_mode'] = mode
    for k, v in kwargs.items():
        if k in dashboard_state:
            dashboard_state[k] = v
    dashboard_state['last_update'] = datetime.now().isoformat()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)