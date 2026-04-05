from flask import Flask, request, jsonify, session, render_template
from functools import wraps
import os
import json

from crypto_utils import CryptoUtils
from database import init_db, register_user, get_user, save_entry, get_entries, delete_entry

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secure random secret key for sessions

# Initialize DB
init_db()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "Authentication required. Please login."}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    # 1. Hash the master password for verification
    utils = CryptoUtils(password)
    password_hash = utils.hash_password_for_storage(password)
    
    # 2. Generate a unique salt for this user (used for key derivation)
    user_salt = os.urandom(16)
    
    if register_user(username, password_hash, user_salt):
        return jsonify({"message": "User registered successfully"}), 201
    else:
        return jsonify({"error": "Username already exists"}), 409

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = get_user(username)
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    # Verify password
    utils = CryptoUtils(password)
    if utils.verify_password(user['password_hash'], password):
        session['user_id'] = user['id']
        session['username'] = username
        # Store user_salt in session for convenience (though we could fetch it from DB)
        session['user_salt'] = user['user_salt'] 
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@app.route('/api/save', methods=['POST'])
@login_required
def save_password():
    data = request.json
    service = data.get('service')
    password_val = data.get('password')
    master_password = data.get('master_password') # Client sends master password

    if not service or not password_val or not master_password:
        return jsonify({"error": "Service, password, and master_password required"}), 400

    # Retrieve user salt from session (or DB)
    user_salt = session.get('user_salt')
    if not user_salt:
        return jsonify({"error": "Session expired or invalid"}), 401

    # Derive Key: Master Password + User Salt
    # We manually replicate the logic from crypto_utils to ensure consistency
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=user_salt,
        iterations=100_000,
        backend=default_backend()
    )
    key = kdf.derive(master_password.encode('utf-8'))

    # Encrypt Data: Key + Random Nonce
    nonce = os.urandom(12)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, password_val.encode('utf-8'), None)

    # Save to DB
    save_entry(session['user_id'], service, ciphertext, nonce)
    
    return jsonify({"message": "Password saved successfully"}), 200

@app.route('/api/get', methods=['GET'])
@login_required
def get_passwords():
    master_password = request.args.get('master_password')
    if not master_password:
        return jsonify({"error": "Master password required for decryption"}), 400

    user_salt = session.get('user_salt')
    if not user_salt:
        return jsonify({"error": "Session expired"}), 401

    # Derive Key
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=user_salt,
        iterations=100_000,
        backend=default_backend()
    )
    key = kdf.derive(master_password.encode('utf-8'))

    entries = get_entries(session['user_id'])
    decrypted_entries = []

    for entry in entries:
        try:
            aesgcm = AESGCM(key)
            plaintext = aesgcm.decrypt(entry['nonce'], entry['encrypted_data'], None)
            decrypted_entries.append({
                "id": entry['id'],
                "service": entry['service_name'],
                "password": plaintext.decode('utf-8')
            })
        except Exception:
            # If decryption fails, it means the master password is wrong
            return jsonify({"error": "Invalid master password"}), 403

    return jsonify({"entries": decrypted_entries}), 200

@app.route('/api/delete/<int:entry_id>', methods=['DELETE'])
@login_required
def delete_password(entry_id):
    delete_entry(entry_id)
    return jsonify({"message": "Entry deleted"}), 200

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    print("Starting server on http://127.0.0.1:5000")
    app.run(debug=True)