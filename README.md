CODE SIGNING WITH PRIVATE KEY 

This project demonstrates a secure software distribution pipeline using:
- Code signing with self-signed certificates
- Timestamped signatures
- Short-lived token-based downloads via HTTPS server


Features
- 'hello.exe' – Example signed executable with self-signed certificate.  
- Code signing done via 'signtool.exe' with timestamp integration.  
- HTTPS local server ('server.py') issues short-lived tokens for downloads.  
- `requirements.txt` ensures quick Python environment setup.  

---

Repository Contents
- `hello.exe` → Signed executable.  
- `MyApp.exe` → Unsigned dummy executable (shows “Untrusted publisher”).  
- `self-signed-cert-internal.crt` → Self-signed certificate used for signing.  
- `server.py` → Flask-based HTTPS server with short-lived download tokens.  
- `requirements.txt` → Python dependencies.  
- `.gitignore` → Ignore sensitive files (private keys).  
- `README.md` → This file.  

Not uploaded for security reasons:  
- Private keys (`.key`, `.pfx`)  
- Certificate Signing Request (`.csr`)  


 How It Works
1. Generate a key, CSR, and self-signed certificate using OpenSSL.  
2. Sign executables with `signtool.exe` + timestamp server.  
3. Host signed executables on HTTPS server (`server.py`).  
4. Issue short-lived tokens for download (5 minutes).  
5. Verify signatures via Windows Explorer → Properties → Digital Signatures.  

Setup Instructions
1. Install Dependencies
pip install -r requirements.txt
