#!/usr/bin/env python3
"""
Build the ready-to-sell digital fulfillment assets for Stripe & Gumroad:
1. dist/commercial/SES_COMMERCIAL_LICENSE.pdf
2. dist/commercial/ses-enterprise-boilerplate.zip
"""

from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT_DIR = ROOT / "dist" / "commercial"

EXCLUDED_DIRS = {
    ".git",
    ".github",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    ".next",
    "target",
    "dist",
    "data",
    ".tmp",
    "site",
}

EXCLUDED_FILES = {
    ".env",
    ".env.prod",
    ".env.compose",
    "gateway.db",
    "ESTADO_E_INVENTARIO_SES.md",
    "PLAN_PRODUCTIZACION.md",
    "PLAN_PRODUCTIZACION_TRAINING_TOOLKIT.md",
    "build_commercial_assets.py",
    "setup_stripe_links.py",
    "check_crate_publication.py",
    "validate_release.py",
    "verify_release_artifacts.py",
    "logo.png",
}


def build_license_pdf(output_path: Path) -> Path:
    """Generate the official Commercial License Certificate PDF."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    license_text = (ROOT / "COMMERCIAL_LICENSE.md").read_text(encoding="utf-8")

    try:
        from ses.core.reports import EnterpriseReportPDF

        pdf = EnterpriseReportPDF(
            title="Commercial License Certificate",
            subtitle="SES Core & Enterprise White-Label Suite",
            watermark="LICENSE CERTIFICATE",
            classification="COMMERCIAL LICENSE",
        )
        pdf.alias_nb_pages()
        pdf.add_page()

        pdf.draw_section_title("Official Dual-License & White-Label Grant")
        for block in license_text.replace("\r\n", "\n").split("\n\n"):
            cleaned = (
                block.replace("# ", "")
                .replace("## ", "")
                .replace("### ", "")
                .replace("**", "")
                .replace("`", "")
                .strip()
            )
            if not cleaned or cleaned == "---":
                continue
            pdf.draw_body_text(cleaned, size=9)
            pdf.ln(2)

        pdf.output(str(output_path))
        return output_path
    except Exception as exc:
        print(f"[WARN] PDF fallback triggered: {type(exc).__name__}: {exc}")
        # Minimal valid PDF 1.4 fallback if fpdf2 is not installed in the current interpreter
        minimal_pdf = (
            b"%PDF-1.4\n"
            b"1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj\n"
            b"2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1 >>endobj\n"
            b"3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>endobj\n"
            b"4 0 obj<< /Length 168 >>stream\n"
            b"BT /F1 14 Tf 50 720 Td (SES Core & Enterprise - Commercial License Certificate) Tj "
            b"/F1 10 Tf 0 -28 Td (Retain your Stripe or Gumroad receipt alongside COMMERCIAL_LICENSE.md.) Tj ET\n"
            b"endstream\nendobj\n"
            b"5 0 obj<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>endobj\n"
            b"xref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n"
            b"0000000115 00000 n \n0000000241 00000 n \n0000000460 00000 n \n"
            b"trailer<< /Size 6 /Root 1 0 R >>\nstartxref\n528\n%%EOF\n"
        )
        output_path.write_bytes(minimal_pdf)
        return output_path


def build_boilerplate_zip(output_path: Path, license_pdf_path: Path) -> Path:
    """Package the clean White-Label Enterprise Boilerplate zip archive."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        if license_pdf_path.is_file():
            zf.write(
                license_pdf_path,
                arcname="ses-enterprise-boilerplate/SES_COMMERCIAL_LICENSE.pdf",
            )
        for file_path in sorted(ROOT.rglob("*")):
            if not file_path.is_file():
                continue
            rel_parts = file_path.relative_to(ROOT).parts
            if any(part in EXCLUDED_DIRS for part in rel_parts):
                continue
            if file_path.name in EXCLUDED_FILES or file_path.suffix in {".pyc", ".whl", ".log"}:
                continue
            arcname = str(Path("ses-enterprise-boilerplate") / file_path.relative_to(ROOT))
            zf.write(file_path, arcname=arcname)
    return output_path


def main() -> int:
    pdf_path = build_license_pdf(OUT_DIR / "SES_COMMERCIAL_LICENSE.pdf")
    zip_path = build_boilerplate_zip(OUT_DIR / "ses-enterprise-boilerplate.zip", pdf_path)
    print(f"Built Commercial License PDF: {pdf_path} ({pdf_path.stat().st_size:,} bytes)")
    print(f"Built White-Label Boilerplate ZIP: {zip_path} ({zip_path.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
