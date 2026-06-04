#!/usr/bin/env python3
"""Render a markdown file to a publication-quality PDF via Chrome headless.

Usage: makepdf.py input.md [output.pdf]
"""
import subprocess
import sys
import tempfile
from pathlib import Path

import markdown

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

CSS = """
@page { size: A4; margin: 20mm 18mm; }
* { box-sizing: border-box; }
body { font-family: -apple-system, 'Helvetica Neue', Arial, sans-serif;
  color: #16222e; font-size: 10.6pt; line-height: 1.5; max-width: 100%; margin: 0; }
h1 { font-size: 22pt; letter-spacing: -.5px; margin: 0 0 2px; color: #0d1b2a;
  border-bottom: 3px solid #e8543f; padding-bottom: 8px; }
h2 { font-size: 11pt; color: #e8543f; text-transform: uppercase; letter-spacing: .6px;
  margin: 6px 0 14px; font-weight: 700; }
h3 { font-size: 14pt; color: #0d1b2a; margin: 22px 0 6px; letter-spacing: -.2px;
  border-top: 1px solid #e6ebf0; padding-top: 14px; }
h3:first-of-type { border-top: none; }
h4 { font-size: 11.5pt; color: #2a3744; margin: 14px 0 4px; }
p { margin: 8px 0; }
strong { color: #0d1b2a; }
em { color: #3a4654; }
a { color: #e8543f; text-decoration: none; }
blockquote { border-left: 4px solid #e8543f; background: #fff6f4; margin: 14px 0;
  padding: 10px 16px; border-radius: 0 8px 8px 0; color: #2a3744; }
blockquote p { margin: 4px 0; }
table { border-collapse: collapse; width: 100%; margin: 14px 0; font-size: 9.6pt; }
th { background: #0d1b2a; color: #fff; text-align: left; padding: 7px 9px; font-weight: 600; }
td { border-bottom: 1px solid #e6ebf0; padding: 6px 9px; vertical-align: top; }
tr:nth-child(even) td { background: #f8fafb; }
code { background: #f0f3f6; padding: 1px 5px; border-radius: 4px; font-size: 9pt;
  font-family: 'SF Mono', Menlo, monospace; color: #c0392b; }
hr { border: none; border-top: 1px solid #e6ebf0; margin: 22px 0; }
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
    html = f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{body}</body></html>"
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
        f.write(html)
        html_path = f.name
    subprocess.run(
        [CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
         f"--print-to-pdf={out}", f"file://{html_path}"],
        check=True, capture_output=True,
    )
    print(out)


if __name__ == "__main__":
    main()
