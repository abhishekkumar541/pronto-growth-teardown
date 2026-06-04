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
@media(max-width:760px){.kpis{grid-template-columns:repeat(2,1fr)}.grid{grid-template-columns:1fr}.plan{grid-template-columns:1fr}header h1{font-size:26px}}
</style></head>
<body><div class="wrap">
<div class="topbar">
<div class="brandrow"><img src="__LOGO__" alt="Pronto"/><div class="div"></div><span class="lbl">Growth Teardown</span></div>
<span class="pill">Independent analysis</span>
</div>
<header>
<h1>The growth ceiling is <span class="g">supply liquidity</span>.</h1>
<div class="sub">What 4,464 public reviews say about the one moment that decides whether Pronto keeps a customer: whether a cleaner is actually at the door, on time.</div>
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

<div class="card full"><h3>Five moves, in order of leverage</h3>
<p class="cap">Everything here serves one thing: making sure a pro is actually there. The first move is the engine. The rest protect it.</p>
<div id="exps"></div></div>

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
 `<b>The short version.</b> When a cleaner shows up, people love Pronto. You can read it in the reviews. The trouble starts earlier, with a quieter question: is a pro actually free in this neighbourhood, at this hour? `+
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
 `<span class="node hot">Same cleaner, every week</span><span class="arrow">→</span>`+
 `<span class="node">Demand you can predict</span><span class="arrow">→</span>`+
 `<span class="node">Supply you can pre-plan</span><span class="arrow">→</span>`+
 `<span class="node">A pro who shows up</span><span class="arrow">→</span>`+
 `<span class="node">Worth recommending</span>`+
 `</div>`+
 `<p class="cap" style="color:#9ab3a6;margin-top:14px">A standing weekly booking is not just a loyal customer. It is a forecast, and a forecast is the one thing that lets operations promise a pro will be there. It is also the only real moat. Anyone can hire the same cleaners, Urban Company included. What is hard to copy is owning a household's weekly slot and the cleaner they have come to trust.</p>`;

const exps=[
 ['flag','The engine','Make the first visit a standing booking','After a good first clean, one tap keeps the same person every week. Recurring bookings turn unpredictable demand into a forecast operations can plan around, which lifts reliability for everyone nearby. Everything else just protects this.'],
 ['core','Liquidity','Stop promising what you cannot staff','Only offer an instant slot where pros are genuinely free nearby. Everywhere else, offer an honest later time. Refusing a promise you cannot keep is the cheapest reliability you can buy.'],
 ['enab','First impression','Protect the first booking','Hold a backup pro in reserve for first visits. If it still falls through, refund and apologise before the customer has to ask.'],
 ['enab','Payments','Fix the payment without removing it','Paying up front keeps fraud and no-shows down, so keep it. Just hold the money and take it only when the cleaner checks in. The "they took my money and vanished" review goes away.'],
 ['enab','Honesty','Be honest about timing','Replace the fake "two minutes away" with a real arrival window and a person to call. Honesty calms people even when the news is slow.'],
];
document.getElementById('exps').innerHTML = exps.map(e=>
 `<div class="exp"><span class="badge ${e[0]}">${e[1]}</span><div class="body"><b>${e[2]}</b><br>${e[3]}</div></div>`).join('');

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
