#!/usr/bin/env python3
"""Convert markdown to styled HTML then to PDF using macOS native tools."""
import subprocess
import markdown
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
MD_FILE = BASE / "output" / "Kshitij_Dashboard_API_Specification.md"
HTML_FILE = BASE / "output" / "Kshitij_Dashboard_API_Specification_print.html"
PDF_FILE = BASE / "output" / "Kshitij_Dashboard_API_Specification.pdf"

md_text = MD_FILE.read_text(encoding="utf-8")

html_body = markdown.markdown(
    md_text,
    extensions=["tables", "fenced_code", "toc", "sane_lists"],
)

full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Kshitij Dashboard API Specification</title>
<style>
  @page {{ size: A4; margin: 20mm 18mm 20mm 18mm; }}
  body {{
    font-family: -apple-system, 'Helvetica Neue', Arial, sans-serif;
    font-size: 11px; line-height: 1.55; color: #1e293b;
    max-width: 100%; padding: 0; margin: 0;
  }}
  h1 {{ font-size: 22px; color: #0f172a; border-bottom: 3px solid #3b82f6; padding-bottom: 8px; margin-top: 30px; page-break-after: avoid; }}
  h2 {{ font-size: 16px; color: #1e40af; border-bottom: 1px solid #cbd5e1; padding-bottom: 4px; margin-top: 24px; page-break-after: avoid; }}
  h3 {{ font-size: 13px; color: #334155; margin-top: 18px; page-break-after: avoid; }}
  h4 {{ font-size: 11px; color: #475569; }}
  table {{ border-collapse: collapse; width: 100%; margin: 10px 0 16px 0; font-size: 10px; page-break-inside: avoid; }}
  th {{ background: #f1f5f9; color: #334155; font-weight: 600; text-align: left; padding: 6px 8px; border: 1px solid #cbd5e1; }}
  td {{ padding: 5px 8px; border: 1px solid #e2e8f0; vertical-align: top; }}
  tr:nth-child(even) {{ background: #f8fafc; }}
  code {{ font-family: 'SF Mono', 'Menlo', monospace; font-size: 10px; background: #f1f5f9; padding: 1px 4px; border-radius: 3px; }}
  pre {{ background: #1e293b; color: #e2e8f0; padding: 12px 14px; border-radius: 6px; overflow-x: auto; font-size: 9.5px; line-height: 1.45; page-break-inside: avoid; }}
  pre code {{ background: none; padding: 0; color: #e2e8f0; }}
  blockquote {{ border-left: 3px solid #3b82f6; margin: 10px 0; padding: 6px 14px; color: #475569; background: #f8fafc; }}
  strong {{ color: #0f172a; }}
  hr {{ border: none; border-top: 1px solid #e2e8f0; margin: 20px 0; }}
  a {{ color: #2563eb; text-decoration: none; }}
  ul, ol {{ padding-left: 22px; }}
  li {{ margin-bottom: 3px; }}
  .toc {{ background: #f8fafc; border: 1px solid #e2e8f0; padding: 12px 18px; border-radius: 6px; margin-bottom: 20px; }}
  .toc a {{ color: #1e40af; }}
</style>
</head>
<body>
{html_body}
</body>
</html>"""

HTML_FILE.write_text(full_html, encoding="utf-8")
print(f"HTML written to {HTML_FILE}")

# Use macOS cupsfilter or /usr/sbin/cupsfilter for PDF conversion
# Alternatively use the Python webbrowser + osascript approach
# Best approach: use macOS's built-in textutil or a swift-based approach

# Try using the macOS built-in printing via command line
try:
    result = subprocess.run(
        ["/usr/sbin/cupsfilter", "-o", "media=A4", str(HTML_FILE)],
        capture_output=True, timeout=30
    )
    if result.returncode == 0:
        PDF_FILE.write_bytes(result.stdout)
        print(f"PDF written to {PDF_FILE}")
    else:
        raise RuntimeError("cupsfilter failed")
except Exception:
    # Fallback: use wkhtmltopdf if available, otherwise tell user
    try:
        subprocess.run(
            ["wkhtmltopdf", "--page-size", "A4",
             "--margin-top", "20mm", "--margin-bottom", "20mm",
             "--margin-left", "18mm", "--margin-right", "18mm",
             str(HTML_FILE), str(PDF_FILE)],
            check=True, capture_output=True, timeout=30
        )
        print(f"PDF written to {PDF_FILE}")
    except Exception:
        print(f"PDF generation requires manual step.")
        print(f"Open {HTML_FILE} in browser and Print → Save as PDF")
        print(f"Or install: brew install wkhtmltopdf")
