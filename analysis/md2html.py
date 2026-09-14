"""Convert FlipFocus Markdown to HTML with embedded figures."""
from pathlib import Path
import re

PAPER_DIR = Path(r"F:\Claude project\ubicomp_teenager\paper")
FIGS_REL  = "../results/figures"

# Figure mapping: (keyword_in_md, svg_filename, max_width_pct, alt_text)
FIGURES = [
    ("Figure 1:", "fig4_sensor_timeseries.svg", "100", "Figure 1: Sensor timeseries"),
    ("Figure 2:", "fig1_boxplot.svg", "85", "Figure 2: Focus score boxplot"),
    ("Figure 3:", "fig2_individual.svg", "100", "Figure 3: Individual trajectories"),
    ("Figure 4:", "fig3_validation.svg", "78", "Figure 4: Validation scatter"),
]

CSS = """<style>
  @media print { body { margin: 0; } @page { margin: 2.5cm; size: A4; } }
  body { font-family: "Times New Roman", serif; font-size: 12pt; line-height: 1.8; max-width: 800px; margin: 2.5cm auto; color: #111; }
  h1 { font-size: 16pt; text-align: center; font-weight: bold; margin: 0 0 4pt; }
  h2 { font-size: 13pt; margin: 18pt 0 8pt; border-bottom: 1px solid #999; padding-bottom: 3pt; }
  h3 { font-size: 11.5pt; margin: 14pt 0 6pt; }
  .authors { text-align: center; font-size: 11pt; margin: 6pt 0; }
  .affiliation { text-align: center; font-size: 9pt; color: #555; margin: 2pt 0 12pt; }
  p { margin: 4pt 0; text-indent: 2em; }
  p.no-indent { text-indent: 0; }
  table { border-collapse: collapse; margin: 10pt auto; font-size: 10pt; width: 95%; }
  th { background: #f0f0f0; font-weight: bold; padding: 4pt 8pt; border: 1px solid #999; }
  td { padding: 3pt 8pt; border: 1px solid #ccc; text-align: center; }
  .fig-wrap { text-align:center; margin: 8pt 0; }
  .fig-wrap img { height: auto; }
  .ref-list { font-size: 10pt; margin: 6pt 0; }
  .ref-list li { margin: 2pt 0; }
  .highlight { background: #fffde7; padding: 1pt 4pt; }
  ul, ol { margin: 4pt 0 4pt 2em; padding: 0; text-align: left; }
  li { margin: 2pt 0; }
  em { font-style: italic; }
  strong { font-weight: bold; }
  .venue { text-align:center; font-size:10pt; color:#888; margin:4pt 0 16pt; }
  blockquote { border-left: 3px solid #ccc; margin: 8pt 16pt; padding: 4pt 12pt; color: #444; font-style: italic; }
  hr { border: none; border-top: 1px solid #ccc; margin: 12pt 0; }
</style>"""

def md_to_html(md_path: Path, html_path: Path, lang: str):
    """Convert a Markdown file to HTML with embedded figures."""
    text = md_path.read_text(encoding="utf-8")

    # Split into lines
    lines = text.split("\n")
    html_lines = []
    in_code = False
    in_table = False
    in_list = False
    in_blockquote = False
    para_lines = []

    def flush_para():
        nonlocal para_lines
        if para_lines:
            content = " ".join(para_lines).strip()
            if content:
                # Inline formatting
                content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
                content = re.sub(r'\*(.+?)\*', r'<em>\1</em>', content)
                content = re.sub(r'`(.+?)`', r'<code>\1</code>', content)
                html_lines.append(f"<p>{content}</p>")
            para_lines = []

    in_ol = False
    in_ul = False

    for line in lines:
        # Figure placeholders
        stripped = line.strip().replace("**", "")
        for keyword, svg, w, alt in FIGURES:
            if stripped.startswith(f"> {keyword}"):
                html_lines.append(f'<div class="fig-wrap"><img src="{FIGS_REL}/{svg}" style="max-width:{w}%;" alt="{alt}"></div>')
                fig_text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line[2:].strip())
                html_lines.append(f"<p><em>{fig_text}</em></p>")
                line = "__CONSUMED__"
                break
        if line == "__CONSUMED__":
            continue

        # Headers
        if line.startswith("# ") and not line.startswith("## "):
            flush_para()
            html_lines.append(f"<h1>{line[2:]}</h1>")
            continue
        if line.startswith("## "):
            flush_para()
            html_lines.append(f"<h2>{line[3:]}</h2>")
            continue
        if line.startswith("### "):
            flush_para()
            html_lines.append(f"<h3>{line[4:]}</h3>")
            continue

        # Horizontal rule
        if line.strip() == "---":
            flush_para()
            html_lines.append("<hr>")
            continue

        # Blockquote
        if line.startswith("> ") and not any(line.strip().startswith(f"> {k}") for k,_,_,_ in FIGURES):
            flush_para()
            content = line[2:]
            content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
            content = re.sub(r'\*(.+?)\*', r'<em>\1</em>', content)
            html_lines.append(f"<blockquote>{content}</blockquote>")
            continue

        # Table rows
        if line.startswith("|"):
            flush_para()
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if all(c.startswith(":---") or c.startswith("---") for c in cells):
                continue  # skip separator row
            is_header = all(c.startswith(":---") or c.startswith("---") or c == "" for c in [""] + cells + [""]) == False
            tag = "th" if (html_lines and html_lines[-1].startswith("<table")) else "td"
            # Detect header row (first row after table tag)
            cell_html = "".join(f"<{tag}>{c}</{tag}>" for c in cells)
            if not html_lines or not html_lines[-1].startswith("<table"):
                html_lines.append("<table>")
            html_lines.append(f"<tr>{cell_html}</tr>")
            continue

        # Close table on non-table, non-empty line
        if html_lines and html_lines[-1].startswith("<tr>") and line.strip() and not line.startswith("|"):
            html_lines.append("</table>")
        if html_lines and html_lines[-1].startswith("<table>") and line.strip() and not line.startswith("|"):
            html_lines[-1] = html_lines[-1].replace("<table>", "")  # remove empty table

        # Ordered list
        if re.match(r'^\d+\.\s', line.strip()):
            flush_para()
            if not in_ol:
                if in_ul:
                    html_lines.append("</ul>")
                    in_ul = False
                html_lines.append("<ol>")
                in_ol = True
            content = re.sub(r'^\d+\.\s', '', line.strip())
            content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
            content = re.sub(r'\*(.+?)\*', r'<em>\1</em>', content)
            html_lines.append(f"<li>{content}</li>")
            continue

        # Unordered list
        if line.strip().startswith("- ") or line.strip().startswith("* "):
            flush_para()
            if not in_ul:
                if in_ol:
                    html_lines.append("</ol>")
                    in_ol = False
                html_lines.append("<ul>")
                in_ul = True
            content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line.strip()[2:])
            content = re.sub(r'\*(.+?)\*', r'<em>\1</em>', content)
            html_lines.append(f"<li>{content}</li>")
            continue

        # Close lists on non-list line
        if in_ol and not re.match(r'^\d+\.\s', line.strip()):
            html_lines.append("</ol>")
            in_ol = False
        if in_ul and not (line.strip().startswith("- ") or line.strip().startswith("* ")):
            html_lines.append("</ul>")
            in_ul = False

        # Authors / affiliation
        if line.startswith("**") and "¹" in line and not line.startswith("**关键词"):
            flush_para()
            content = line.replace("**", "")
            content = re.sub(r'\*(.+?)\*', r'<em>\1</em>', content)
            html_lines.append(f'<div class="authors">{content}</div>')
            continue
        if line.startswith("¹") and ("High School" in line or "Sanlin" in line or "学校" in line):
            flush_para()
            html_lines.append(f'<div class="affiliation">{line.strip()}</div>')
            continue
        if "CHCI" in line and "2026" in line and line.startswith("投稿") or line.startswith("Submitted"):
            flush_para()
            html_lines.append(f'<div class="venue">{line.strip()}</div>')
            continue

        # Empty line → flush paragraph
        if line.strip() == "":
            flush_para()
            continue

        # Regular text
        para_lines.append(line)

    flush_para()
    if in_ol:
        html_lines.append("</ol>")
    if in_ul:
        html_lines.append("</ul>")

    # Build HTML
    title = "FlipFocus: Phone Flip Detection Tool"
    if lang == "zh":
        title = "FlipFocus：基于浏览器多传感器融合的手机翻转行为检测与分析工具"

    body = "\n".join(html_lines)
    html = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<title>{title}</title>
{CSS}
</head>
<body>
{body}
</body>
</html>"""

    html_path.write_text(html, encoding="utf-8")
    kb = html_path.stat().st_size / 1024
    print(f"  {html_path.name}  ({kb:.0f} KB)")

# Generate both
md_to_html(PAPER_DIR / "FlipFocus_CHCI2026.md", PAPER_DIR / "FlipFocus_CHCI2026.html", "zh")
md_to_html(PAPER_DIR / "FlipFocus_CHCI2026_en.md", PAPER_DIR / "FlipFocus_CHCI2026_en.html", "en")
print("Done.")
