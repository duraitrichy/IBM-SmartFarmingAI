"""
reports.py — Report generation (PDF, CSV, Excel).
"""

import io
import csv
from datetime import datetime
from pathlib import Path
from flask import Blueprint, render_template, Response, send_file, session
from sqlalchemy import select
from database import db, Recommendation, ChatHistory, WeatherRecord, Disease, MarketPrice
from config import ActiveConfig

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/")
def reports_page():
    farmer_id = session.get("farmer_id")
    recs = db.session.scalars(select(Recommendation).where(Recommendation.farmer_id == farmer_id).order_by(Recommendation.created_at.desc()).limit(20)).all()
    return render_template("reports.html", recommendations=recs)


@reports_bp.route("/csv/recommendations")
def download_csv():
    farmer_id = session.get("farmer_id")
    rows = db.session.scalars(select(Recommendation).where(Recommendation.farmer_id == farmer_id)).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Agent Type", "Query", "Risk Level", "Confidence", "Date"])
    for r in rows:
        writer.writerow([r.id, r.agent_type, r.query, r.risk_level,
                         r.confidence_score, r.created_at.strftime("%Y-%m-%d %H:%M")])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=recommendations.csv"},
    )


def _pdf_safe(text: str) -> str:
    """Normalize unicode to latin-1 safe ASCII for fpdf built-in fonts."""
    replacements = {
        "\u2014": "-", "\u2013": "-",       # em dash, en dash
        "\u2018": "'", "\u2019": "'",        # curly single quotes
        "\u201c": '"', "\u201d": '"',        # curly double quotes
        "\u2026": "...",                      # ellipsis
        "\u00b0": " degrees",                # degree sign
        "\u20b9": "Rs.",                     # Indian rupee symbol
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text.encode("latin-1", errors="ignore").decode("latin-1")


@reports_bp.route("/pdf/recommendations")
def download_pdf():
    try:
        from fpdf import FPDF
    except ImportError:
        return "PDF generation requires fpdf2. Install it with: pip install fpdf2", 500

    farmer_id = session.get("farmer_id")
    rows = db.session.scalars(select(Recommendation).where(Recommendation.farmer_id == farmer_id).limit(10)).all()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "SmartFarmingAI - Recommendations Report", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
    pdf.ln(5)

    for rec in rows:
        pdf.set_font("Helvetica", "B", 11)
        agent = _pdf_safe(rec.agent_type.upper() if rec.agent_type else "")
        date_str = rec.created_at.strftime("%Y-%m-%d") if rec.created_at else ""
        pdf.cell(0, 8, f"{agent} Advisory - {date_str}", ln=True)
        pdf.set_font("Helvetica", "", 9)
        if rec.problem_summary:
            pdf.multi_cell(0, 6, _pdf_safe(rec.problem_summary[:300]))
        if rec.recommended_action:
            pdf.set_font("Helvetica", "I", 9)
            pdf.multi_cell(0, 6, "Action: " + _pdf_safe(rec.recommended_action[:200]))
        risk = _pdf_safe(rec.risk_level or "Low")
        conf = int((rec.confidence_score or 0) * 100)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(0, 6, f"Risk: {risk}  |  Confidence: {conf}%", ln=True)
        pdf.ln(3)

    buf = io.BytesIO(pdf.output())
    buf.seek(0)
    return send_file(buf, mimetype="application/pdf",
                     as_attachment=True, download_name="recommendations.pdf")
