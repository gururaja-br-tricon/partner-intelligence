"""
Run once, locally, to generate the AUTH_SVC key pair. Does NOT require
the openssl CLI — uses the `cryptography` package directly.

Usage:
    python generate_auth_keys.py

Produces:
    auth_svc_private_key.pem  — keep this secret, .gitignore it, never commit
    auth_svc_public_key.pem   — paste the body (strip BEGIN/END lines) into
                                 ALTER USER AUTH_SVC SET RSA_PUBLIC_KEY = '...'
"""

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
)

public_pem = private_key.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
)

with open("auth_svc_private_key.pem", "wb") as f:
    f.write(private_pem)

with open("auth_svc_public_key.pem", "wb") as f:
    f.write(public_pem)

print("Generated auth_svc_private_key.pem and auth_svc_public_key.pem")
print()
print("Public key body for ALTER USER AUTH_SVC SET RSA_PUBLIC_KEY = '...':")
print()
body = "".join(public_pem.decode().splitlines()[1:-1])
print(body)