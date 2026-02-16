import os
import zipfile
import datetime

PROJECT_NAME = "AI_City_Project"
OUTPUT_BUNDLE = f"Sovereign_Migration_Package_{datetime.datetime.now().strftime('%Y%m%d')}.zip"

# Items to include
INCLUSIONS = [
    PROJECT_NAME,
    "Taskfile.yml",
    ".citadel_key"
]

# Items to exclude (patterns)
EXCLUSIONS = [
    ".venv",
    "__pycache__",
    ".git",
    ".vscode",
    ".idea",
    ".tmp",
    ".pytest_cache"
]

def create_migration_package():
    print(f"🏛️ Initiating Imperial Migration Packaging: {OUTPUT_BUNDLE}")
    
    with zipfile.ZipFile(OUTPUT_BUNDLE, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root_item in INCLUSIONS:
            if not os.path.exists(root_item):
                print(f"⚠️ Warning: {root_item} not found. Skipping.")
                continue
                
            if os.path.isfile(root_item):
                zipf.write(root_item)
                print(f"📄 Added file: {root_item}")
            else:
                for root, dirs, files in os.walk(root_item):
                    # Skip excluded directories
                    dirs[:] = [d for d in dirs if d not in EXCLUSIONS]
                    
                    for file in files:
                        if any(exc in file for exc in EXCLUSIONS):
                            continue
                        file_path = os.path.join(root, file)
                        zipf.write(file_path)
    
    print(f"✅ Imperial Migration Package ready: {os.path.abspath(OUTPUT_BUNDLE)}")
    print("\n--- Oracle Cloud Quick-Start ---")
    print("1. Upload this zip to your Oracle VM Standard.A1.Flex (ARM).")
    print("2. Run: unzip " + OUTPUT_BUNDLE)
    print("3. Run: cd " + PROJECT_NAME)
    print("4. Run: sudo docker build -t aicity-os .")
    print("5. Run: sudo docker run -d --name aicity-os --restart always aicity-os")

if __name__ == "__main__":
    create_migration_package()
