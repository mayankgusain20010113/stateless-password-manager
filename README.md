# Stateless Password Manager

A secure, educational password manager built with Python and Flask. 
Unlike traditional managers, this application operates in a **stateless** manner regarding sensitive data storage: all credentials are encrypted client-side (or in-memory) using AES-256-GCM before being persisted to a local SQLite database.

> ⚠️ **Disclaimer:** This is an educational project designed to demonstrate cryptographic concepts (hashing, symmetric encryption, salting). It is **not** intended for production use without a professional security audit.

## 🛠 Tech Stack
- **Language:** Python 3.10+
- **Framework:** Flask (Lightweight web server)
- **Cryptography:** `cryptography` library (Fernet/AES-GCM)
- **Database:** SQLite (Encrypted blob storage)
- **UI:** Jinja2 Templates (Simple HTML/CSS)

## 🔐 Security Architecture
1. **Master Password:** Hashed using **Argon2** (via `argon2-cffi`) with a random salt.
2. **Vault Encryption:** Data is encrypted using **AES-256-GCM** (Authenticated Encryption).
3. **Key Derivation:** PBKDF2 or Argon2 used to derive the encryption key from the master password.
4. **Stateless Design:** No plaintext passwords ever touch the disk or network.

## 🗺 Roadmap
- [x] **Step 1:** Project initialization, repo setup, and architecture documentation.
- [ ] **Step 2:** Implement core cryptography module (Key derivation, Encryption/Decryption).
- [ ] **Step 3:** Build the Flask backend API (Register, Login, CRUD operations).
- [ ] **Step 4:** Create the frontend UI (Login form, Dashboard).
- [ ] **Step 5:** Testing, error handling, and final polish.

## 📦 Installation
```bash
pip install flask cryptography argon2-cffi
python app.py
