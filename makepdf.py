#!/usr/bin/env python3
"""Render a markdown file to a publication-quality PDF via Chrome headless.

Usage: makepdf.py input.md [output.pdf]
"""
import base64
import subprocess
import sys
import tempfile
from pathlib import Path

import markdown

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
ROOT = Path(__file__).parent
LOGO = ROOT / "brand" / "pronto-logo.png"

# Pronto brand: green #18A860, near-black ink, soft green surfaces.
CSS = """
@page { size: A4; margin: 18mm 18mm 20mm; }
* { box-sizing: border-box; }
body { font-family: -apple-system, 'Helvetica Neue', Arial, sans-serif;
  color: #15201a; font-size: 10.6pt; line-height: 1.5; max-width: 100%; margin: 0; }
.brandbar { display: flex; align-items: center; gap: 10px; border-bottom: 2px solid #18A860;
  padding-bottom: 10px; margin-bottom: 18px; }
.brandbar img { height: 26px; }
.brandbar span { font-size: 10pt; color: #5d6f64; font-weight: 600; letter-spacing: .3px; }
h1 { font-size: 22pt; letter-spacing: -.5px; margin: 4px 0 2px; color: #0B1A12; }
h1 + p em, h1 ~ p:first-of-type em { color: #5d6f64; }
h2 { font-size: 11pt; color: #0F8A4E; text-transform: uppercase; letter-spacing: .6px;
  margin: 6px 0 14px; font-weight: 700; }
h3 { font-size: 14pt; color: #0B1A12; margin: 22px 0 6px; letter-spacing: -.2px;
  border-top: 1px solid #e3ece6; padding-top: 14px; }
h3:first-of-type { border-top: none; }
h4 { font-size: 11.5pt; color: #243a2f; margin: 14px 0 4px; }
p { margin: 8px 0; }
strong { color: #0B1A12; }
em { color: #3a4a42; }
a { color: #0F8A4E; text-decoration: none; }
blockquote { border-left: 4px solid #18A860; background: #E8F5EE; margin: 14px 0;
  padding: 10px 16px; border-radius: 0 8px 8px 0; color: #243a2f; }
blockquote p { margin: 4px 0; }
table { border-collapse: collapse; width: 100%; margin: 14px 0; font-size: 9.6pt; }
th { background: #0B1A12; color: #fff; text-align: left; padding: 7px 9px; font-weight: 600; }
td { border-bottom: 1px solid #e3ece6; padding: 6px 9px; vertical-align: top; }
tr:nth-child(even) td { background: #f4faf6; }
code { background: #eef5f0; padding: 1px 5px; border-radius: 4px; font-size: 9pt;
  font-family: 'SF Mono', Menlo, monospace; color: #0F8A4E; }
hr { border: none; border-top: 1px solid #e3ece6; margin: 22px 0; }
ul, ol { margin: 8px 0; padding-left: 22px; }
li { margin: 4px 0; }
h3, h4 { page-break-after: avoid; }
table, blockquote { page-break-inside: avoid; }
"""


def main():
    src = Path(sys.argv[1])
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_suffix(".pdf")
    body = markdown.markdown(
        src.read_text(),
        extensions=["tables", "fenced_code", "sane_lists", "attr_list"],
    )
    bar = ""
    if LOGO.exists():
        logo64 = base64.b64encode(LOGO.read_bytes()).decode()
        bar = (f"<div class='brandbar'><img src='data:image/png;base64,{logo64}'/>"
               f"<span>Growth Teardown</span></div>")
    html = f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{bar}{body}</body></html>"
    out = out.resolve()
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
        f.write(html)
        html_path = f.name
    profile = tempfile.mkdtemp(prefix="chrome-pdf-")
    subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu", "--no-first-run",
         f"--user-data-dir={profile}", "--no-pdf-header-footer",
         f"--print-to-pdf={out}", f"file://{html_path}"],
        check=True, capture_output=True,
    )
    if not out.exists():
        raise SystemExit(f"PDF was not written to {out}")
    print(out)


if __name__ == "__main__":
    main()
