import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import argon2

# Constants
SALT_LENGTH = 16  # 128 bits
NONCE_LENGTH = 12 # 96 bits (standard for GCM)
ITERATIONS = 100_000
KEY_LENGTH = 32   # 256 bits for AES-256

class CryptoUtils:
    def __init__(self, master_password: str):
        self.master_password = master_password.encode('utf-8')
        self.argon2_hasher = argon2.PasswordHasher()

    def derive_key(self, salt: bytes) -> bytes:
        """Derives a 256-bit encryption key from the master password using PBKDF2."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=KEY_LENGTH,
            salt=salt,
            iterations=ITERATIONS,
            backend=default_backend()
        )
        return kdf.derive(self.master_password)

    def encrypt_data(self, plaintext: str) -> tuple:
        """
        Encrypts plaintext using AES-256-GCM.
        Returns (nonce, ciphertext_with_tag)
        """
        salt = os.urandom(SALT_LENGTH)
        nonce = os.urandom(NONCE_LENGTH)
        
        key = self.derive_key(salt)
        aesgcm = AESGCM(key)
        
        ciphertext = aesgcm.encrypt(nonce, plaintext.encode('utf-8'), None)
        
        # Return salt, nonce, and ciphertext (tag is included in ciphertext)
        return salt, nonce, ciphertext

    def decrypt_data(self, salt: bytes, nonce: bytes, ciphertext: bytes) -> str:
        """
        Decrypts ciphertext using the derived key.
        """
        key = self.derive_key(salt)
        aesgcm = AESGCM(key)
        
        try:
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)
            return plaintext.decode('utf-8')
        except Exception as e:
            raise ValueError("Decryption failed. Wrong password or corrupted data.") from e

    def hash_password_for_storage(self, password: str) -> str:
        """Hashes the master password for secure storage (using Argon2)."""
        return self.argon2_hasher.hash(password)

    def verify_password(self, stored_hash: str, password: str) -> bool:
        """Verifies a password against a stored Argon2 hash."""
        try:
            self.argon2_hasher.verify(stored_hash, password)
            return True
        except argon2.exceptions.VerifyMismatchError:
            return False