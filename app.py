import os
import subprocess
from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "supersecretkey"
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def run_signtool(file_path):
    try:
        result = subprocess.run(
            ["signtool", "verify", "/pa", "/all", "/v", file_path],
            capture_output=True,
            text=True,
            shell=True
        )
        output = result.stdout

        cert_info = {
            "valid": False,
            "subject": "N/A",
            "issuer": "N/A",
            "valid_from": "N/A",
            "valid_to": "N/A",
            "fingerprint": "N/A",
        }

        # Set validity
        if "Successfully verified" in output:
            cert_info["valid"] = True

        # Extract SHA256 file hash
        if "Hash of file (sha256):" in output:
            cert_info["fingerprint"] = output.split("Hash of file (sha256):")[1].split("\n")[0].strip()

        # Extract Issued to
        if "Issued to:" in output:
            cert_info["subject"] = output.split("Issued to:")[1].split("\n")[0].strip()

        # Extract Issued by
        if "Issued by:" in output:
            cert_info["issuer"] = output.split("Issued by:")[1].split("\n")[0].strip()

        # Extract Valid To
        if "Expires:" in output:
            cert_info["valid_to"] = output.split("Expires:")[1].split("\n")[0].strip()

        # Extract Timestamp (as Valid From)
        if "The signature is timestamped:" in output:
            cert_info["valid_from"] = output.split("The signature is timestamped:")[1].split("\n")[0].strip()

        return cert_info

    except Exception as e:
        return {"error": str(e)}


@app.route("/", methods=["GET", "POST"])
def index():
    cert_info = None
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file uploaded!")
            return redirect(request.url)

        file = request.files["file"]
        if file.filename == "":
            flash("No file selected!")
            return redirect(request.url)

        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)

            cert_info = run_signtool(file_path)
            session["cert_info"] = cert_info

    return render_template("index.html", cert_info=cert_info)


@app.route("/download_report")
def download_report():
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    cert_info = session.get("cert_info")
    if not cert_info:
        flash("No report to download. Please verify a file first.")
        return redirect(url_for("index"))

    report_path = os.path.join(UPLOAD_FOLDER, "certificate_report.pdf")
    c = canvas.Canvas(report_path, pagesize=letter)
    c.setFont("Helvetica", 12)
    c.drawString(100, 750, "Certificate Verification Report")
    y = 720
    for key, value in cert_info.items():
        c.drawString(100, y, f"{key}: {value}")
        y -= 20
    c.save()

    return send_file(report_path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)

   



