from __future__ import annotations

from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Preformatted, SimpleDocTemplate, Spacer


PROJECT_ROOT = Path(__file__).resolve().parent
SOURCE_MARKDOWN = PROJECT_ROOT / "FINAL_REPORT.md"
OUTPUT_PDF = PROJECT_ROOT / "FINAL_REPORT.pdf"


def main() -> None:
    text = SOURCE_MARKDOWN.read_text(encoding="utf-8")
    styles = getSampleStyleSheet()
    document = SimpleDocTemplate(str(OUTPUT_PDF), pagesize=A4)

    story = [Paragraph("File Guard Final Report", styles["Title"]), Spacer(1, 12)]
    for block in text.split("\n\n"):
        cleaned = block.strip()
        if not cleaned:
            continue
        if cleaned.startswith("#"):
            story.append(Paragraph(cleaned.lstrip("# ").strip(), styles["Heading2"]))
        elif cleaned.startswith("- "):
            story.append(Preformatted(cleaned, styles["Code"]))
        else:
            story.append(Paragraph(cleaned.replace("\n", "<br/>"), styles["BodyText"]))
        story.append(Spacer(1, 10))

    document.build(story)
    print(f"Generated {OUTPUT_PDF}")


if __name__ == "__main__":
    main()
