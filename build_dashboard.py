#!/usr/bin/env python3
"""Build the single-file dashboard.html, styled in Pronto's brand
(green #18A860, near-black headlines, soft green surfaces, Pronto logo + icon).
Data + brand assets are embedded inline so the file is fully portable."""
import base64
import json
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / "data"
BRAND = ROOT / "brand"
raw = json.load(open(DATA / "reviews_raw.json"))
cls = json.load(open(DATA / "reviews_classified.json"))
liq = json.load(open(DATA / "liquidity_split.json"))


def b64(p):
    return base64.b64encode(Path(p).read_bytes()).decode()


LOGO = "data:image/png;base64," + b64(BRAND / "pronto-logo.png")
LOGO_WHITE = "data:image/png;base64," + b64(BRAND / "pronto-logo-white.png")
ICON = "data:image/png;base64," + b64(BRAND / "pronto-icon.png")

pr_raw = [r for r in raw if r["brand"] == "pronto"]
uc_raw = [r for r in raw if r["brand"] == "urban_company"]
pr = [r for r in cls if r["brand"] == "pronto"]
pr_neg = [r for r in pr if r["sentiment"] == "negative"]
uc_neg = [r for r in cls if r["brand"] == "urban_company" and r["sentiment"] == "negative"]

THEME_LABEL = {
    "reliability": "Reliability (no-show / cancel)", "support_refunds": "Support & refunds",
    "pro_quality": "Pro quality", "supply_availability": "No slots / not in area",
    "app_booking_ux": "App & booking UX", "pricing_value": "Pricing & value",
    "scheduling": "Scheduling", "other": "Other",
}


def rating_dist(rows):
    c = Counter(r["rating"] for r in rows if r.get("rating"))
    return [c.get(i, 0) for i in range(1, 6)]


def theme_counts(rows):
    c = Counter(r["theme"] for r in rows)
    items = [(THEME_LABEL.get(k, k), v) for k, v in c.most_common()]
    return [i[0] for i in items], [i[1] for i in items]


def quotes(rows, theme, n=2, maxlen=220):
    out = []
    for r in rows:
        if r["theme"] == theme and len(r["text"]) > 60:
            out.append(" ".join(r["text"].split())[:maxlen])
        if len(out) >= n:
            break
    return out


pr_theme_l, pr_theme_v = theme_counts(pr_neg)
uc_theme_l, uc_theme_v = theme_counts(uc_neg)
avg = round(sum(r["rating"] for r in pr_raw) / len(pr_raw), 2)
one_star = sum(1 for r in pr_raw if r["rating"] == 1)
features = sorted({r["feature_request"] for r in cls if r["feature_request"]})

D = {
    "generated": date.today().isoformat(),
    "kpis": {"total_scraped": len(raw), "pronto_reviews": len(pr_raw), "uc_reviews": len(uc_raw),
             "pronto_avg": avg, "one_star": one_star, "one_star_pct": round(100 * one_star / len(pr_raw)),
             "sample": len(cls)},
    "rating_pr": rating_dist(pr_raw),
    "pr_theme": {"labels": pr_theme_l, "values": pr_theme_v},
    "uc_theme": {"labels": uc_theme_l, "values": uc_theme_v},
    "reliability_share": {
        "pronto": round(100 * sum(1 for r in pr_neg if r["theme"] == "reliability") / len(pr_neg)),
        "uc": round(100 * sum(1 for r in uc_neg if r["theme"] == "reliability") / len(uc_neg))},
    "liq": liq,
    "quotes": {"reliability": quotes(pr_neg, "reliability", 3),
               "support_refunds": quotes(pr_neg, "support_refunds", 2),
               "pro_quality_pos": [" ".join(r["text"].split())[:200] for r in pr if r["sentiment"] == "positive" and r["theme"] == "pro_quality"][:3]},
    "features": features, "n_pr_neg": len(pr_neg), "n_uc_neg": len(uc_neg),
}

HTML = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Pronto · Growth Teardown</title>
<link rel="icon" href="__ICON__"/>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@500;600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
:root{--brand:#18A860;--brandD:#0F8A4E;--ink:#0B1A12;--mut:#5d6f64;--line:#e3ece6;
--soft:#E8F5EE;--softL:#cfe9d9;--uc:#64748b;--alert:#E5484D;--amb:#C9A227;--bg:#f6faf7;--card:#fff;--dark:#0B1A12}
*{box-sizing:border-box}
body{margin:0;font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;color:var(--ink);background:var(--bg);line-height:1.55}
.wrap{max-width:1080px;margin:0 auto;padding:0 24px 64px}
h1,h2,h3,.kpi .n,.big{font-family:'Poppins',sans-serif}
.topbar{display:flex;align-items:center;justify-content:space-between;padding:20px 0 8px;border-bottom:1px solid var(--line);margin-bottom:26px}
.brandrow{display:flex;align-items:center;gap:12px}
.brandrow img{height:30px}
.brandrow .div{width:1px;height:24px;background:var(--line)}
.brandrow .lbl{font-family:'Poppins';font-weight:600;font-size:15px;color:var(--ink)}
.pill{background:var(--soft);color:var(--brandD);font-weight:700;font-size:11px;padding:5px 12px;border-radius:20px;letter-spacing:.3px}
header h1{font-size:33px;line-height:1.12;margin:18px 0 8px;letter-spacing:-.6px;font-weight:800}
header h1 .g{color:var(--brand)}
header .sub{color:var(--mut);font-size:15px;max-width:760px}
.kpis{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin:24px 0}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:16px}
.kpi .n{font-size:25px;font-weight:800;letter-spacing:-.5px}
.kpi .l{font-size:11px;color:var(--mut);text-transform:uppercase;letter-spacing:.4px;margin-top:3px;font-weight:600}
.kpi.alert .n{color:var(--alert)} .kpi.good .n{color:var(--brand)}
.thesis{background:var(--soft);border:1px solid var(--softL);border-radius:16px;padding:20px 22px;margin:6px 0 16px}
.thesis b{color:var(--brandD)}
.delta{background:#fffaf0;border:1px solid #f0e2c8;border-left:4px solid var(--amb);border-radius:12px;padding:12px 16px;margin:0 0 18px;font-size:12.5px;color:#6b5d2f}
.delta b{color:var(--ink)}
.honesty{background:var(--dark);color:#d6e4dc;border-radius:16px;padding:22px;margin:0 0 28px;position:relative;overflow:hidden}
.honesty .wm{position:absolute;right:18px;top:16px;height:20px;opacity:.5}
.honesty h3{color:#fff;margin:0 0 6px;font-size:17px}
.honesty .cap{color:#9ab3a6;font-size:12.5px;margin:0 0 12px;max-width:760px}
.honesty table{width:100%;border-collapse:collapse;font-size:12.5px}
.honesty td{border-bottom:1px solid #1f3a2b;padding:8px 8px;vertical-align:top}
.honesty td:first-child{color:#cfe0d7}.honesty td:last-child{color:#7fe0ab}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}
.card{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:18px 20px;margin-bottom:18px}
.card h3{margin:0 0 2px;font-size:16px;font-weight:700}
.card .cap{color:var(--mut);font-size:12.5px;margin:0 0 14px}
.full{grid-column:1/-1}
canvas{max-height:300px}
.quote{border-left:3px solid var(--line);padding:6px 0 6px 12px;margin:10px 0;color:#3a4a42;font-size:13.5px;font-style:italic}
.quote.pr{border-color:var(--alert)}.quote.good{border-color:var(--brand)}
ul.feat{columns:2;gap:24px;font-size:13.5px;color:#3a4a42;margin:6px 0 0;padding-left:18px}
ul.feat li{margin:4px 0;break-inside:avoid}
.method{font-size:12px;color:var(--mut);background:#fff;border:1px dashed var(--line);border-radius:12px;padding:14px 16px;margin-top:24px}
.big{font-size:42px;font-weight:800;letter-spacing:-1px}
.cmp{display:flex;gap:24px;align-items:center;justify-content:center;text-align:center;padding:8px 0}
.cmp .v{font-size:13px;color:var(--mut);font-weight:600}.cmp .pr{color:var(--alert)}.cmp .uc{color:var(--uc)}
.flow{background:var(--dark);color:#eaf3ee;border-radius:16px;padding:24px;margin:0 0 18px;position:relative;overflow:hidden}
.flow .wm{position:absolute;right:18px;top:16px;height:20px;opacity:.5}
.flow h3{color:#fff;margin:0 0 14px}
.flowrow{display:flex;flex-wrap:wrap;gap:8px;align-items:center;font-size:13px}
.node{background:#14301f;border:1px solid #245138;border-radius:10px;padding:8px 12px;color:#eaf3ee}
.node.hot{background:var(--brand);border-color:var(--brand);color:#04150b;font-weight:700}
.arrow{color:#5e8a72;font-size:18px}
.exp{display:flex;gap:12px;align-items:flex-start;padding:11px 0;border-bottom:1px solid var(--line)}
.exp:last-child{border-bottom:none}
.exp .badge{flex:0 0 auto;font-size:10.5px;font-weight:700;text-transform:uppercase;letter-spacing:.4px;padding:4px 9px;border-radius:20px;margin-top:2px}
.exp .badge.flag{background:var(--brand);color:#fff}.exp .badge.core{background:var(--ink);color:#fff}.exp .badge.enab{background:var(--soft);color:var(--brandD)}
.exp .body{font-size:13.5px}.exp .body b{color:var(--ink)}
.plan{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:4px 0 14px}
.phase{background:var(--soft);border:1px solid var(--softL);border-radius:12px;padding:14px}
.phase .ph{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.4px;color:var(--brandD)}
.phase .pt{font-size:13.5px;color:#33423a;margin-top:6px}
.metric{background:var(--dark);color:#eaf3ee;border-radius:12px;padding:15px 18px;font-size:13.5px}
.metric b{color:#fff}.metric .star{color:#7fe0ab;font-weight:700;text-transform:uppercase;letter-spacing:.4px;font-size:11px}
.foot{text-align:center;color:var(--mut);font-size:12px;margin-top:30px}
.foot img{height:18px;vertical-align:middle;opacity:.6;margin-right:6px}
.calc{display:grid;grid-template-columns:1fr 1fr;gap:22px;align-items:start;margin-top:6px}
.presets{display:flex;gap:8px;margin:0 0 16px;flex-wrap:wrap}
.preset{font-size:12px;font-weight:600;border:1px solid var(--softL);background:var(--soft);color:var(--brandD);border-radius:20px;padding:6px 13px;cursor:pointer;user-select:none}
.preset.active{background:var(--brand);color:#fff;border-color:var(--brand)}
.ctrl{margin:0 0 15px}
.ctrl label{display:flex;justify-content:space-between;font-size:12.5px;color:var(--ink);font-weight:600;margin-bottom:6px}
.ctrl label .val{color:var(--brandD);font-family:'Poppins';font-weight:700}
input[type=range]{width:100%;accent-color:var(--brand);height:4px;margin:2px 0}
.outs{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-top:6px}
.out{border:1px solid var(--line);border-radius:12px;padding:12px 14px}
.out .on{font-family:'Poppins';font-weight:800;font-size:19px;color:var(--ink);letter-spacing:-.02em}
.out .ol{font-size:10.5px;color:var(--mut);margin-top:3px;line-height:1.3}
.out.hl{background:var(--soft);border-color:var(--softL)}.out.hl .on{color:var(--brandD)}
.tree{margin:8px 0 20px}
.troot{background:var(--ink);color:#fff;border-radius:10px;padding:10px 14px;font-size:12.5px;font-weight:600;text-align:center;margin-bottom:10px}
.tcols{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.tcol{border:1px solid var(--line);border-radius:10px;padding:12px;background:#fff}
.tcol .td{font-size:11.5px;font-weight:700;color:var(--brandD);margin-bottom:6px}
.tcol .tm{font-size:12px;color:var(--body)}
.eval2col{display:grid;grid-template-columns:1fr 1fr;gap:22px;align-items:start;margin-top:6px}
.stbl{width:100%;border-collapse:collapse;font-size:12px}
.stbl th{text-align:left;color:var(--mut);font-weight:600;font-size:10px;text-transform:uppercase;letter-spacing:.03em;padding:6px 7px;border-bottom:1px solid var(--line);cursor:pointer;user-select:none;white-space:nowrap}
.stbl th:hover{color:var(--brandD)}
.stbl td{padding:8px 7px;border-bottom:1px solid var(--line);vertical-align:middle}
.stbl tr:last-child td{border-bottom:none}
.stbl .mname{font-weight:600;color:var(--ink)}
.pz{font-family:'Poppins';font-weight:700;color:var(--brandD)}
.cbadge,.pbadge{font-size:9.5px;font-weight:700;padding:2px 8px;border-radius:20px;white-space:nowrap}
.cbadge.cb-Data{background:var(--soft);color:var(--brandD)}
.cbadge.cb-Inferred{background:#fdf6e3;color:#9a7b1a}
.cbadge.cb-Hypothesis{background:#eef1f4;color:#647280}
.pbadge.p-Do-first{background:var(--brand);color:#fff}
.pbadge.p-Big-bet{background:var(--ink);color:#fff}
.pbadge.p-Quick-win{background:var(--soft);color:var(--brandD)}
.pbadge.p-Later{background:#eef1f4;color:#647280}
.hmg{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:4px}
.hcard{border:1px solid var(--line);border-radius:12px;padding:14px}
.hcard h4{margin:0 0 9px;font-size:12.5px;color:var(--ink);font-family:'Poppins';font-weight:700}
.hcard .hl{display:flex;gap:9px;font-size:11.3px;margin:5px 0;line-height:1.45}
.hcard .hl .t{flex:0 0 58px;font-weight:700;color:var(--mut);text-transform:uppercase;font-size:9px;letter-spacing:.03em;padding-top:2px}
.hcard .hl.s .t{color:var(--brandD)}.hcard .hl.g .t{color:var(--alert)}
.hcard .hl .x{flex:1;color:var(--body)}
@media(max-width:760px){.kpis{grid-template-columns:repeat(2,1fr)}.grid{grid-template-columns:1fr}.plan{grid-template-columns:1fr}.calc{grid-template-columns:1fr}.eval2col{grid-template-columns:1fr}.tcols{grid-template-columns:1fr}.hmg{grid-template-columns:1fr}header h1{font-size:26px}}
</style></head>
<body><div class="wrap">
<div class="topbar">
<div class="brandrow"><img src="__LOGO__" alt="Pronto"/><div class="div"></div><span class="lbl">Growth Teardown</span></div>
<span class="pill">Independent analysis</span>
</div>
<header>
<h1>The growth ceiling is <span class="g">supply liquidity</span>.</h1>
<div class="sub">What 4,464 public reviews say about the one moment that decides whether Pronto keeps a customer: whether a professional is actually at the door, on time.</div>
</header>

<div class="thesis" id="thesis"></div>
<div class="honesty" id="honesty"></div>
<div class="kpis" id="kpis"></div>

<div class="grid">
<div class="card"><h3>How Pronto is rated</h3><p class="cap">All __PRN__ Pronto reviews with text. People either love it or uninstall in frustration.</p><canvas id="ratePr"></canvas></div>
<div class="card"><h3>Root cause: what the reviews can and cannot tell you</h3><p class="cap">Pronto's harshest reviews (one and two star), sorted by what they actually describe.</p><canvas id="liq"></canvas></div>
</div>

<div class="card full"><h3>Same city, opposite problem</h3>
<p class="cap">What unhappy customers complain about, Pronto beside Urban Company. Urban Company has crossed the supply threshold. Pronto has not yet.</p>
<canvas id="themeCmp" style="max-height:340px"></canvas></div>

<div class="grid">
<div class="card"><h3>How often "nobody came" is the complaint</h3><p class="cap">Share of unhappy reviews about a no-show or cancellation.</p>
<div class="cmp"><div><div class="big pr" id="relPr"></div><div class="v pr">Pronto</div></div><div style="font-size:22px;color:#cbd5cd">vs</div><div><div class="big uc" id="relUc"></div><div class="v uc">Urban Company</div></div></div>
<p class="cap" style="margin-top:8px">Urban Company's unhappy customers say a pro <b>overcharged</b> them, which at least means a pro arrived. Pronto's say <b>nobody came</b>.</p></div>
<div class="card"><h3>What unhappy customers say</h3><p class="cap">A few representative one-star reviews.</p><div id="qRel"></div></div>
</div>

<div class="flow" id="flow"></div>

<div class="card full"><h3>The other half of the marketplace: keeping pros busy and nearby</h3>
<p class="cap">A no-show is usually a supply problem wearing a demand costume. Three things steady it.</p>
<div class="move"><div class="mi">A</div><div class="mb"><b>Make supply plannable.</b> A weekly subscription is not just revenue. It tells operations exactly where a pro needs to be next Tuesday, which is how you keep enough professionals free in the areas that matter. Predictable demand is the cheapest way to fix reliability.</div></div>
<div class="move"><div class="mi">B</div><div class="mb"><b>Let your best pros recruit and coach.</b> The professionals who already do great work are your cheapest, most trusted source of new ones. Give top pros a simple way to refer and mentor newcomers, and pay them for it. Supply grows from the inside, and quality travels with it.</div></div>
<div class="move"><div class="mi">C</div><div class="mb"><b>Grow by density, not by map.</b> Win one area at a time. A neighbourhood where supply is thick feels instant and reliable. The same number of pros spread thin across a city feels broken everywhere.</div></div></div>

<div class="card full"><h3>Growth model: what moving one number does</h3>
<p class="cap">A simple projection over twelve months. Drag the first slider, the share of first bookings that actually get completed, and watch everything downstream move. It assumes a steady stream of new first-time bookings each month.</p>
<div class="presets" id="presets">
  <span class="preset" data-p="today">Where Pronto is today</span>
  <span class="preset" data-p="fix">Fix the first booking</span>
  <span class="preset" data-p="flywheel">Full flywheel</span>
</div>
<div class="calc">
 <div>
  <div class="ctrl"><label>First bookings that get completed <span class="val" id="vC1"></span></label><input type="range" id="c1" min="40" max="95" step="1"></div>
  <div class="ctrl"><label>Completed first visits that book again <span class="val" id="vR2"></span></label><input type="range" id="r2" min="20" max="70" step="1"></div>
  <div class="ctrl"><label>Repeat customers who go weekly <span class="val" id="vSub"></span></label><input type="range" id="sub" min="5" max="60" step="1"></div>
  <div class="outs">
    <div class="out hl"><div class="on" id="oActive"></div><div class="ol">active customers by month 12</div></div>
    <div class="out"><div class="on" id="oSub"></div><div class="ol">of them on a weekly plan</div></div>
    <div class="out"><div class="on" id="oRev"></div><div class="ol">monthly revenue by month 12</div></div>
    <div class="out"><div class="on" id="oLift"></div><div class="ol">vs where Pronto is today</div></div>
  </div>
 </div>
 <div><canvas id="growthChart" style="max-height:300px"></canvas></div>
</div>
<p class="cap" style="margin-top:14px">The first slider is the one that matters. A bigger acquisition campaign adds to the top. Making sure the pro shows up multiplies everything below it.</p></div>

<div class="card full"><h3>How I would prioritise, and how I would know I was right</h3>
<p class="cap">I scored every move on three things: the prize, meaning the extra monthly revenue it unlocks by month 12, read straight off the model above; the effort to build and run it; and how strong the evidence behind it is. The numbers are directional, and I would recalibrate them against Pronto's own data in the first week.</p>
<div class="tree">
  <div class="troot">Goal: more first bookings that actually get completed, which then compounds through the flywheel</div>
  <div class="tcols">
    <div class="tcol"><div class="td">A · Don't promise what you cannot fulfil</div><div class="tm">Stop offering instant slots where no pro is genuinely free.</div></div>
    <div class="tcol"><div class="td">B · Have enough supply where demand is</div><div class="tm">Standing weekly bookings make demand plannable. Top pros recruit and coach new ones.</div></div>
    <div class="tcol"><div class="td">C · Recover gracefully when it still fails</div><div class="tm">Capture on arrival, a backup pro, and an honest arrival time with a human to call.</div></div>
  </div>
</div>
<div class="eval2col">
  <div><canvas id="prioChart" style="max-height:320px"></canvas><p class="cap" style="margin-top:8px;text-align:center">Bubble size shows how strong the evidence is. Top-left is do first. Top-right is a bigger bet.</p></div>
  <div id="scoreTable"></div>
</div></div>

<div class="card full"><h3>For each move: what I believe, how I would know, and what would tell me to stop</h3>
<p class="cap">Every move written as a test, with the number that would prove it worked and the guardrail that catches damage early.</p>
<div id="hmg"></div></div>

<div class="card full"><h3>The first ninety days</h3>
<p class="cap">How I would sequence this, and the one number I would own.</p>
<div class="plan">
<div class="phase"><div class="ph">Weeks 1 to 2 · Learn</div><div class="pt">Stop guessing from reviews. Build the booking-to-arrival funnel by area and hour, find where supply runs thin, and see how many people never book a second time.</div></div>
<div class="phase"><div class="ph">Weeks 3 to 6 · Steady the promise</div><div class="pt">In one or two thin areas, stop over-offering instant slots, give honest arrival windows, and hold a backup pro for first visits.</div></div>
<div class="phase"><div class="ph">Weeks 7 to 13 · Start the habit</div><div class="pt">Turn good first visits into weekly bookings in those areas, and watch whether steady demand lifts the share of bookings that get finished.</div></div>
</div>
<div class="metric"><span class="star">The one number I would own</span><br><b>First-booking completion rate</b>, the share of first bookings that end with a pro actually finishing the job, in the areas we focus on. Get that right and activation, repeat bookings, word of mouth, and the refund problem all move with it.</div></div>

<div class="grid">
<div class="card"><h3>When the money is gone and no one answers</h3><p class="cap">Payment comes first, so a broken booking reads as a scam. The fix is to hold the money and take it only on arrival.</p><div id="qSup"></div></div>
<div class="card"><h3>What happy customers say</h3><p class="cap">Five-star reviews. The work is loved when it actually happens.</p><div id="qPos"></div></div>
</div>

<div class="card full"><h3>What people are asking for</h3>
<p class="cap">Real requests, taken straight from the reviews. A ready-made backlog.</p>
<ul class="feat" id="feat"></ul></div>

<div class="method" id="method"></div>
<div class="foot"><img src="__LOGO__" alt="Pronto"/>Independent growth teardown. Not an official Pronto document.</div>
</div>

<script>
const D = __DATA__;
const C = {brand:'#18A860', uc:'#64748b', alert:'#E5484D', amb:'#C9A227'};
Chart.defaults.font.family = "'Inter',-apple-system,Segoe UI,Roboto,Arial,sans-serif";
Chart.defaults.font.size = 12;

document.getElementById('thesis').innerHTML =
 `<b>The short version.</b> When a professional shows up, people love Pronto. You can read it in the reviews. The trouble starts earlier, with a quieter question: is a pro actually free in this neighbourhood, at this hour? `+
 `<b>${D.reliability_share.pronto}%</b> of Pronto's unhappy reviews are about a no-show or cancellation, against <b>${D.reliability_share.uc}%</b> for Urban Company in the same cities. Because the customer has already paid, a broken booking does not feel like bad luck. It feels like being cheated, and the word "scam" follows. `+
 `The fix is not a campaign. It is a habit. Turn a good first visit into a standing weekly booking, and let that steady demand keep supply dense enough that a pro is simply there.`;

document.getElementById('honesty').innerHTML =
 `<img class="wm" src="__LOGOW__" alt=""/>`+
 `<h3>What the reviews can and cannot tell me, and where I would look next</h3>`+
 `<p class="cap">Reviews are written by the angriest and the happiest customers, never the quiet middle. There is no denominator here, and no way to see the person who simply never booked again. So I treat them as a place to find the right questions, not the answers. The chart on the right makes the point: ${D.liq.unclear_pct}% of the harshest reviews give no cause at all.</p>`+
 `<table>`+
 `<tr><td>Was the failure "no pro existed" or "a pro flaked"? (different fixes)</td><td>Event split: requested → assigned → checked-in → completed, per pincode/slot</td></tr>`+
 `<tr><td>How bad is the <i>silent</i> churn? (non-rebookers leave no review)</td><td>First→second-booking cohort retention, weekly</td></tr>`+
 `<tr><td>Where is liquidity actually thin?</td><td>Supply density: available pro-hours ÷ requested, by pincode × slot</td></tr>`+
 `<tr><td>Is "15-min" real or aspirational?</td><td>Promised ETA vs actual check-in delta</td></tr>`+
 `<tr><td>Does prepaid gate fraud/no-shows or just add friction?</td><td>No-show &amp; chargeback rate: prepaid vs authorize-only cells</td></tr>`+
 `</table>`;

const k = D.kpis;
const kpis = [
 ['Reviews read', k.total_scraped.toLocaleString(), ''],
 ['Pronto reviews', k.pronto_reviews.toLocaleString(), ''],
 ['Average rating', k.pronto_avg+'★', 'good'],
 ['One-star reviews', k.one_star.toLocaleString()+' ('+k.one_star_pct+'%)', 'alert'],
 ['Hand-read sample', k.sample, ''],
];
document.getElementById('kpis').innerHTML = kpis.map(x=>
 `<div class="kpi ${x[2]}"><div class="n">${x[1]}</div><div class="l">${x[0]}</div></div>`).join('');

new Chart(ratePr,{type:'bar',data:{labels:['1★','2★','3★','4★','5★'],
 datasets:[{data:D.rating_pr,backgroundColor:['#E5484D','#ef8a5f','#e3c14e','#9ec96b','#18A860'],borderRadius:6}]},
 options:{plugins:{legend:{display:false}},scales:{y:{beginAtZero:true}}}});

new Chart(liq,{type:'doughnut',data:{
 labels:['"No pro existed" (liquidity) '+D.liq.liquidity_pct+'%','"Pro flaked" (matching/ops) '+D.liq.matching_pct+'%','No attributable cause '+D.liq.unclear_pct+'%'],
 datasets:[{data:[D.liq.liquidity,D.liq.matching,D.liq.unclear],backgroundColor:[C.alert,C.amb,'#d3ddd7'],borderWidth:2,borderColor:'#fff'}]},
 options:{plugins:{legend:{position:'bottom',labels:{boxWidth:12,font:{size:11}}},
  tooltip:{callbacks:{label:c=>c.label+' ('+c.raw+' reviews)'}}},cutout:'58%'}});

const allThemes=[...new Set([...D.pr_theme.labels,...D.uc_theme.labels])];
const map=(lab,val,t)=>allThemes.map(x=>{const i=lab.indexOf(x);return i<0?0:Math.round(100*val[i]/t);});
new Chart(themeCmp,{type:'bar',data:{labels:allThemes,datasets:[
 {label:'Pronto',data:map(D.pr_theme.labels,D.pr_theme.values,D.n_pr_neg),backgroundColor:C.brand,borderRadius:5},
 {label:'Urban Company',data:map(D.uc_theme.labels,D.uc_theme.values,D.n_uc_neg),backgroundColor:C.uc,borderRadius:5}]},
 options:{plugins:{legend:{position:'top'},tooltip:{callbacks:{label:c=>c.dataset.label+': '+c.raw+'% of negatives'}}},
 scales:{y:{beginAtZero:true,ticks:{callback:v=>v+'%'}}}}});

document.getElementById('relPr').textContent=D.reliability_share.pronto+'%';
document.getElementById('relUc').textContent=D.reliability_share.uc+'%';

const q=(arr,cls)=>arr.map(t=>`<div class="quote ${cls}">"${t}…"</div>`).join('');
document.getElementById('qRel').innerHTML=q(D.quotes.reliability,'pr');
document.getElementById('qSup').innerHTML=q(D.quotes.support_refunds,'pr');
document.getElementById('qPos').innerHTML=q(D.quotes.pro_quality_pos,'good');
document.getElementById('feat').innerHTML=D.features.map(f=>`<li>${f}</li>`).join('');

document.getElementById('flow').innerHTML =
 `<img class="wm" src="__LOGOW__" alt=""/>`+
 `<h3>The fix is a habit, not a campaign</h3>`+
 `<div class="flowrow">`+
 `<span class="node">A great first visit</span><span class="arrow">→</span>`+
 `<span class="node hot">Same professional, every week</span><span class="arrow">→</span>`+
 `<span class="node">Demand you can predict</span><span class="arrow">→</span>`+
 `<span class="node">Supply you can pre-plan</span><span class="arrow">→</span>`+
 `<span class="node">A pro who shows up</span><span class="arrow">→</span>`+
 `<span class="node">Worth recommending</span>`+
 `</div>`+
 `<p class="cap" style="color:#9ab3a6;margin-top:14px">A standing weekly booking is not just a loyal customer. It is a forecast, and a forecast is the one thing that lets operations promise a pro will be there. It is also the only real moat. Anyone can hire the same professionals, Urban Company included. What is hard to copy is owning a household's weekly slot and the professional they have come to trust.</p>`;

// ---- Evaluation logic: prize sized off the growth model, plotted + scored ----
const DRV={A:"Don't over-promise", B:"Build supply", C:"Recover well"};
const EVAL=[
 {m:"Make the first visit a standing booking",driver:"B",rev:"₹60L",revn:6020000,impact:10,effort:5,conf:"Inferred",cnum:6,prio:"Big bet"},
 {m:"Stop promising what you cannot staff",driver:"A",rev:"₹34L",revn:3390000,impact:6,effort:6,conf:"Data-backed",cnum:8,prio:"Big bet"},
 {m:"Capture payment only on arrival",driver:"C",rev:"₹29L",revn:2940000,impact:5,effort:4,conf:"Data-backed",cnum:8,prio:"Quick win"},
 {m:"Let top pros recruit and coach",driver:"B",rev:"₹29L",revn:2940000,impact:5,effort:6,conf:"Hypothesis",cnum:4,prio:"Later"},
 {m:"Hold a backup pro for first visits",driver:"C",rev:"₹23L",revn:2260000,impact:4,effort:5,conf:"Data-backed",cnum:8,prio:"Later"},
 {m:"Honest arrival time and a human to call",driver:"C",rev:"₹11L",revn:1130000,impact:3,effort:3,conf:"Data-backed",cnum:8,prio:"Quick win"},
];
const HMG=[
 {m:"Make the first visit a standing booking",
  h:"Offering a one-tap 'same professional, every week' right after a great first visit will turn more first-timers into regulars and make their demand predictable enough to staff against.",
  s:"First-to-second booking rate, and the share of active customers on a weekly plan.",
  g:"Pro utilisation and how often standing bookings get cancelled. If pros get locked into routes they abandon, stop."},
 {m:"Stop promising what you cannot staff",
  h:"Only showing instant slots where a pro is genuinely free nearby will cut no-shows by more than it costs in lost instant bookings.",
  s:"First-booking completion rate in the test areas, and the no-show share of complaints.",
  g:"Instant-booking volume and conversion. If honest availability quietly kills demand, fix the messaging, not the honesty."},
 {m:"Capture payment only on arrival",
  h:"Holding the payment and charging only when the professional checks in will remove the 'they took my money' anger and lift willingness to try again.",
  s:"Rebooking rate after a wobble, and how often 'scam' or 'refund' shows up in new reviews.",
  g:"Fraud and chargeback rate, and pro no-shows. If removing upfront capture invites abuse, tighten it."},
 {m:"Let top pros recruit and coach",
  h:"The professionals who already do great work are the cheapest, most trusted source of new ones, so paying them to refer and mentor should grow supply where it is thin without dropping quality.",
  s:"New pros sourced and activated through referrals, their early ratings, and supply density in target areas.",
  g:"New-pro quality and complaint rate. If mentored pros underperform, fix the coaching before scaling it."},
 {m:"Hold a backup pro for first visits",
  h:"Pre-committing a second pro for first-ever bookings, with an instant refund and apology if it still fails, will protect the first impression that decides everything.",
  s:"Completion rate of first-ever bookings, and 30-day retention of customers whose first booking was recovered.",
  g:"The cost of over-provisioning per saved booking. If it costs more than a customer is worth, narrow it to the densest areas."},
 {m:"Honest arrival time and a human to call",
  h:"Replacing the fake 'two minutes away' with a real arrival window and a reachable person will cut rage-cancellations even when operations are slow.",
  s:"Cancellation rate during the wait, and support satisfaction.",
  g:"Average handle time and support cost. Keep a human reachable without drowning the team."},
];
const CCOL={Data:'#18A860', Inferred:'#C9A227', Hypothesis:'#94a3b8'};
const ccls = c => c.split('-')[0];
new Chart(document.getElementById('prioChart'),{type:'bubble',
 data:{datasets:EVAL.map((e,i)=>({label:(i+1)+'. '+e.m,data:[{x:e.effort,y:e.impact,r:6+e.cnum}],
   backgroundColor:CCOL[ccls(e.conf)]+'cc',borderColor:CCOL[ccls(e.conf)],borderWidth:1}))},
 options:{plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>{const e=EVAL[c.datasetIndex];return (c.datasetIndex+1)+'. '+e.m+'  ·  prize '+e.rev+'/mo';}}}},
  scales:{x:{min:0,max:10,title:{display:true,text:'Effort to build and run',color:'#7c8b82'},ticks:{stepSize:5,callback:v=>v===0?'low':v===10?'high':''},grid:{color:c=>c.tick.value===5?'#c2d3c9':'#eef2ef'}},
          y:{min:0,max:11,title:{display:true,text:'Prize: revenue at stake',color:'#7c8b82'},ticks:{stepSize:5,callback:v=>v===0?'low':v===10?'high':''},grid:{color:c=>c.tick.value===5?'#c2d3c9':'#eef2ef'}}}},
 plugins:[{afterDatasetsDraw(ch){const cx=ch.ctx;ch.data.datasets.forEach((ds,di)=>{const p=ch.getDatasetMeta(di).data[0];if(!p)return;cx.save();cx.fillStyle='#fff';cx.font='700 11px Inter';cx.textAlign='center';cx.textBaseline='middle';cx.fillText(String(di+1),p.x,p.y);cx.restore();});}}]});

let sk='impact', sd=-1;
const cols=[['m','Move'],['driver','Driver'],['revn','Prize / mo'],['impact','Impact'],['effort','Effort'],['conf','Evidence'],['prio','Priority']];
function renderTable(){
 const rows=EVAL.map((e,i)=>({...e,n:i+1}));
 rows.sort((a,b)=>{const x=a[sk],y=b[sk];return (typeof x==='string'?x.localeCompare(y):x-y)*sd;});
 const head='<tr>'+cols.map(c=>`<th data-k="${c[0]}">${c[1]}</th>`).join('')+'</tr>';
 const body=rows.map(e=>`<tr>
  <td><span class="mname">${e.n}. ${e.m}</span></td>
  <td>${e.driver} · ${DRV[e.driver]}</td>
  <td class="pz">${e.rev}</td><td>${e.impact}</td><td>${e.effort}</td>
  <td><span class="cbadge cb-${ccls(e.conf)}">${e.conf}</span></td>
  <td><span class="pbadge p-${e.prio.replace(/ /g,'-')}">${e.prio}</span></td></tr>`).join('');
 document.getElementById('scoreTable').innerHTML=`<table class="stbl"><thead>${head}</thead><tbody>${body}</tbody></table>`;
 document.querySelectorAll('.stbl th').forEach(th=>th.onclick=()=>{const k=th.dataset.k;
   if(sk===k)sd*=-1; else {sk=k; sd=(k==='m'||k==='driver'||k==='conf'||k==='prio')?1:-1;} renderTable();});
}
renderTable();
document.getElementById('hmg').innerHTML=HMG.map((x,i)=>`<div class="hcard"><h4>${i+1}. ${x.m}</h4>
 <div class="hl"><span class="t">Believe</span><span class="x">${x.h}</span></div>
 <div class="hl s"><span class="t">Success</span><span class="x">${x.s}</span></div>
 <div class="hl g"><span class="t">Guardrail</span><span class="x">${x.g}</span></div></div>`).join('');

// ---- Growth-model calculator (tied to first-booking completion rate) ----
const FIX = {leads:10000, churnSub:0.04, churnCasual:0.12, price:400, bkSub:4, bkCasual:1.5};
function project(c1, r2, sub){
  let s=0, c=0; const act=[];
  for(let m=0;m<12;m++){
    const completed = FIX.leads*c1, repeat = completed*r2;
    s = s*(1-FIX.churnSub) + repeat*sub;
    c = c*(1-FIX.churnCasual) + repeat*(1-sub);
    act.push(Math.round(s+c));
  }
  const rev = s*FIX.bkSub*FIX.price + c*FIX.bkCasual*FIX.price;
  return {act, sub:Math.round(s), active:Math.round(s+c), rev};
}
const PRESETS = {today:[65,40,15], fix:[90,40,15], flywheel:[90,55,45]};
const baseline = project(0.65, 0.40, 0.15);
function inr(v){ return v>=1e7 ? '₹'+(v/1e7).toFixed(1)+' Cr' : v>=1e5 ? '₹'+(v/1e5).toFixed(1)+' L' : '₹'+Math.round(v).toLocaleString('en-IN'); }
const $ = id => document.getElementById(id);
const c1El=$('c1'), r2El=$('r2'), subEl=$('sub');
let gChart;
function renderCalc(){
  const c1=+c1El.value, r2=+r2El.value, sub=+subEl.value;
  $('vC1').textContent=c1+'%'; $('vR2').textContent=r2+'%'; $('vSub').textContent=sub+'%';
  const r = project(c1/100, r2/100, sub/100);
  $('oActive').textContent = r.active.toLocaleString('en-IN');
  $('oSub').textContent = r.sub.toLocaleString('en-IN');
  $('oRev').textContent = inr(r.rev);
  $('oLift').textContent = (r.active/baseline.active).toFixed(1)+'× today';
  if(!gChart){
    gChart = new Chart($('growthChart'),{type:'line',
      data:{labels:[...Array(12)].map((_,i)=>'M'+(i+1)),datasets:[
        {label:'This plan',data:r.act,borderColor:'#18A860',backgroundColor:'rgba(24,168,96,.10)',fill:true,tension:.3,pointRadius:0,borderWidth:2.5},
        {label:'Where Pronto is today',data:baseline.act,borderColor:'#9aa7b3',borderDash:[5,4],fill:false,tension:.3,pointRadius:0,borderWidth:1.5}]},
      options:{plugins:{legend:{position:'top',labels:{boxWidth:12,font:{size:11}}}},
        scales:{y:{beginAtZero:true,ticks:{callback:v=>v>=1000?(v/1000)+'k':v}}}}});
  } else { gChart.data.datasets[0].data=r.act; gChart.update(); }
}
function setPreset(name){
  const [a,b,c]=PRESETS[name]; c1El.value=a; r2El.value=b; subEl.value=c;
  document.querySelectorAll('.preset').forEach(x=>x.classList.toggle('active', x.dataset.p===name));
  renderCalc();
}
[c1El,r2El,subEl].forEach(e=>e.addEventListener('input',()=>{
  document.querySelectorAll('.preset').forEach(x=>x.classList.remove('active')); renderCalc();
}));
document.querySelectorAll('.preset').forEach(p=>p.addEventListener('click',()=>setPreset(p.dataset.p)));
setPreset('today');

document.getElementById('method').innerHTML =
 `<b>How this was made.</b> ${k.total_scraped.toLocaleString()} public reviews were read across Pronto and Urban Company, from Google Play and the App Store in India. `+
 `The rating counts use every Pronto review with text (${k.pronto_reviews.toLocaleString()}). The theme and root-cause breakdowns use a hand-read sample of ${k.sample}, so every claim can be traced back to a real review. `+
 `Reviews come from the angriest and the happiest customers, never the quiet middle, so I treat all of this as a place to find questions worth testing against real product data, not as the final word. The Pronto name and logo are used only to say who this is about.`;
</script>
</body></html>"""

html = (HTML.replace("__DATA__", json.dumps(D)).replace("__GEN__", D["generated"])
        .replace("__PRN__", f"{D['kpis']['pronto_reviews']:,}")
        .replace("__LOGOW__", LOGO_WHITE).replace("__LOGO__", LOGO).replace("__ICON__", ICON))
(ROOT / "dashboard.html").write_text(html)
print("Wrote dashboard.html (Pronto-branded), size", len(html))
