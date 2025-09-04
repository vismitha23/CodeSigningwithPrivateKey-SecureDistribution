from flask import Flask, request, send_file, jsonify
import jwt, datetime, hashlib

app = Flask(__name__)
SECRET_KEY = "super-secret-key"   # Change this for production

# --- Generate short-lived token (5 minutes) ---
@app.route("/get-token", methods=["GET"])
def get_token():
    expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
    token = jwt.encode({"exp": expiry}, SECRET_KEY, algorithm="HS256")
    return jsonify({"token": token})

# --- Secure download for SIGNED exe ---
@app.route("/download/signed", methods=["GET"])
def download_signed():
    token = request.args.get("token")
    if not token:
        return "Token required", 403
    try:
        jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return "Token expired", 403
    except jwt.InvalidTokenError:
        return "Invalid token", 403
    return send_file("hello.exe", as_attachment=True)

# --- Download UNSIGNED exe (to show “not trusted”) ---
@app.route("/download/unsigned", methods=["GET"])
def download_unsigned():
    return send_file("MyApp.exe", as_attachment=True)

# --- SHA-256 checksum for signed exe ---
@app.route("/checksum", methods=["GET"])
def checksum():
    sha256_hash = hashlib.sha256()
    with open("hello.exe", "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    return jsonify({"file": "hello.exe", "sha256": sha256_hash.hexdigest()})

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        ssl_context=("self-signed-cert-internal.crt", "internal-server.key")
    )
