#!/usr/bin/env python3
"""Build the v2 single-file dashboard.html (Chart.js via CDN) from the raw +
classified review data. Data is embedded inline so the file is portable.

v2 changes: liquidity reframe, 3-way root-cause split, a "what this data can't
see" panel, a subscription-flywheel section, and reordered experiments.
"""
import json
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / "data"
raw = json.load(open(DATA / "reviews_raw.json"))
cls = json.load(open(DATA / "reviews_classified.json"))
liq = json.load(open(DATA / "liquidity_split.json"))

pr_raw = [r for r in raw if r["brand"] == "pronto"]
uc_raw = [r for r in raw if r["brand"] == "urban_company"]
pr = [r for r in cls if r["brand"] == "pronto"]
pr_neg = [r for r in pr if r["sentiment"] == "negative"]
uc_neg = [r for r in cls if r["brand"] == "urban_company" and r["sentiment"] == "negative"]

THEME_LABEL = {
    "reliability": "Reliability (no-show / cancel)",
    "support_refunds": "Support & refunds",
    "pro_quality": "Pro quality",
    "supply_availability": "No slots / not in area",
    "app_booking_ux": "App & booking UX",
    "pricing_value": "Pricing & value",
    "scheduling": "Scheduling",
    "other": "Other",
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
# share of attributable causes that are liquidity vs matching
attributable = liq["liquidity"] + liq["matching"]
liq_share_of_known = round(100 * liq["liquidity"] / attributable) if attributable else 0

D = {
    "generated": date.today().isoformat(),
    "kpis": {
        "total_scraped": len(raw), "pronto_reviews": len(pr_raw),
        "uc_reviews": len(uc_raw), "pronto_avg": avg,
        "one_star": one_star, "one_star_pct": round(100 * one_star / len(pr_raw)),
        "sample": len(cls),
    },
    "rating_pr": rating_dist(pr_raw),
    "pr_theme": {"labels": pr_theme_l, "values": pr_theme_v},
    "uc_theme": {"labels": uc_theme_l, "values": uc_theme_v},
    "reliability_share": {
        "pronto": round(100 * sum(1 for r in pr_neg if r["theme"] == "reliability") / len(pr_neg)),
        "uc": round(100 * sum(1 for r in uc_neg if r["theme"] == "reliability") / len(uc_neg)),
    },
    "liq": liq,
    "liq_share_of_known": liq_share_of_known,
    "quotes": {
        "reliability": quotes(pr_neg, "reliability", 3),
        "support_refunds": quotes(pr_neg, "support_refunds", 2),
        "pro_quality_pos": [" ".join(r["text"].split())[:200] for r in pr if r["sentiment"] == "positive" and r["theme"] == "pro_quality"][:3],
    },
    "features": features,
    "n_pr_neg": len(pr_neg), "n_uc_neg": len(uc_neg),
}

HTML = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Pronto Growth Teardown v2.0 — Review-Mining Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
:root{--ink:#0d1b2a;--mut:#5a6b7b;--line:#e6ebf0;--pr:#e8543f;--uc:#3a6ea5;--bg:#f6f8fa;--card:#fff;--good:#2a9d6a;--amb:#c9a227}
*{box-sizing:border-box}body{margin:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;color:var(--ink);background:var(--bg);line-height:1.5}
.wrap{max-width:1080px;margin:0 auto;padding:32px 24px 64px}
header h1{font-size:30px;margin:0 0 4px;letter-spacing:-.4px}
header .sub{color:var(--mut);font-size:15px}
.tag{display:inline-block;background:var(--pr);color:#fff;font-size:11px;font-weight:700;padding:3px 9px;border-radius:20px;letter-spacing:.5px;text-transform:uppercase;margin-bottom:14px}
.v2{background:#0d1b2a;margin-left:6px}
.kpis{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin:24px 0}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px}
.kpi .n{font-size:26px;font-weight:800;letter-spacing:-.5px}
.kpi .l{font-size:11px;color:var(--mut);text-transform:uppercase;letter-spacing:.4px;margin-top:2px}
.kpi.alert .n{color:var(--pr)}
.thesis{background:linear-gradient(135deg,#fff,#fff6f4);border:1px solid #f3d3cc;border-left:4px solid var(--pr);border-radius:12px;padding:20px 22px;margin:8px 0 20px}
.thesis b{color:var(--pr)}
.honesty{background:#0d1b2a;color:#dce4ec;border-radius:12px;padding:20px 22px;margin:0 0 28px}
.honesty h3{color:#fff;margin:0 0 6px;font-size:16px}
.honesty .cap{color:#9fb0c0;font-size:12.5px;margin:0 0 12px}
.honesty table{width:100%;border-collapse:collapse;font-size:12.5px}
.honesty td{border-bottom:1px solid #22344a;padding:7px 8px;vertical-align:top}
.honesty td:first-child{color:#cbd6e2}.honesty td:last-child{color:#8fd3b0}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px 20px;margin-bottom:18px}
.card h3{margin:0 0 2px;font-size:16px}
.card .cap{color:var(--mut);font-size:12.5px;margin:0 0 14px}
.full{grid-column:1/-1}
canvas{max-height:300px}
.quote{border-left:3px solid var(--line);padding:6px 0 6px 12px;margin:10px 0;color:#33424f;font-size:13.5px;font-style:italic}
.quote.pr{border-color:var(--pr)}.quote.good{border-color:var(--good)}
ul.feat{columns:2;gap:24px;font-size:13.5px;color:#33424f;margin:6px 0 0;padding-left:18px}
ul.feat li{margin:4px 0;break-inside:avoid}
.method{font-size:12px;color:var(--mut);background:#fff;border:1px dashed var(--line);border-radius:10px;padding:14px 16px;margin-top:24px}
.big{font-size:40px;font-weight:800;letter-spacing:-1px}
.cmp{display:flex;gap:24px;align-items:center;justify-content:center;text-align:center;padding:8px 0}
.cmp .v{font-size:13px;color:var(--mut)}.cmp .pr{color:var(--pr)}.cmp .uc{color:var(--uc)}
.flow{background:linear-gradient(135deg,#0d1b2a,#16314a);color:#eaf1f7;border-radius:12px;padding:22px;margin:0 0 18px}
.flow h3{color:#fff;margin:0 0 14px}
.flowrow{display:flex;flex-wrap:wrap;gap:8px;align-items:center;font-size:13px}
.node{background:#1d3a57;border:1px solid #2c4b6e;border-radius:8px;padding:8px 12px;color:#eaf1f7}
.node.hot{background:var(--pr);border-color:var(--pr);font-weight:700}
.arrow{color:#6f8aa6;font-size:18px}
.exp{display:flex;gap:12px;align-items:flex-start;padding:11px 0;border-bottom:1px solid var(--line)}
.exp:last-child{border-bottom:none}
.exp .badge{flex:0 0 auto;font-size:10.5px;font-weight:700;text-transform:uppercase;letter-spacing:.4px;padding:3px 8px;border-radius:20px;margin-top:2px}
.exp .badge.flag{background:var(--pr);color:#fff}.exp .badge.core{background:#0d1b2a;color:#fff}.exp .badge.enab{background:#eef1f4;color:#5a6b7b}
.exp .body{font-size:13.5px}.exp .body b{color:#0d1b2a}
@media(max-width:760px){.kpis{grid-template-columns:repeat(2,1fr)}.grid{grid-template-columns:1fr}}
</style></head>
<body><div class="wrap">
<header>
<div class="tag">Independent Growth Teardown · Built with Claude Code</div><div class="tag v2">v2.0</div>
<h1>Pronto — The Growth Ceiling Is Supply Liquidity</h1>
<div class="sub">4,464 public Google Play + App Store reviews (Pronto + Urban Company). No-shows are the symptom; liquidity is the disease. Generated __GEN__.</div>
</header>

<div class="thesis" id="thesis"></div>
<div class="honesty" id="honesty"></div>
<div class="kpis" id="kpis"></div>

<div class="grid">
<div class="card"><h3>Pronto rating distribution</h3><p class="cap">All __PRN__ Pronto reviews with text. Bimodal: love it, or rage-uninstall.</p><canvas id="ratePr"></canvas></div>
<div class="card"><h3>Root cause of the failures — what reviews can (and can't) tell you</h3><p class="cap">Pronto's harshest reviews (1-2★), attributed by language.</p><canvas id="liq"></canvas></div>
</div>

<div class="card full"><h3>Same market, opposite failure modes: Pronto's #1 problem is liquidity — Urban Company's isn't</h3>
<p class="cap">Negative-review themes, Pronto vs Urban Company. UC has crossed the liquidity threshold; Pronto hasn't yet.</p>
<canvas id="themeCmp" style="max-height:340px"></canvas></div>

<div class="grid">
<div class="card"><h3>Reliability share of complaints</h3><p class="cap">% of negative reviews about no-shows / cancellations.</p>
<div class="cmp"><div><div class="big pr" id="relPr"></div><div class="v pr">Pronto</div></div><div style="font-size:22px;color:#bbb">vs</div><div><div class="big uc" id="relUc"></div><div class="v uc">Urban Company</div></div></div>
<p class="cap" style="margin-top:8px">UC's detractors complain their pro <b>overcharged</b> — meaning a pro reliably showed up. Pronto's complain <b>nobody came.</b></p></div>
<div class="card"><h3>Voice of the detractor</h3><p class="cap">Representative Pronto 1★ reviews.</p><div id="qRel"></div></div>
</div>

<div class="flow" id="flow"></div>

<div class="card full"><h3>The experiments — one primary bet, sequenced</h3>
<p class="cap">Everything serves liquidity. The flywheel is the strategy; the rest are enablers.</p>
<div id="exps"></div></div>

<div class="grid">
<div class="card"><h3>Voice of the detractor — "no refund" / support</h3><p class="cap">Prepaid + no human recovery = "scam" perception. Fix: capture-on-arrival, not remove prepay.</p><div id="qSup"></div></div>
<div class="card"><h3>Voice of the promoter — what's working</h3><p class="cap">5★ reviews: the product IS loved when the pro shows up.</p><div id="qPos"></div></div>
</div>

<div class="card full"><h3>Feature requests &amp; concrete asks surfaced from reviews</h3>
<p class="cap">Verbatim asks extracted during classification — a free backlog.</p>
<ul class="feat" id="feat"></ul></div>

<div class="method" id="method"></div>
</div>

<script>
const D = __DATA__;
const C = {pr:'#e8543f', uc:'#3a6ea5', mut:'#9aa7b3', good:'#2a9d6a', amb:'#c9a227'};
Chart.defaults.font.family = "-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif";
Chart.defaults.font.size = 12;

document.getElementById('thesis').innerHTML =
 `<b>Thesis (v2):</b> Pronto's growth ceiling isn't acquisition — it's <b>supply liquidity</b> (a qualified pro actually available in your pincode & slot). No-shows are the symptom. `+
 `<b>${D.reliability_share.pronto}%</b> of Pronto's negative reviews are no-shows/cancellations vs <b>${D.reliability_share.uc}%</b> for Urban Company — same market, opposite failure mode. `+
 `Prepaid turns each failure into a "scam" review. The cure isn't a demand-side patch; it's a <b>subscription flywheel</b> that turns unpredictable demand into forecastable demand you can pre-staff — making reliability a consequence, not a hope.`;

document.getElementById('honesty').innerHTML =
 `<h3>What this data can NOT see — and what I'd pull on day one</h3>`+
 `<p class="cap">App-store reviews are the loudest 15%, with no denominator and no cohorts. I'd form hypotheses here, then validate against instrumentation. The chart on the right proves the point: ${D.liq.unclear_pct}% of the harshest reviews state no root cause at all.</p>`+
 `<table>`+
 `<tr><td>Was the failure "no pro existed" or "a pro flaked"? (different fixes)</td><td>Event split: requested → assigned → checked-in → completed, per pincode/slot</td></tr>`+
 `<tr><td>How bad is the <i>silent</i> churn? (non-rebookers leave no review)</td><td>First→second-booking cohort retention, weekly</td></tr>`+
 `<tr><td>Where is liquidity actually thin?</td><td>Supply density: available pro-hours ÷ requested, by pincode × slot</td></tr>`+
 `<tr><td>Is "15-min" real or aspirational?</td><td>Promised ETA vs actual check-in delta</td></tr>`+
 `<tr><td>Does prepaid gate fraud/no-shows or just add friction?</td><td>No-show & chargeback rate: prepaid vs authorize-only cells</td></tr>`+
 `</table>`;

const k = D.kpis;
const kpis = [
 ['Reviews mined', k.total_scraped.toLocaleString(), false],
 ['Pronto reviews', k.pronto_reviews.toLocaleString(), false],
 ['Pronto avg ★', k.pronto_avg, false],
 ['1★ reviews', k.one_star.toLocaleString()+' ('+k.one_star_pct+'%)', true],
 ['Classified sample', k.sample, false],
];
document.getElementById('kpis').innerHTML = kpis.map(x=>
 `<div class="kpi ${x[2]?'alert':''}"><div class="n">${x[1]}</div><div class="l">${x[0]}</div></div>`).join('');

new Chart(ratePr,{type:'bar',data:{labels:['1★','2★','3★','4★','5★'],
 datasets:[{data:D.rating_pr,backgroundColor:['#e8543f','#ef8a5f','#f0c05a','#9ec96b','#2a9d6a']}]},
 options:{plugins:{legend:{display:false}},scales:{y:{beginAtZero:true}}}});

// Root-cause 3-way split (doughnut) — liquidity vs matching vs unclear
new Chart(liq,{type:'doughnut',data:{
 labels:['"No pro existed" (liquidity) '+D.liq.liquidity_pct+'%','"Pro flaked" (matching/ops) '+D.liq.matching_pct+'%','No attributable cause '+D.liq.unclear_pct+'%'],
 datasets:[{data:[D.liq.liquidity,D.liq.matching,D.liq.unclear],backgroundColor:[C.pr,C.amb,'#cdd6df'],borderWidth:2,borderColor:'#fff'}]},
 options:{plugins:{legend:{position:'bottom',labels:{boxWidth:12,font:{size:11}}},
  tooltip:{callbacks:{label:c=>c.label+' ('+c.raw+' reviews)'}}},cutout:'58%'}});

const allThemes=[...new Set([...D.pr_theme.labels,...D.uc_theme.labels])];
const map=(lab,val,t)=>allThemes.map(x=>{const i=lab.indexOf(x);return i<0?0:Math.round(100*val[i]/t);});
new Chart(themeCmp,{type:'bar',data:{labels:allThemes,datasets:[
 {label:'Pronto',data:map(D.pr_theme.labels,D.pr_theme.values,D.n_pr_neg),backgroundColor:C.pr},
 {label:'Urban Company',data:map(D.uc_theme.labels,D.uc_theme.values,D.n_uc_neg),backgroundColor:C.uc}]},
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
 `<h3>The cure: a subscription flywheel that manufactures its own liquidity</h3>`+
 `<div class="flowrow">`+
 `<span class="node">Great first visit</span><span class="arrow">→</span>`+
 `<span class="node hot">Same-pro recurring subscription</span><span class="arrow">→</span>`+
 `<span class="node">Forecastable demand</span><span class="arrow">→</span>`+
 `<span class="node">Pre-positioned, fuller-utilized supply</span><span class="arrow">→</span>`+
 `<span class="node">Density you can plan</span><span class="arrow">→</span>`+
 `<span class="node">Reliability worth referring</span>`+
 `</div>`+
 `<p class="cap" style="color:#9fb0c0;margin-top:14px">Subscription isn't a retention afterthought — it's the engine input. A book of recurring cleans is a demand forecast, and a forecast is what lets ops guarantee a pro is there. It's also the moat: you can't moat on supply count (cleaners are interchangeable), so you moat by cornering the high-frequency buyer and owning "reliable" as a brand before UC's instant-help product does.</p>`;

const exps=[
 ['flag','Primary bet','E1 · Subscription flywheel — same-pro recurring after a great first visit','Turns unpredictable demand into a forecast ops can staff against, lifting density & reliability for everyone in that pincode. This is the loop; the rest are enablers.'],
 ['core','Liquidity','E2 · Supply-density-aware booking','Only surface instant slots where available pro-hours cover the pincode×slot; else an honest scheduled slot or waitlist. The cheapest reliability gain is refusing to promise liquidity you don\'t have.'],
 ['enab','Enabler','E3 · Guaranteed first visit via supply over-provisioning','Pre-commit a backup pro on first bookings; if it still fails, auto-refund + apology credit before the customer asks. A supply mechanism, not just a refund policy.'],
 ['enab','Enabler','E4 · Fix prepaid without killing it — authorize & capture on arrival','Don\'t remove prepay (it gates fraud, no-shows, working capital). Authorize at booking, capture when the pro checks in. Kills the "they took my money and ghosted" review without re-opening the fraud hole.'],
 ['enab','Hygiene','E5 · Honest ETA + one-tap human','Replace the fake "2 minutes away" loop and the self-closing AI chat. Lowest leverage, fastest to ship; honesty cuts rage-cancels even when ops are slow.'],
];
document.getElementById('exps').innerHTML = exps.map(e=>
 `<div class="exp"><span class="badge ${e[0]}">${e[1]}</span><div class="body"><b>${e[2]}</b><br>${e[3]}</div></div>`).join('');

document.getElementById('method').innerHTML =
 `<b>Method &amp; honesty note (v2).</b> ${k.total_scraped.toLocaleString()} public reviews scraped (Google Play + Apple RSS) for Pronto and Urban Company. `+
 `Rating distribution & volume use the full Pronto set (${k.pronto_reviews.toLocaleString()}). Theme/stage breakdowns use a stratified, hand-classified sample of ${k.sample}. `+
 `The root-cause split is a keyword attribution over ${D.liq.n_negative} of the harshest reviews — directional, and deliberately shows that ${D.liq.unclear_pct}% are unattributable from reviews alone (the case for event instrumentation). `+
 `Reviewers skew to extremes — treat all of this as signal to test, not population truth. Built independently with Claude Code; not affiliated with Pronto.`;
</script>
</body></html>"""

html = (HTML.replace("__DATA__", json.dumps(D)).replace("__GEN__", D["generated"])
        .replace("__PRN__", f"{D['kpis']['pronto_reviews']:,}"))
(ROOT / "dashboard.html").write_text(html)
print("Wrote dashboard.html (v2)")
