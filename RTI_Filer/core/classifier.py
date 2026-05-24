import json
import os
import re

def load_ministries_data():
    """Loads the Central Ministries database from data/ministries.json.
    
    The JSON schema uses 'mappings' as root key and 'ministry' as name field.
    Falls back to a hardcoded list if the file is missing or unreadable.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Search: core/../data/, core/data/, and cwd/data/
    path_options = [
        os.path.join(current_dir, "..", "data", "ministries.json"),  # RTI_Filer/data/
        os.path.join(current_dir, "data", "ministries.json"),
        os.path.join(os.getcwd(), "data", "ministries.json"),
    ]

    for path in path_options:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # ministries.json uses 'mappings' key — normalise it
                    if "mappings" in data and "ministries" not in data:
                        data["ministries"] = data["mappings"]
                    print(f"[OK] Loaded ministries from: {path}")
                    return data
            except Exception as e:
                print(f"[WARN] Failed to read JSON file ({str(e)}). Trying next path.")

    print("[WARN] Deploying fallback ministry keywords database.")
    return {
        "ministries": [
            {
                "ministry": "Ministry of Road Transport and Highways",
                "keywords": ["road", "highway", "sarak", "contractor", "pothole", "construction", "toll", "bypass"]
            },
            {
                "ministry": "Ministry of Consumer Affairs, Food and Public Distribution",
                "keywords": ["ration", "pds", "food grain", "consumer", "dealer", "chawal", "gehu"]
            },
            {
                "ministry": "Ministry of Railways",
                "keywords": ["railway", "station", "train", "platform", "irctc", "berth", "ticket"]
            }
        ]
    }

def classify_issue(problem_text: str) -> dict:
    """
    Scans the user problem against all ministries and keywords dynamically.
    Returns a dictionary with the key 'ministry' to match main.py expectations.
    """
    db = load_ministries_data()
    cleaned_input = problem_text.lower()
    
    best_match = None
    max_matches = 0
    
    # Dynamic keyword density and boundary matching loop
    for ministry in db.get("ministries", []):
        match_count = 0
        for keyword in ministry.get("keywords", []):
            # Regex boundary (\b) use kiya hai taaki partial match na ho
            if re.search(r'\b' + re.escape(keyword.lower()) + r'\b', cleaned_input):
                match_count += 1

        if match_count > max_matches:
            max_matches = match_count
            # ministries.json uses 'ministry' key; fallback uses same key now
            best_match = ministry.get("ministry") or ministry.get("name")
            
    # Agar koi bhi keyword match na ho, toh general portal par bhej do
    if not best_match or max_matches == 0:
        best_match = "Department of Administrative Reforms and Public Grievances (General Portal)"
        
    # SYNCED WITH MAIN.PY: Key name is strictly 'ministry'
    return {"ministry": best_match}