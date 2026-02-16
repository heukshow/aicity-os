import os
import re
import json

# --- Configuration ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEGAL_DIR = os.path.join(PROJECT_ROOT, 'directives', 'legal')
FINANCIAL_DIR = os.path.join(PROJECT_ROOT, 'directives', 'financial') # Future proofing
OUTPUTS_DIR = os.path.join(PROJECT_ROOT, 'outputs')
BUSINESS_PROFILE = os.path.join(LEGAL_DIR, 'business_profile.json')

from security_vault import SovereignVault

class SecurityRedactor:
    """The PII Masking Engine (Ensures no real PII leaks to outputs)"""
    
    def __init__(self):
        self.pii_patterns = []
        self.vault = SovereignVault()
        self._load_pii_patterns()

    def _load_pii_patterns(self):
        """Loads real PII from the encrypted profile to create masking patterns."""
        profile_enc = BUSINESS_PROFILE + '.enc'
        if os.path.exists(profile_enc):
            try:
                profile_json = self.vault.decrypt_to_memory(profile_enc)
                profile = json.loads(profile_json)
                info = profile.get("company_info", {})
                
                # Extract sensitive strings to mask
                sensitive_data = [
                    info.get("registration_number"),
                    info.get("dob"),
                    info.get("address_kr"),
                    info.get("bank_account", {}).get("account_number")
                ]
                
                for data in sensitive_data:
                    if data:
                        # Escape special chars and add to patterns
                        self.pii_patterns.append(re.escape(data))
            except Exception as e:
                print(f"🛡️ [Redactor] Error decrypting/parsing profile: {e}")
        
        # Add generic patterns (Bank accounts, Reg numbers)
        self.pii_patterns.append(r'\d{3}-\d{2}-\d{5}') # Biz Reg
        self.pii_patterns.append(r'\d{4}-\d{3}-\d{6}') # Bank Account style

    def redact_file(self, filepath):
        """Scans and redacts PII from a specific file."""
        if not os.path.exists(filepath):
            return

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        for pattern in self.pii_patterns:
            content = re.sub(pattern, "[CONFIDENTIAL_PII_REDACTED]", content)

        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"🛡️ [Redactor] PII detected and masked in: {os.path.basename(filepath)}")
        else:
            print(f"✅ [Redactor] No PII detected in: {os.path.basename(filepath)}")

    def scan_outputs(self):
        """Scans the entire outputs/ directory for potential leaks."""
        print("🔍 [Redactor] Scanning all outputs for PII leaks...")
        for root, dirs, files in os.walk(OUTPUTS_DIR):
            for file in files:
                if file.endswith('.md') or file.endswith('.txt') or file.endswith('.json'):
                    self.redact_file(os.path.join(root, file))

if __name__ == "__main__":
    redactor = SecurityRedactor()
    redactor.scan_outputs()
