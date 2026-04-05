# Stateless Password Manager

A secure, educational password manager built with Python and Flask. 
Unlike traditional managers, this application operates in a **stateless** manner regarding sensitive data storage: all credentials are encrypted client-side (or in-memory) using AES-256-GCM before being persisted to a local SQLite database.

> ⚠️ **Disclaimer:** This is an educational project designed to demonstrate cryptographic concepts (hashing, symmetric encryption, salting). It is **not** intended for production use without a professional security audit.

## 🛠 Tech Stack
- **Language:** Python 3.10+
- **Framework:** Flask (Lightweight web server)
- **Cryptography:** `cryptography` library (AES-256-GCM)
- **Password Hashing:** `argon2-cffi`
- **Database:** SQLite (Encrypted blob storage)
- **Frontend:** Vanilla HTML/CSS/JavaScript

## 🔐 Security Architecture
1. **Master Password:** Hashed using **Argon2** (memory-hard function) for storage.
2. **Key Derivation:** PBKDF2-HMAC-SHA256 derives the encryption key from the master password + user salt.
3. **Data Encryption:** AES-256-GCM (Authenticated Encryption) ensures data integrity and confidentiality.
4. **Stateless Design:** No plaintext passwords ever touch the disk or network. The server only stores encrypted blobs.

## 🚀 How to Run
1. Clone the repository:
   ```bash
   git clone https://github.com/mayankgusain20010113/stateless-password-manager.git
   cd stateless-password-manager

## 📸 Screenshots
![UI Screenshot](*.png)