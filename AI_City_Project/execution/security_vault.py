import os
import secrets
import base64

# --- Configuration ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECURE_DIR = os.path.join(PROJECT_ROOT, 'directives', 'legal')
KEY_FILE = os.path.join(PROJECT_ROOT, '.citadel_key') # Hidden key file

class SovereignVault:
    """Zero-Cost Local Encryption Engine (XOR Stream Cipher)"""
    
    def __init__(self):
        self.key = self._get_or_create_key()

    def _get_or_create_key(self):
        """Retrieves the master key or creates a high-entropy one if missing."""
        if os.path.exists(KEY_FILE):
            with open(KEY_FILE, 'rb') as f:
                return f.read()
        else:
            # Generate 256-bit random key
            new_key = secrets.token_bytes(32)
            with open(KEY_FILE, 'wb') as f:
                f.write(new_key)
            print("🛡️ [Vault] New Master Key generated and hidden.")
            return new_key

    def _xor_process(self, data, key):
        """Applies XOR stream cipher to data."""
        return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])

    def encrypt_file(self, filepath):
        """Encrypts a file locally."""
        if not os.path.exists(filepath) or filepath.endswith('.enc'):
            return

        with open(filepath, 'rb') as f:
            data = f.read()

        encrypted_data = self._xor_process(data, self.key)
        
        with open(filepath + '.enc', 'wb') as f:
            f.write(encrypted_data)
        
        # Original file is removed for security (In a real deploy, we'd wipe it)
        os.remove(filepath)
        print(f"🔒 [Vault] File locked and encrypted: {os.path.basename(filepath)}")

    def decrypt_to_memory(self, filepath_enc):
        """Decrypts an .enc file into memory (doesn't write back to disk)."""
        if not os.path.exists(filepath_enc):
            return None

        with open(filepath_enc, 'rb') as f:
            enc_data = f.read()

        return self._xor_process(enc_data, self.key).decode('utf-8')

    def lock_secure_zone(self):
        """Encrypts all sensitive files in the legal directory."""
        print("🏛️ [Vault] Initiating Sovereign Lockdown...")
        for root, dirs, files in os.walk(SECURE_DIR):
            for file in files:
                if not file.endswith('.enc'):
                    self.encrypt_file(os.path.join(root, file))
        print("✅ [Vault] All sensitive data is now encrypted.")

if __name__ == "__main__":
    vault = SovereignVault()
    vault.lock_secure_zone()
