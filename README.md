# Secure PKI-Based 2FA Microservice (Python/FastAPI)

## 🌟 Project Objective
This project implements a secure, containerized microservice that demonstrates enterprise-grade authentication practices using Public Key Infrastructure (PKI) and Time-based One-Time Password (TOTP) two-factor authentication (2FA).

The microservice handles sensitive key management, secure data persistence across container restarts, and provides three dedicated REST API endpoints for a complete authentication flow.

## ✨ Core Security & Technology Features

| Feature | Details |
| :--- | :--- |
| **Asymmetric Cryptography** | RSA 4096-bit key generation, RSA/OAEP decryption (SHA-256), RSA-PSS digital signing (SHA-256, max salt) for proof of work. |
| **Authentication Protocol** | TOTP 2FA (RFC 6238) using SHA-1, 30-second window, 6-digit codes, and a `±1` period tolerance for verification. |
| **Containerization** | Multi-stage Docker build for minimal image size (Python 3.11-slim), Cron Daemon installation, and UTC timezone enforcement. |
| **Persistence** | Secure volume mounting for persistent storage (`/data` and `/cron`), ensuring the decrypted seed survives container restarts. |
| **Automation** | A scheduled Cron job runs every minute to generate and log the current TOTP code, demonstrating continuous security operations. |
| **API Framework** | Built using Python 3 and **FastAPI** for high performance and modern API design. |

---

## 💻 API Endpoints

The service exposes the following endpoints on port **8080**:

| Method | Endpoint | Description | Status Codes |
| :--- | :--- | :--- | :--- |
| `POST` | `/decrypt-seed` | Accepts a Base64-encoded encrypted seed, decrypts it using the student's private key (RSA/OAEP), and stores the resulting hex seed at `/data/seed.txt`. | `200 OK`, `500 Internal Server Error` |
| `GET` | `/generate-2fa` | Reads the stored hex seed, generates the current 6-digit TOTP code, and reports the remaining validity seconds (`0-30`). | `200 OK`, `500 Internal Server Error` (if seed is missing) |
| `POST` | `/verify-2fa` | Accepts a code (`{"code": "123456"}`) and verifies it against the stored seed using a `±1` period (30-second) tolerance. | `200 OK` (`{"valid": true/false}`), `400 Bad Request` |

---

## 🛠️ Project Structure
.
├── app/
│   ├── main.py               # ➡️ FastAPI Application & API Endpoints
│   ├── crypto_utils.py       # ➡️ RSA Key Operations & Decryption/Signing
│   ├── totp_utils.py         # ➡️ TOTP Code Generation & Verification
│   ├── cron/
│   │   └── 2fa-cron          # ➡️ CRITICAL: Cron Schedule Config (Must use LF Endings)
│   └── scripts/
│       └── log_2fa_cron.py   # ➡️ Cron Job Script (Generates and logs 2FA code)
│
├── .gitattributes            # **CRITICAL:** Forces LF line endings on app/cron/2fa-cron
├── docker-compose.yml        # Orchestrates service, volumes, and port mapping
├── Dockerfile                # Multi-stage build instructions for image optimization
├── requirements.txt          # Python dependencies (fastapi, uvicorn, cryptography, pyotp)
│
├── student_private.pem       # Student RSA Private Key (Committed as required for decryption)
├── student_public.pem        # Student RSA Public Key (Required for submission)
├── instructor_public.pem     # Instructor's Public Key (For commit signature encryption)
├── encrypted_seed.txt        # Encrypted seed (NOT committed to Git)
└── scripts/
    └── sign_and_encrypt_commit.py # Local script to generate the final cryptographic proof:

## ⚙️ Setup and Deployment

### Prerequisites
1.  Docker and Docker Compose installed.
2.  Python 3.x (for running local scripts).

### 1. Build the Docker Image
The multi-stage Dockerfile is used to create a small, optimized runtime image.

```bash
docker-compose build

2. Run the Service
Start the container in detached mode. This launches the FastAPI server and the cron daemon.
docker-compose up -d

3.Decrypt the Seed (Initialization)
The first step is always to decrypt the seed using your private key and store it persistently.

(PowerShell Command)

$EncryptedSeed = (Get-Content -Raw encrypted_seed.txt).Trim()
$Body = @{ encrypted_seed = $EncryptedSeed } | ConvertTo-Json
$Headers = @{ "Content-Type" = "application/json" }
Invoke-RestMethod -Uri http://localhost:8080/decrypt-seed -Method POST -Headers $Headers -Body $Body
# Expected Output: status: ok

4. Verify Functionality and Persistence

Test,Command,Success Criteria
2FA Generation,Invoke-RestMethod -Uri http://localhost:8080/generate-2fa -Method GET,Returns a 6-digit code and valid_for time.
Seed Persistence,docker-compose restart then rerun 2FA Generation.,Must still return a code (not an error).
Cron Job Log,docker exec pki-2fa cat /cron/last_code.txt,"Shows recent, correctly formatted entries with UTC timestamps (e.g., YYYY-MM-DD HH:MM:SS - 2FA Code: XXXXXX)."

🔒 Commit Proof Generation
This proof verifies the authorship of the code at the submission commit hash.

1.Get Final Commit Hash:
git log -1 --format=%H
2.Generate Proof: Execute the local Python script which performs the required cryptographic operations:
Sign: Commit hash using RSA-PSS-SHA256.
Encrypt: The resulting signature using the Instructor's Public Key (RSA/OAEP-SHA256).
python scripts/sign_and_encrypt_commit.py 
# Output is the Base64-encoded Encrypted Signature (single line)

🛑 Security Notes
1.Key Exposure: student_private.pem is committed to this public repository solely for the purpose of the evaluation process (allowing the container to build and run correctly). These keys must never be reused in a production environment.

2.Timezone: The entire environment (API and Cron) operates strictly on UTC to ensure TOTP codes are generated and verified against the correct time epoch.