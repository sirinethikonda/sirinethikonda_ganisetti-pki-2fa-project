# scripts/sign_and_encrypt_commit.py
import subprocess, base64, pathlib, sys
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import utils, rsa

ROOT = pathlib.Path(__file__).resolve().parents[1]
PRIV_PEM = ROOT / "student_private.pem"       # No longer looking in the 'keys' subfolder
INSTR_PUB_PEM = ROOT / "instructor_public.pem"

def get_latest_commit_hash():
    out = subprocess.check_output(["git", "log", "-1", "--format=%H"], cwd=ROOT)
    return out.decode().strip()

def load_private_key(path: pathlib.Path):
    pem = path.read_bytes()
    priv = serialization.load_pem_private_key(pem, password=None)
    return priv

def load_public_key(path: pathlib.Path):
    pem = path.read_bytes()
    pub = serialization.load_pem_public_key(pem)
    return pub

def sign_commit(commit_hash: str, priv_key):
    msg = commit_hash.encode("utf-8")  # ASCII/UTF-8 string per spec
    signature = priv_key.sign(
        msg,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature

def encrypt_signature(sig: bytes, instr_pub):
    ct = instr_pub.encrypt(
        sig,
        padding.OAEP(
            mgf=padding.MGF1(hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return ct

def main():
    if not PRIV_PEM.exists():
        print("student_private.pem not found at", PRIV_PEM); sys.exit(1)
    if not INSTR_PUB_PEM.exists():
        print("instructor_public.pem not found at", INSTR_PUB_PEM); sys.exit(1)

    commit_hash = get_latest_commit_hash()
    print("Commit hash:", commit_hash)

    priv = load_private_key(PRIV_PEM)
    instr_pub = load_public_key(INSTR_PUB_PEM)

    sig = sign_commit(commit_hash, priv)
    ct = encrypt_signature(sig, instr_pub)
    b64 = base64.b64encode(ct).decode("ascii")
    print("Encrypted signature (BASE64, single line):")
    print(b64)

if __name__ == "__main__":
    main()
