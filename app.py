import os
import hashlib
import subprocess
from flask import Flask, render_template, request, redirect, url_for, send_file, session
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__)

# Secret key for sessions (required!)
app.secret_key = "supersecretkey123"  

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def verify_certificate(file_path):
    """
    Verifies the digital signature of a Windows executable using signtool.
    """
    try:
        result = subprocess.run(
            ["signtool", "verify", "/pa", file_path],
            capture_output=True, text=True
        )

        cert_info = {
            "valid": False,
            "subject": None,
            "issuer": None,
            "valid_from": None,
            "valid_to": None,
            "fingerprint": None
        }

        if "Successfully verified" in result.stdout:
            cert_info["valid"] = True

            # Dummy certificate info (replace with real parsing if needed)
            cert_info["subject"] = "Demo Organization"
            cert_info["issuer"] = "Trusted CA"
            cert_info["valid_from"] = "2023-01-01"
            cert_info["valid_to"] = "2026-01-01"

            # Compute SHA256 fingerprint
            with open(file_path, "rb") as f:
                cert_info["fingerprint"] = hashlib.sha256(f.read()).hexdigest()

        return cert_info
    except Exception as e:
        print("Verification error:", e)
        return None


@app.route("/", methods=["GET", "POST"])
def index():
    cert_info = None

    if request.method == "POST":
        if "file" not in request.files:
            return redirect(request.url)

        file = request.files["file"]
        if file.filename == "":
            return redirect(request.url)

        if file:
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(filepath)

            cert_info = verify_certificate(filepath)

            if cert_info:
                # ✅ Store in session for download_report
                session["cert_info"] = cert_info

    return render_template("index.html", cert_info=cert_info)


@app.route("/download_report")
def download_report():
    cert_info = session.get("cert_info")
    if not cert_info:
        return redirect(url_for("index"))

    report_path = os.path.join(app.config["UPLOAD_FOLDER"], "verification_report.pdf")

    # Generate PDF
    c = canvas.Canvas(report_path, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, 750, "Certificate Verification Report")

    c.setFont("Helvetica", 12)
    y = 700
    for key, value in cert_info.items():
        c.drawString(100, y, f"{key.capitalize()}: {value if value else 'N/A'}")
        y -= 25

    c.drawString(100, y - 20, f"Generated On: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    c.save()

    return send_file(report_path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)

   


