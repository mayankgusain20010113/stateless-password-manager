from crypto_utils import CryptoUtils

def test_encryption():
    master_pw = "MySecurePassword123!"
    utils = CryptoUtils(master_pw)
    
    # Test Encryption
    original_text = "Secret Password: supersecret123"
    salt, nonce, ciphertext = utils.encrypt_data(original_text)
    
    print(f"Original: {original_text}")
    print(f"Salt (hex): {salt.hex()}")
    print(f"Nonce (hex): {nonce.hex()}")
    print(f"Ciphertext (hex): {ciphertext.hex()}")
    
    # Test Decryption
    decrypted = utils.decrypt_data(salt, nonce, ciphertext)
    print(f"Decrypted: {decrypted}")
    
    assert original_text == decrypted, "Decryption failed!"
    
    # Test Wrong Password
    wrong_utils = CryptoUtils("WrongPassword")
    try:
        wrong_utils.decrypt_data(salt, nonce, ciphertext)
        print("ERROR: Should have failed with wrong password!")
    except ValueError:
        print("Correctly rejected wrong password.")

if __name__ == "__main__":
    test_encryption()