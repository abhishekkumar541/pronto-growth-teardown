#!/usr/bin/env python3
"""Build the v2 single-file dashboard.html, styled in Pronto's brand
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
@media(max-width:760px){.kpis{grid-template-columns:repeat(2,1fr)}.grid{grid-template-columns:1fr}.plan{grid-template-columns:1fr}header h1{font-size:26px}}
</style></head>
<body><div class="wrap">
<div class="topbar">
<div class="brandrow"><img src="__LOGO__" alt="Pronto"/><div class="div"></div><span class="lbl">Growth Teardown</span></div>
<span class="pill">v2.0 · Internal-style analysis</span>
</div>
<header>
<h1>The growth ceiling is <span class="g">supply liquidity</span>.</h1>
<div class="sub">What 4,464 public reviews (Pronto + Urban Company) say about where growth is gated. No-shows are the symptom; liquidity is the disease. Generated __GEN__.</div>
</header>

<div class="thesis" id="thesis"></div>
<div class="delta" id="delta"></div>
<div class="honesty" id="honesty"></div>
<div class="kpis" id="kpis"></div>

<div class="grid">
<div class="card"><h3>Pronto rating distribution</h3><p class="cap">All __PRN__ Pronto reviews with text. Bimodal: love it, or rage-uninstall.</p><canvas id="ratePr"></canvas></div>
<div class="card"><h3>Root cause — what reviews can (and can't) tell you</h3><p class="cap">Pronto's harshest reviews (1-2★), attributed by language.</p><canvas id="liq"></canvas></div>
</div>

<div class="card full"><h3>Same market, opposite failure modes</h3>
<p class="cap">Negative-review themes, Pronto vs Urban Company. UC has crossed the liquidity threshold; Pronto hasn't yet.</p>
<canvas id="themeCmp" style="max-height:340px"></canvas></div>

<div class="grid">
<div class="card"><h3>Reliability share of complaints</h3><p class="cap">% of negative reviews about no-shows / cancellations.</p>
<div class="cmp"><div><div class="big pr" id="relPr"></div><div class="v pr">Pronto</div></div><div style="font-size:22px;color:#cbd5cd">vs</div><div><div class="big uc" id="relUc"></div><div class="v uc">Urban Company</div></div></div>
<p class="cap" style="margin-top:8px">UC's detractors complain their pro <b>overcharged</b> — meaning a pro reliably showed up. Pronto's complain <b>nobody came.</b></p></div>
<div class="card"><h3>Voice of the detractor</h3><p class="cap">Representative Pronto 1★ reviews.</p><div id="qRel"></div></div>
</div>

<div class="flow" id="flow"></div>

<div class="card full"><h3>The experiments — one primary bet, sequenced</h3>
<p class="cap">Everything serves liquidity. The flywheel is the strategy; the rest are enablers.</p>
<div id="exps"></div></div>

<div class="card full"><h3>Day 1 → 90 operating plan</h3>
<p class="cap">How I'd sequence this in the role — and the one metric I'd stake it on.</p>
<div class="plan">
<div class="phase"><div class="ph">Day 1–14 · Instrument</div><div class="pt">Stop guessing from reviews. Build the <b>requested→assigned→checked-in→completed</b> funnel by pincode×slot, the supply-density heatmap, and first→second-booking cohort retention.</div></div>
<div class="phase"><div class="ph">Day 15–45 · De-risk the promise</div><div class="pt">Ship <b>E2</b> (density-aware booking) + <b>E5</b> (honest ETA/human) in 1–2 thin pincodes; stand up <b>E3</b> over-provisioning for first bookings there.</div></div>
<div class="phase"><div class="ph">Day 45–90 · Spin the flywheel</div><div class="pt">Launch <b>E1</b> (same-pro subscription) in the proven pincodes; A/B authorize-on-arrival (<b>E4</b>). Measure: does subscription density lift completion rate?</div></div>
</div>
<div class="metric"><span class="star">The one metric I'd stake the role on</span><br><b>First-booking completion rate</b> (booked → pro actually completed) in target pincodes — the single number that gates activation, retention, referral, and the "scam"-review problem at once. Secondary: first→second-booking cohort retention.</div></div>

<div class="grid">
<div class="card"><h3>Voice of the detractor — "no refund" / support</h3><p class="cap">Prepaid + no human recovery = "scam" perception. Fix: capture-on-arrival, not remove prepay.</p><div id="qSup"></div></div>
<div class="card"><h3>Voice of the promoter — what's working</h3><p class="cap">5★ reviews: the product IS loved when the pro shows up.</p><div id="qPos"></div></div>
</div>

<div class="card full"><h3>Feature requests &amp; concrete asks surfaced from reviews</h3>
<p class="cap">Verbatim asks extracted during classification — a free backlog.</p>
<ul class="feat" id="feat"></ul></div>

<div class="method" id="method"></div>
<div class="foot"><img src="__LOGO__" alt="Pronto"/>Independent growth teardown · built with Claude Code · not an official Pronto document.</div>
</div>

<script>
const D = __DATA__;
const C = {brand:'#18A860', uc:'#64748b', alert:'#E5484D', amb:'#C9A227'};
Chart.defaults.font.family = "'Inter',-apple-system,Segoe UI,Roboto,Arial,sans-serif";
Chart.defaults.font.size = 12;

document.getElementById('thesis').innerHTML =
 `<b>Thesis (v2):</b> Pronto's growth ceiling isn't acquisition — it's <b>supply liquidity</b> (a qualified pro actually available in your pincode &amp; slot). No-shows are the symptom. `+
 `<b>${D.reliability_share.pronto}%</b> of Pronto's negative reviews are no-shows/cancellations vs <b>${D.reliability_share.uc}%</b> for Urban Company — same market, opposite failure mode. `+
 `Prepaid turns each failure into a "scam" review. The cure isn't a demand-side patch; it's a <b>subscription flywheel</b> that turns unpredictable demand into forecastable demand you can pre-staff — making reliability a consequence, not a hope.`;

document.getElementById('delta').innerHTML =
 `<b>What changed v1 → v2.</b> v1 called the problem "first-booking reliability." After pressure-testing the thesis against five marketplace operators' frameworks, I rebuilt it: reliability is a <b>symptom</b>; the disease is <b>supply liquidity</b>. v2 also adds what this data can't see + what I'd instrument day one, a root-cause split, and promotes the subscription flywheel to the strategy. Showing the iteration is the point — that's how I'd work inside the team.`;

document.getElementById('honesty').innerHTML =
 `<img class="wm" src="__LOGOW__" alt=""/>`+
 `<h3>What this data can NOT see — and what I'd pull on day one</h3>`+
 `<p class="cap">App-store reviews are the loudest 15%, with no denominator and no cohorts. I'd form hypotheses here, then validate against instrumentation. The chart on the right proves the point: ${D.liq.unclear_pct}% of the harshest reviews state no root cause at all.</p>`+
 `<table>`+
 `<tr><td>Was the failure "no pro existed" or "a pro flaked"? (different fixes)</td><td>Event split: requested → assigned → checked-in → completed, per pincode/slot</td></tr>`+
 `<tr><td>How bad is the <i>silent</i> churn? (non-rebookers leave no review)</td><td>First→second-booking cohort retention, weekly</td></tr>`+
 `<tr><td>Where is liquidity actually thin?</td><td>Supply density: available pro-hours ÷ requested, by pincode × slot</td></tr>`+
 `<tr><td>Is "15-min" real or aspirational?</td><td>Promised ETA vs actual check-in delta</td></tr>`+
 `<tr><td>Does prepaid gate fraud/no-shows or just add friction?</td><td>No-show &amp; chargeback rate: prepaid vs authorize-only cells</td></tr>`+
 `</table>`;

const k = D.kpis;
const kpis = [
 ['Reviews mined', k.total_scraped.toLocaleString(), ''],
 ['Pronto reviews', k.pronto_reviews.toLocaleString(), ''],
 ['Avg rating', k.pronto_avg+'★', 'good'],
 ['1★ reviews', k.one_star.toLocaleString()+' ('+k.one_star_pct+'%)', 'alert'],
 ['Classified sample', k.sample, ''],
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
 `<h3>The cure: a subscription flywheel that manufactures its own liquidity</h3>`+
 `<div class="flowrow">`+
 `<span class="node">Great first visit</span><span class="arrow">→</span>`+
 `<span class="node hot">Same-pro recurring subscription</span><span class="arrow">→</span>`+
 `<span class="node">Forecastable demand</span><span class="arrow">→</span>`+
 `<span class="node">Pre-positioned supply</span><span class="arrow">→</span>`+
 `<span class="node">Density you can plan</span><span class="arrow">→</span>`+
 `<span class="node">Reliability worth referring</span>`+
 `</div>`+
 `<p class="cap" style="color:#9ab3a6;margin-top:14px">Subscription isn't a retention afterthought — it's the engine input. A book of recurring cleans is a demand forecast, and a forecast is what lets ops guarantee a pro is there. It's also the moat: you can't moat on supply count (cleaners are interchangeable), so you moat by cornering the high-frequency buyer and owning "reliable" as a brand before UC's instant-help product does.</p>`;

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
 `Rating distribution &amp; volume use the full Pronto set (${k.pronto_reviews.toLocaleString()}). Theme/stage breakdowns use a stratified, hand-classified sample of ${k.sample}. `+
 `The root-cause split is a keyword attribution over ${D.liq.n_negative} of the harshest reviews — directional, and deliberately shows that ${D.liq.unclear_pct}% are unattributable from reviews alone (the case for event instrumentation). `+
 `Reviewers skew to extremes — treat all of this as signal to test, not population truth. Built independently with Claude Code; the Pronto name and logo are used for identification only.`;
</script>
</body></html>"""

html = (HTML.replace("__DATA__", json.dumps(D)).replace("__GEN__", D["generated"])
        .replace("__PRN__", f"{D['kpis']['pronto_reviews']:,}")
        .replace("__LOGOW__", LOGO_WHITE).replace("__LOGO__", LOGO).replace("__ICON__", ICON))
(ROOT / "dashboard.html").write_text(html)
print("Wrote dashboard.html (Pronto-branded v2), size", len(html))
