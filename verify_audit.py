import os
import sys

# Paths to check
ROOT = r"c:\Users\vaibh\Documents\GitHub\Code-JAM"
SEARCH_STRINGS = ["SAI University", "saiuniversity.edu.in", "superadmin", "timetable_manager"]

def check_hardcoding():
    print("--- Hardcoding Audit ---")
    found = False
    for root, dirs, files in os.walk(ROOT):
        if ".git" in root or "__pycache__" in root or ".venv" in root:
            continue
        for file in files:
            if file.endswith((".py", ".html", ".js", ".md")):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        for s in SEARCH_STRINGS:
                            if s in content:
                                print(f"FOUND '{s}' in {path}")
                                found = True
                except Exception as e:
                    pass
    if not found:
        print("PASS: No blacklisted hardcoded strings found.")
    else:
        print("FAIL: Hardcoded strings still exist.")

def check_db_seeding():
    print("\n--- DB Seeding Audit ---")
    # This checks the content of init_db.py roughly
    path = os.path.join(ROOT, "init_db.py")
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
        checks = [
            ("Apex Institute of Technology" in content, "Fictional University 1"),
            ("Greenfield University" in content, "Fictional University 2"),
            ("school_id=None" in content and "role='admin'" in content, "Platform Owner has school_id=None"),
            ("must_change_password=True" in content, "must_change_password set to True"),
            ("'password123'" in content, "Default password is password123")
        ]
        for ok, desc in checks:
            status = "PASS" if ok else "FAIL"
            print(f"{status}: {desc}")

if __name__ == "__main__":
    check_hardcoding()
    check_db_seeding()
