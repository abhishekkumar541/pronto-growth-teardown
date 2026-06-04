#!/usr/bin/env python3
"""Build a designed, human-written PDF of the Pronto growth teardown.

Modern strategy-memo layout in Pronto's own brand (green #18A860, Poppins +
Inter, Pronto logo). Fixed A4 "sheets" so pagination, headers and page numbers
are fully under our control. Copy is hand-written: warm, user-first, no em
dashes, no AI tells.

Usage: build_teardown_pdf.py [output.pdf]
"""
import base64
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
BRAND = ROOT / "brand"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def b64(p):
    return "data:image/png;base64," + base64.b64encode(Path(p).read_bytes()).decode()


LOGO = b64(BRAND / "pronto-logo.png")
LOGOW = b64(BRAND / "pronto-logo-white.png")
FONTS = (BRAND / "fonts_embedded.css").read_text()  # self-contained Poppins + Inter
TODAY = date.today().strftime("%B %Y")

CSS = """
@page { size: A4; margin: 0; }
* { box-sizing: border-box; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
:root{
  --green:#18A860; --greenD:#0F7E47; --ink:#0E1A14; --body:#36443c; --mut:#7c8b82;
  --line:#e4ece7; --soft:#EAF6EF; --softL:#d3ead9; --alert:#E0533B; --slate:#6b7a86; --bg:#ffffff;
}
html,body{ margin:0; padding:0; background:#eef1ee; }
body{ font-family:'Inter',-apple-system,'Segoe UI',Arial,sans-serif; color:var(--body);
  font-size:11pt; line-height:1.58; -webkit-font-smoothing:antialiased; }
h1,h2,h3,.num,.stat .n,.eyebrow{ font-family:'Poppins','Inter',sans-serif; }
.sheet{ position:relative; width:210mm; height:297mm; padding:20mm 20mm 16mm;
  background:var(--bg); overflow:hidden; page-break-after:always; display:flex; flex-direction:column; }
.sheet:last-child{ page-break-after:auto; }

/* running header + footer */
.rh{ display:flex; align-items:center; justify-content:space-between;
  border-bottom:1px solid var(--line); padding-bottom:10px; margin-bottom:24px; }
.rh img{ height:20px; }
.rh .lbl{ font-size:8.5pt; letter-spacing:.14em; text-transform:uppercase; color:var(--mut); font-weight:600; }
.rf{ position:absolute; left:20mm; right:20mm; bottom:11mm; display:flex; align-items:center;
  justify-content:space-between; border-top:1px solid var(--line); padding-top:8px;
  font-size:8pt; color:var(--mut); letter-spacing:.04em; }
.rf .pg{ font-family:'Poppins'; font-weight:600; color:var(--ink); }

.eyebrow{ font-size:9pt; letter-spacing:.18em; text-transform:uppercase; color:var(--green); font-weight:700; }
.num{ color:var(--green); font-weight:700; }
.sec-h{ font-size:17pt; font-weight:700; color:var(--ink); letter-spacing:-.01em; margin:0 0 12px; line-height:1.15; }
.sec-h .num{ margin-right:10px; }
p{ margin:0 0 12px; }
.lead{ font-size:11.5pt; color:var(--body); }
strong{ color:var(--ink); font-weight:600; }

/* COVER */
.cover{ justify-content:flex-start; }
.cover .top{ display:flex; align-items:center; justify-content:space-between; }
.cover .top img{ height:30px; }
.cover .top .date{ font-size:9pt; letter-spacing:.16em; text-transform:uppercase; color:var(--mut); font-weight:600; }
.cover .mid{ margin-top:auto; margin-bottom:auto; }
.cover .eyebrow{ margin-bottom:18px; }
.cover h1{ font-size:42pt; line-height:1.06; letter-spacing:-.02em; color:var(--ink); font-weight:800; margin:0 0 22px; max-width:15em; }
.cover h1 .g{ color:var(--green); }
.cover .rule{ width:64px; height:5px; background:var(--green); border-radius:3px; margin:0 0 22px; }
.cover .sub{ font-size:13pt; line-height:1.5; color:var(--body); max-width:30em; }
.cover .foot{ font-size:8.5pt; color:var(--mut); border-top:1px solid var(--line); padding-top:12px; }

/* BENTO STATS */
.bento{ display:grid; grid-template-columns:repeat(4,1fr); gap:10px; margin:6px 0 20px; }
.stat{ border:1px solid var(--line); border-radius:14px; padding:14px 15px; background:#fff; }
.stat .n{ font-size:24pt; font-weight:800; letter-spacing:-.02em; color:var(--ink); line-height:1; }
.stat .n.alert{ color:var(--alert); } .stat .n.green{ color:var(--green); }
.stat .k{ font-size:8.2pt; color:var(--mut); margin-top:7px; line-height:1.35; }
.stat.fill{ background:var(--soft); border-color:var(--softL); }

/* CALLOUT */
.callout{ background:var(--soft); border-left:4px solid var(--green); border-radius:0 12px 12px 0;
  padding:14px 18px; margin:6px 0 18px; font-size:11.5pt; color:var(--ink); }
.callout b{ color:var(--greenD); }

/* clean key/val rows */
.rows{ margin:4px 0 8px; }
.row{ display:flex; gap:16px; padding:10px 0; border-bottom:1px solid var(--line); }
.row:last-child{ border-bottom:none; }
.row .q{ flex:1; color:var(--ink); font-weight:600; font-size:10.5pt; }
.row .a{ flex:1; color:var(--body); font-size:10pt; }

/* split stat trio */
.trio{ display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin:8px 0 6px; }
.tcard{ border:1px solid var(--line); border-radius:12px; padding:14px; }
.tcard .tn{ font-family:'Poppins'; font-weight:800; font-size:18pt; color:var(--ink); }
.tcard .tn.a{ color:var(--alert); } .tcard .tn.g{ color:var(--green); }
.tcard .tk{ font-size:9pt; color:var(--mut); margin-top:5px; }

/* FLYWHEEL */
.flow{ display:flex; flex-wrap:wrap; gap:7px; align-items:center; margin:10px 0 14px; }
.fnode{ background:#fff; border:1px solid var(--softL); border-radius:9px; padding:8px 11px;
  font-size:9.3pt; color:var(--ink); font-weight:500; }
.fnode.hot{ background:var(--green); border-color:var(--green); color:#fff; font-weight:700; }
.farr{ color:var(--green); font-weight:700; }

/* MOVES */
.move{ display:flex; gap:13px; padding:10px 0; border-bottom:1px solid var(--line); }
.move:last-child{ border-bottom:none; }
.move .mi{ flex:0 0 26px; height:26px; border-radius:8px; background:var(--soft); color:var(--greenD);
  font-family:'Poppins'; font-weight:700; font-size:11pt; display:flex; align-items:center; justify-content:center; }
.move .mb{ font-size:10.4pt; } .move .mb b{ color:var(--ink); }

/* TIMELINE */
.tl{ display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin:8px 0 14px; }
.tlc{ border:1px solid var(--line); border-radius:12px; padding:14px; background:#fff; }
.tlc .tlh{ font-family:'Poppins'; font-weight:700; font-size:10pt; color:var(--green); margin-bottom:6px; }
.tlc .tlb{ font-size:9.6pt; color:var(--body); }

.metric{ background:var(--ink); color:#eaf3ee; border-radius:14px; padding:18px 20px; margin:8px 0 16px; }
.metric .ml{ font-family:'Poppins'; font-size:8.5pt; letter-spacing:.14em; text-transform:uppercase; color:#7fe0ab; font-weight:700; }
.metric p{ margin:8px 0 0; color:#dbeae2; font-size:10.6pt; }
.metric b{ color:#fff; }

.close{ font-size:11pt; color:var(--body); }
.sign{ margin-top:14px; font-size:10pt; color:var(--mut); }

/* EVALUATION: issue tree, 2x2 matrix, scoring table, tests */
.ptree{ margin:4px 0 14px; }
.proot{ background:var(--ink); color:#fff; border-radius:8px; padding:8px 12px; font-size:9.2pt; font-weight:600; text-align:center; margin-bottom:8px; }
.pcols{ display:grid; grid-template-columns:repeat(3,1fr); gap:8px; }
.pcol{ border:1px solid var(--line); border-radius:8px; padding:9px; }
.pcol .pd{ font-size:8.6pt; font-weight:700; color:var(--greenD); margin-bottom:4px; }
.pcol .pm{ font-size:8.4pt; color:var(--body); }
.matrix{ position:relative; height:240px; border:1px solid var(--line); border-radius:10px; margin:6px 0 14px; background:#fbfdfc; }
.matrix .mqh{ position:absolute; left:0; right:0; top:50%; border-top:1px dashed #cdddd3; }
.matrix .mqv{ position:absolute; top:0; bottom:0; left:50%; border-left:1px dashed #cdddd3; }
.matrix .mdot{ position:absolute; width:24px; height:24px; margin:-12px 0 0 -12px; border-radius:50%; color:#fff; font-family:'Poppins'; font-weight:700; font-size:11px; display:flex; align-items:center; justify-content:center; }
.matrix .mlbl{ position:absolute; font-size:8pt; color:#aab6ae; font-weight:600; }
.matrix .tl{ left:12px; top:10px; } .matrix .tr{ right:12px; top:10px; } .matrix .bl{ left:12px; bottom:26px; } .matrix .br{ right:12px; bottom:26px; }
.matrix .myaxis{ position:absolute; left:8px; top:55%; transform:rotate(-90deg); transform-origin:left; font-size:8pt; color:var(--mut); white-space:nowrap; }
.matrix .mxaxis{ position:absolute; bottom:6px; left:50%; transform:translateX(-50%); font-size:8pt; color:var(--mut); }
.ptbl{ width:100%; border-collapse:collapse; font-size:8.8pt; }
.ptbl th{ text-align:left; color:var(--mut); font-size:7.4pt; text-transform:uppercase; letter-spacing:.03em; padding:5px 6px; border-bottom:1px solid var(--line); }
.ptbl td{ padding:6px; border-bottom:1px solid var(--line); vertical-align:middle; }
.ptbl tr:last-child td{ border-bottom:none; }
.pz{ font-family:'Poppins'; font-weight:700; color:var(--greenD); }
.cb,.pb{ font-size:7.4pt; font-weight:700; padding:2px 7px; border-radius:20px; white-space:nowrap; }
.cb-Data{ background:#E8F5EE; color:#0F7E47; } .cb-Inferred{ background:#fdf6e3; color:#9a7b1a; } .cb-Hypothesis{ background:#eef1f4; color:#647280; }
.pb-Big-bet{ background:var(--ink); color:#fff; } .pb-Quick-win{ background:#E8F5EE; color:#0F7E47; } .pb-Later{ background:#eef1f4; color:#647280; }
.tests{ display:grid; grid-template-columns:1fr 1fr; gap:10px; }
.tcard{ border:1px solid var(--line); border-radius:10px; padding:11px; }
.tcard h5{ margin:0 0 7px; font-size:9.3pt; font-family:'Poppins'; font-weight:700; color:var(--ink); }
.tcard .tr{ display:flex; gap:7px; font-size:8.3pt; margin:4px 0; line-height:1.4; }
.tcard .tr .k{ flex:0 0 48px; font-size:6.8pt; font-weight:700; text-transform:uppercase; letter-spacing:.03em; color:#9aa7a0; padding-top:2px; }
.tcard .tr.s .k{ color:var(--greenD); } .tcard .tr.g .k{ color:#c0392b; }
.tcard .tr .v{ flex:1; color:var(--body); }
"""

# ---------------------------------------------------------------- content ----
def rh(label="The growth teardown"):
    return (f'<div class="rh"><img src="{LOGO}"/>'
            f'<span class="lbl">{label}</span></div>')

def rf(page, total=7, note="Independent analysis"):
    return (f'<div class="rf"><span>{note}</span>'
            f'<span class="pg">{page:02d} / {total:02d}</span></div>')

COVER = f"""
<section class="sheet cover">
  <div class="top"><img src="{LOGO}"/><span class="date">Growth Teardown · {TODAY}</span></div>
  <div class="mid">
    <div class="eyebrow">A note on where growth is won or lost</div>
    <h1>The growth ceiling is <span class="g">supply liquidity</span>.</h1>
    <div class="rule"></div>
    <p class="sub">What 4,464 reviews reveal about the one moment that decides whether
      Pronto keeps a customer: whether a cleaner is actually at the door, on time.</p>
  </div>
  <div class="foot">Prepared independently from public app-store data. Not an official Pronto document.</div>
</section>
"""

P2 = f"""
<section class="sheet">
  {rh()}
  <div class="eyebrow">01 / The person behind the reviews</div>
  <h2 class="sec-h" style="margin-top:8px">When nobody shows up</h2>
  <p class="lead">Read enough of Pronto's reviews and a person starts to appear. She booked a
    cleaning before family arrived for the weekend. She took the morning off. She waited.
    Nobody came, and the app kept telling her a professional was on the way.</p>
  <p>When the work actually happens, people love it. The five-star reviews are full of relief.
    A home made ready before a puja. A flat sorted out after a move to a new city. Help that
    turned up in fifteen minutes on a morning the regular maid did not. That is most of the reviews,
    and it is the part most companies would kill for.</p>
  <p>So the question worth asking is not whether people want Pronto. They clearly do. The question
    is quieter. Is a cleaner free in her neighbourhood, at her hour, on the day she needs one?
    When the answer is no, the booking breaks. And because the customer has already paid, a broken
    booking does not feel like bad luck. It feels like being cheated. That is how a simple staffing
    gap becomes the word "scam" in a one-star review.</p>

  <div class="bento">
    <div class="stat"><div class="n">4,464</div><div class="k">public reviews read across Pronto and Urban Company</div></div>
    <div class="stat fill"><div class="n alert">66%</div><div class="k">of Pronto's unhappy reviews are about a no-show or cancellation</div></div>
    <div class="stat"><div class="n">11%</div><div class="k">the same figure for Urban Company, in the same cities</div></div>
    <div class="stat"><div class="n green">85%</div><div class="k">of all Pronto reviews are five star when the visit happens</div></div>
  </div>

  <div class="callout">Same city, same customers, opposite problem. Urban Company's unhappy
    customers complain that a pro <b>overcharged</b> them, which at least means a pro arrived.
    Pronto's complain that <b>nobody came</b>. One company is past the hard part. The other is
    still living it.</div>
  {rf(2)}
</section>
"""

P3 = f"""
<section class="sheet">
  {rh()}
  <div class="eyebrow">02 / What the reviews can and cannot tell me</div>
  <h2 class="sec-h" style="margin-top:8px">Honest about the data</h2>
  <p class="lead">Reviews are a good place to start and a dangerous place to stop. The people who
    write them are the angriest and the happiest, almost never the quiet middle. There is no
    denominator here, and no way to see the customer who simply never booked again. So I treat
    reviews as a way to find the right questions, not the answers.</p>
  <p>Here is the most useful thing they admit. Among the harshest reviews, about one in six clearly
    describe a pro who was never available. About one in eight describe a pro who was assigned and
    then failed to arrive. The rest, close to seven in ten, are too upset to say which. That last
    number is the real finding. You cannot run a growth plan on reviews. You instrument the product
    and let the data say which kind of failure you are looking at.</p>

  <div class="trio">
    <div class="tcard"><div class="tn a">~16%</div><div class="tk">name a pro who never existed (a supply gap)</div></div>
    <div class="tcard"><div class="tn">~12%</div><div class="tk">name a pro who was matched, then flaked</div></div>
    <div class="tcard"><div class="tn g">~72%</div><div class="tk">give no cause at all, which is the case for real data</div></div>
  </div>

  <p style="margin-top:14px"><strong>The four things I would pull in my first week:</strong></p>
  <div class="rows">
    <div class="row"><div class="q">Did a failed booking mean no pro existed, or a pro flaked?</div><div class="a">The booking-to-arrival funnel, broken down by area and time slot.</div></div>
    <div class="row"><div class="q">How many people quietly never come back?</div><div class="a">First-to-second booking retention, watched week by week.</div></div>
    <div class="row"><div class="q">Where is supply actually thin?</div><div class="a">Available pro-hours against requested hours, by pincode and hour.</div></div>
    <div class="row"><div class="q">Is the fifteen-minute promise real?</div><div class="a">Promised arrival time against the time a pro actually checks in.</div></div>
  </div>
  {rf(3)}
</section>
"""

P4 = f"""
<section class="sheet">
  {rh()}
  <div class="eyebrow">03 / The fix is a habit, not a campaign</div>
  <h2 class="sec-h" style="margin-top:8px">Make demand predictable</h2>
  <p class="lead">You do not fix thin supply by asking more cleaners to sit idle and wait. You fix it
    by making demand predictable. A customer who books the same cleaner every Tuesday is not only a
    loyal customer. She is a forecast. And a forecast is the one thing that lets operations promise a
    pro will be there.</p>
  <p>So the plan is quiet and a little boring, which is usually a good sign. Earn a great first visit.
    Turn it into a standing weekly booking with the same person. Use that steady demand to keep supply
    dense in the areas that matter. Reliability stops being a hope and becomes a result.</p>

  <div class="flow">
    <span class="fnode">A great first visit</span><span class="farr">&rarr;</span>
    <span class="fnode hot">Same cleaner, every week</span><span class="farr">&rarr;</span>
    <span class="fnode">Demand you can predict</span><span class="farr">&rarr;</span>
    <span class="fnode">Supply you can pre-plan</span><span class="farr">&rarr;</span>
    <span class="fnode">A pro who shows up</span><span class="farr">&rarr;</span>
    <span class="fnode">Worth recommending</span>
  </div>

  <div class="callout">This is also the only real moat. Anyone can hire the same cleaners, Urban
    Company included. What is hard to copy is owning a household's weekly slot and the cleaner they
    have come to trust.</div>

  <p>From here the work splits into a handful of concrete moves. Rather than rank them by gut, the
    next page sizes each one against the model, plots it by effort and reward, and writes it as a
    test with a clear way to tell whether it worked.</p>
  {rf(4)}
</section>
"""

# ---- Evaluation data (prize sized off the same model as the calculator) ----
DRV = {"A": "Don't over-promise", "B": "Build supply", "C": "Recover well"}
CCOL = {"Data-backed": "#18A860", "Inferred": "#C9A227", "Hypothesis": "#94a3b8"}
EVAL = [
    ("Make the first visit a standing booking", "B", "₹60L", 10, 5, "Inferred", "Big bet"),
    ("Stop promising what you cannot staff", "A", "₹34L", 6, 6, "Data-backed", "Big bet"),
    ("Capture payment only on arrival", "C", "₹29L", 5, 4, "Data-backed", "Quick win"),
    ("Let top pros recruit and coach", "B", "₹29L", 5, 6, "Hypothesis", "Later"),
    ("Hold a backup pro for first visits", "C", "₹23L", 4, 5, "Data-backed", "Later"),
    ("Honest arrival time and a human to call", "C", "₹11L", 3, 3, "Data-backed", "Quick win"),
]
_dots, _rows = "", ""
for _i, (_m, _d, _rev, _imp, _eff, _conf, _prio) in enumerate(EVAL, 1):
    _x, _y = _eff / 10 * 100, (1 - _imp / 11) * 100
    _dots += f'<div class="mdot" style="left:{_x:.0f}%;top:{_y:.0f}%;background:{CCOL[_conf]}">{_i}</div>'
    _cb = _conf.split("-")[0]
    _rows += (f'<tr><td><b>{_i}.</b> {_m}</td><td>{_d} · {DRV[_d]}</td><td class="pz">{_rev}</td>'
              f'<td>{_imp}</td><td>{_eff}</td><td><span class="cb cb-{_cb}">{_conf}</span></td>'
              f'<td><span class="pb pb-{_prio.replace(" ", "-")}">{_prio}</span></td></tr>')

HMG = [
    ("Make the first visit a standing booking",
     "Offering a one-tap 'same cleaner, every week' right after a great first visit will turn more first-timers into regulars and make their demand predictable enough to staff against.",
     "First-to-second booking rate, and the share of active customers on a weekly plan.",
     "Pro utilisation and how often standing bookings get cancelled. If pros get locked into routes they abandon, stop."),
    ("Stop promising what you cannot staff",
     "Only showing instant slots where a pro is genuinely free nearby will cut no-shows by more than it costs in lost instant bookings.",
     "First-booking completion rate in the test areas, and the no-show share of complaints.",
     "Instant-booking volume and conversion. If honest availability quietly kills demand, fix the messaging, not the honesty."),
    ("Capture payment only on arrival",
     "Holding the payment and charging only when the cleaner checks in will remove the 'they took my money' anger and lift willingness to try again.",
     "Rebooking rate after a wobble, and how often 'scam' or 'refund' shows up in new reviews.",
     "Fraud and chargeback rate, and pro no-shows. If removing upfront capture invites abuse, tighten it."),
    ("Let top pros recruit and coach",
     "The cleaners who already do great work are the cheapest, most trusted source of new ones, so paying them to refer and mentor should grow supply where it is thin without dropping quality.",
     "New pros sourced and activated through referrals, their early ratings, and supply density in target areas.",
     "New-pro quality and complaint rate. If mentored pros underperform, fix the coaching before scaling it."),
    ("Hold a backup pro for first visits",
     "Pre-committing a second pro for first-ever bookings, with an instant refund and apology if it still fails, will protect the first impression that decides everything.",
     "Completion rate of first-ever bookings, and 30-day retention of customers whose first booking was recovered.",
     "The cost of over-provisioning per saved booking. If it costs more than a customer is worth, narrow it to the densest areas."),
    ("Honest arrival time and a human to call",
     "Replacing the fake 'two minutes away' with a real arrival window and a reachable person will cut rage-cancellations even when operations are slow.",
     "Cancellation rate during the wait, and support satisfaction.",
     "Average handle time and support cost. Keep a human reachable without drowning the team."),
]
_tests = ""
for _i, (_m, _h, _s, _g) in enumerate(HMG, 1):
    _tests += (f'<div class="tcard"><h5>{_i}. {_m}</h5>'
               f'<div class="tr"><span class="k">Believe</span><span class="v">{_h}</span></div>'
               f'<div class="tr s"><span class="k">Success</span><span class="v">{_s}</span></div>'
               f'<div class="tr g"><span class="k">Guardrail</span><span class="v">{_g}</span></div></div>')

EVAL_A = f"""
<section class="sheet">
  {rh()}
  <div class="eyebrow">04 / How I would prioritise</div>
  <h2 class="sec-h" style="margin-top:8px">Sized, not guessed</h2>
  <p class="lead">I scored every move on three things: the prize, meaning the extra monthly revenue it
    unlocks by month 12 in the model; the effort to build and run it; and how strong the evidence
    behind it is. The numbers are directional, and I would recalibrate them against Pronto's own data
    in the first week.</p>
  <div class="ptree">
    <div class="proot">Goal: more first bookings that actually get completed, which then compounds through the flywheel</div>
    <div class="pcols">
      <div class="pcol"><div class="pd">A · Don't promise what you cannot fulfil</div><div class="pm">Stop offering instant slots where no pro is genuinely free.</div></div>
      <div class="pcol"><div class="pd">B · Have enough supply where demand is</div><div class="pm">Standing weekly bookings make demand plannable. Top pros recruit and coach.</div></div>
      <div class="pcol"><div class="pd">C · Recover gracefully when it fails</div><div class="pm">Capture on arrival, a backup pro, and an honest arrival time with a human to call.</div></div>
    </div>
  </div>
  <div class="matrix">
    <div class="myaxis">Prize: revenue at stake</div><div class="mxaxis">Effort to build and run</div>
    <div class="mqh"></div><div class="mqv"></div>
    <div class="mlbl tl">Do first</div><div class="mlbl tr">Bigger bets</div>
    <div class="mlbl bl">Quick wins</div><div class="mlbl br">Later</div>
    {_dots}
  </div>
  <table class="ptbl">
    <tr><th>Move</th><th>Driver</th><th>Prize / mo</th><th>Impact</th><th>Effort</th><th>Evidence</th><th>Priority</th></tr>
    {_rows}
  </table>
  {rf(5)}
</section>
"""

EVAL_B = f"""
<section class="sheet">
  {rh()}
  <div class="eyebrow">05 / Each move as a test</div>
  <h2 class="sec-h" style="margin-top:8px">What I believe, and how I would know</h2>
  <p class="lead">Every move written the way I would brief it: what I expect to happen, the number
    that would prove it worked, and the guardrail that would tell me to stop before it does damage.</p>
  <div class="tests">{_tests}</div>
  {rf(6)}
</section>
"""

P5 = f"""
<section class="sheet">
  {rh()}
  <div class="eyebrow">06 / The first ninety days</div>
  <h2 class="sec-h" style="margin-top:8px">Where I would start</h2>
  <div class="tl">
    <div class="tlc"><div class="tlh">Weeks 1 to 2 · Learn</div><div class="tlb">Build the booking-to-arrival funnel by area and hour. Find where supply runs thin. See how many people never come back after one try.</div></div>
    <div class="tlc"><div class="tlh">Weeks 3 to 6 · Steady the promise</div><div class="tlb">In one or two thin areas, stop over-offering instant slots, give honest arrival windows, and hold a backup pro for first visits.</div></div>
    <div class="tlc"><div class="tlh">Weeks 7 to 13 · Start the habit</div><div class="tlb">Turn good first visits into weekly bookings in those areas. Watch whether steady demand lifts the share of bookings that actually get finished.</div></div>
  </div>

  <div class="metric">
    <div class="ml">The one number I would own</div>
    <p>The share of first bookings that end with a pro actually finishing the job, in the areas we
      focus on. Get that right and activation, repeat bookings, word of mouth, and the refund problem
      all start to move with it. <b>Everything else is a means to that one end.</b></p>
  </div>

  <p class="close">I wrote this because I would rather show how I think than tell you about it.
    Some of it will be wrong in ways your own data would correct in a day, and I would genuinely like
    to know where. If any of it is useful, I would love to talk it through over a coffee or a call.</p>
  <p class="sign">Prepared from 4,464 public reviews of Pronto and Urban Company, {TODAY}.</p>
  {rf(7, note="Independent analysis · not an official Pronto document")}
</section>
"""

HTML = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"/>
<title>Pronto · Growth Teardown</title>
<style>{FONTS}
{CSS}</style></head><body>{COVER}{P2}{P3}{P4}{EVAL_A}{EVAL_B}{P5}</body></html>"""


def main():
    import shutil
    import time
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "Pronto-Growth-Teardown.pdf"
    out = out.resolve()
    # Chrome's --print-to-pdf and file:// choke on paths with spaces/apostrophes
    # (this project lives under "AI Learning/Lenny's/"), so render in /tmp and move.
    tmphtml = Path(tempfile.mkdtemp(prefix="td-")) / "render.html"
    tmphtml.write_text(HTML)
    tmppdf = Path(tempfile.gettempdir()) / "Pronto-Growth-Teardown.pdf"
    if tmppdf.exists():
        tmppdf.unlink()
    profile = tempfile.mkdtemp(prefix="chrome-pdf-")
    # Chrome 148 headless writes the PDF but then fails to exit, so we launch
    # non-blocking, poll until the file is written and stable, then terminate.
    proc = subprocess.Popen(
        [CHROME, "--headless=new", "--disable-gpu", "--no-first-run",
         f"--user-data-dir={profile}", "--no-pdf-header-footer",
         f"--print-to-pdf={tmppdf}", f"file://{tmphtml}"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    last, stable = -1, 0
    for _ in range(60):  # up to ~30s
        time.sleep(0.5)
        if tmppdf.exists():
            sz = tmppdf.stat().st_size
            stable = stable + 1 if sz == last and sz > 0 else 0
            last = sz
            if stable >= 3:  # size unchanged for ~1.5s
                break
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
    if not tmppdf.exists() or tmppdf.stat().st_size == 0:
        raise SystemExit(f"PDF not written to {tmppdf}")
    shutil.move(str(tmppdf), str(out))
    print(out)


if __name__ == "__main__":
    main()
