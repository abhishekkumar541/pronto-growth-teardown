#!/usr/bin/env python3
"""Build a single-file dashboard.html (Chart.js via CDN) from the raw +
classified review data. Data is embedded inline so the file is portable."""
import json
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / "data"
raw = json.load(open(DATA / "reviews_raw.json"))
cls = json.load(open(DATA / "reviews_classified.json"))

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
STAGE_LABEL = {
    "acquisition": "Acquisition",
    "activation": "Activation (1st booking)",
    "retention": "Retention (repeat/sub)",
    "referral": "Referral",
    "revenue": "Revenue",
    "none": "None",
}


def rating_dist(rows):
    c = Counter(r["rating"] for r in rows if r.get("rating"))
    return [c.get(i, 0) for i in range(1, 6)]


def theme_counts(rows):
    c = Counter(r["theme"] for r in rows)
    items = [(THEME_LABEL.get(k, k), v) for k, v in c.most_common()]
    return [i[0] for i in items], [i[1] for i in items]


def stage_counts(rows):
    c = Counter(r["funnel_stage"] for r in rows)
    order = ["acquisition", "activation", "retention", "revenue", "referral"]
    labels, vals = [], []
    for k in order:
        if c.get(k):
            labels.append(STAGE_LABEL[k])
            vals.append(c[k])
    return labels, vals


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
pr_stage_l, pr_stage_v = stage_counts(pr_neg)

avg = round(sum(r["rating"] for r in pr_raw) / len(pr_raw), 2)
one_star = sum(1 for r in pr_raw if r["rating"] == 1)

features = sorted({r["feature_request"] for r in cls if r["feature_request"]})

D = {
    "generated": date.today().isoformat(),
    "kpis": {
        "total_scraped": len(raw),
        "pronto_reviews": len(pr_raw),
        "uc_reviews": len(uc_raw),
        "pronto_avg": avg,
        "one_star": one_star,
        "one_star_pct": round(100 * one_star / len(pr_raw)),
        "sample": len(cls),
    },
    "rating_pr": rating_dist(pr_raw),
    "rating_uc": rating_dist(uc_raw),
    "pr_theme": {"labels": pr_theme_l, "values": pr_theme_v},
    "uc_theme": {"labels": uc_theme_l, "values": uc_theme_v},
    "pr_stage": {"labels": pr_stage_l, "values": pr_stage_v},
    "reliability_share": {
        "pronto": round(100 * sum(1 for r in pr_neg if r["theme"] == "reliability") / len(pr_neg)),
        "uc": round(100 * sum(1 for r in uc_neg if r["theme"] == "reliability") / len(uc_neg)),
    },
    "activation_share": round(100 * sum(1 for r in pr_neg if r["funnel_stage"] == "activation") / len(pr_neg)),
    "quotes": {
        "reliability": quotes(pr_neg, "reliability", 3),
        "support_refunds": quotes(pr_neg, "support_refunds", 2),
        "supply_availability": quotes(pr_neg, "supply_availability", 2),
        "pro_quality_pos": [" ".join(r["text"].split())[:200] for r in pr if r["sentiment"] == "positive" and r["theme"] == "pro_quality"][:3],
    },
    "features": features,
    "n_pr_neg": len(pr_neg),
    "n_uc_neg": len(uc_neg),
}

HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Pronto Growth Teardown — Review-Mining Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
:root{--ink:#0d1b2a;--mut:#5a6b7b;--line:#e6ebf0;--pr:#e8543f;--uc:#3a6ea5;--bg:#f6f8fa;--card:#fff;--good:#2a9d6a}
*{box-sizing:border-box}body{margin:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;color:var(--ink);background:var(--bg);line-height:1.5}
.wrap{max-width:1080px;margin:0 auto;padding:32px 24px 64px}
header h1{font-size:30px;margin:0 0 4px;letter-spacing:-.4px}
header .sub{color:var(--mut);font-size:15px}
.tag{display:inline-block;background:var(--pr);color:#fff;font-size:11px;font-weight:700;padding:3px 9px;border-radius:20px;letter-spacing:.5px;text-transform:uppercase;margin-bottom:14px}
.kpis{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin:24px 0}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px}
.kpi .n{font-size:26px;font-weight:800;letter-spacing:-.5px}
.kpi .l{font-size:11px;color:var(--mut);text-transform:uppercase;letter-spacing:.4px;margin-top:2px}
.kpi.alert .n{color:var(--pr)}
.thesis{background:linear-gradient(135deg,#fff,#fff6f4);border:1px solid #f3d3cc;border-left:4px solid var(--pr);border-radius:12px;padding:20px 22px;margin:8px 0 28px}
.thesis b{color:var(--pr)}
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
.cmp .v{font-size:13px;color:var(--mut)}
.cmp .pr{color:var(--pr)}.cmp .uc{color:var(--uc)}
@media(max-width:760px){.kpis{grid-template-columns:repeat(2,1fr)}.grid{grid-template-columns:1fr}}
</style></head>
<body><div class="wrap">
<header>
<div class="tag">Independent Growth Teardown · Built with Claude Code</div>
<h1>Pronto — What 4,464 Reviews Say About Growth</h1>
<div class="sub">Mined from public Google Play + App Store reviews for Pronto and Urban Company. Generated __GEN__.</div>
</header>

<div class="thesis" id="thesis"></div>

<div class="kpis" id="kpis"></div>

<div class="grid">
<div class="card"><h3>Pronto rating distribution</h3><p class="cap">All __PRN__ Pronto reviews with text. Bimodal: love it or rage-uninstall.</p><canvas id="ratePr"></canvas></div>
<div class="card"><h3>Where the pain hits in the funnel</h3><p class="cap">Pronto negative reviews by lifecycle stage (classified sample).</p><canvas id="stage"></canvas></div>
</div>

<div class="card full"><h3>The core finding: Pronto's #1 problem is reliability — Urban Company's isn't</h3>
<p class="cap">Negative-review themes, Pronto vs Urban Company. Same market, opposite failure modes.</p>
<canvas id="themeCmp" style="max-height:340px"></canvas></div>

<div class="grid">
<div class="card"><h3>Reliability share of complaints</h3><p class="cap">% of negative reviews about no-shows / cancellations.</p>
<div class="cmp"><div><div class="big pr" id="relPr"></div><div class="v pr">Pronto</div></div><div style="font-size:22px;color:#bbb">vs</div><div><div class="big uc" id="relUc"></div><div class="v uc">Urban Company</div></div></div>
<p class="cap" style="margin-top:8px">UC has solved liquidity; their complaints are about price &amp; pro skill. Pronto is still failing the basic promise: <b>someone shows up.</b></p></div>
<div class="card"><h3>Voice of the detractor — reliability</h3><p class="cap">Representative Pronto 1★ reviews.</p><div id="qRel"></div></div>
</div>

<div class="grid">
<div class="card"><h3>Voice of the detractor — support &amp; "no refund"</h3><p class="cap">The prepaid model + no human recovery = "scam" perception.</p><div id="qSup"></div></div>
<div class="card"><h3>Voice of the promoter — what's working</h3><p class="cap">5★ reviews: the product IS loved when the pro shows up.</p><div id="qPos"></div></div>
</div>

<div class="card full"><h3>Feature requests &amp; concrete asks surfaced from reviews</h3>
<p class="cap">Verbatim asks extracted during classification — a free backlog.</p>
<ul class="feat" id="feat"></ul></div>

<div class="method" id="method"></div>
</div>

<script>
const D = __DATA__;
const C = {pr:'#e8543f', uc:'#3a6ea5', mut:'#9aa7b3', good:'#2a9d6a'};
Chart.defaults.font.family = "-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif";
Chart.defaults.font.size = 12;

document.getElementById('thesis').innerHTML =
 `<b>Thesis:</b> Pronto's growth ceiling is not acquisition — it's that the core promise breaks at the <b>first booking</b>. `+
 `<b>${D.reliability_share.pronto}%</b> of Pronto's negative reviews are about no-shows &amp; cancellations (vs just ${D.reliability_share.uc}% for Urban Company), and <b>${D.activation_share}%</b> of them strike at activation — the customer's very first visit. `+
 `On a <b>prepaid</b> model with no human support to recover the moment, every failed first booking becomes a refund fight and a "scam" review. Fixing first-booking reliability is the highest-leverage growth lever Pronto has.`;

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

new Chart(stage,{type:'bar',data:{labels:D.pr_stage.labels,
 datasets:[{data:D.pr_stage.values,backgroundColor:C.pr}]},
 options:{indexAxis:'y',plugins:{legend:{display:false}},scales:{x:{beginAtZero:true}}}});

// Aligned theme comparison across union of labels
const allThemes=[...new Set([...D.pr_theme.labels,...D.uc_theme.labels])];
const map=(lab,val,t)=>allThemes.map(x=>{const i=lab.indexOf(x);return i<0?0:Math.round(100*val[i]/(t));});
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

document.getElementById('method').innerHTML =
 `<b>Method &amp; honesty note.</b> ${k.total_scraped.toLocaleString()} public reviews were scraped (Google Play + Apple RSS) for Pronto and Urban Company. `+
 `Rating distribution and volume use the full Pronto set (${k.pronto_reviews.toLocaleString()}). Theme/stage breakdowns use a stratified, hand-classified sample of ${k.sample} reviews `+
 `(${D.n_pr_neg} Pronto negatives + promoters + ${D.n_uc_neg} UC negatives) — the full pipeline (analyze.py) classifies all reviews via the Claude API when a key is supplied. `+
 `Reviewers skew to extremes, so treat these as directional signal to test, not population truth. Built independently with Claude Code; not affiliated with Pronto.`;
</script>
</body></html>"""

html = (
    HTML.replace("__DATA__", json.dumps(D))
    .replace("__GEN__", D["generated"])
    .replace("__PRN__", f"{D['kpis']['pronto_reviews']:,}")
)
(ROOT / "dashboard.html").write_text(html)
print("Wrote dashboard.html")
