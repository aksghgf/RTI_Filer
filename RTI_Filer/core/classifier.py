import json
import os
import re

def load_ministries_data():
    """Loads the 80+ Central Ministries database with dynamic path resolution."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    path_option_1 = os.path.join(current_dir, "data", "ministries.json")
    path_option_2 = os.path.join(current_dir, "..", "data", "ministries.json")
    path_option_3 = os.path.join(current_dir, "ministries.json")
    
    json_path = None
    if os.path.exists(path_option_1):
        json_path = path_option_1
    elif os.path.exists(path_option_2):
        json_path = path_option_2
    elif os.path.exists(path_option_3):
        json_path = path_option_3

    # 1. Agar koi path valid mila, toh use load karne ki koshish karo
    if json_path:
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Warning: Failed to read JSON file ({str(e)}). Using fallback.")

    # 2. 👑 FIXED INDENTATION: Agar json_path nahi mila YA file read fail ho gayi,
    # toh yeh default database safe side return hoga (Function ke main block mein hai ye)
    print("⚠️ Notice: Deploying fallback ministry keywords database.")
    return {
        "ministries": [
            {
                "name": "Ministry of Road Transport and Highways",
                "keywords": ["road", "highway", "sarak", "contractor", "pothole", "construction", "toll", "bypass"]
            },
            {
                "name": "Ministry of Consumer Affairs, Food and Public Distribution",
                "keywords": ["ration", "pds", "food grain", "consumer", "dealer", "chawal", "gehu"]
            },
            {
                "name": "Ministry of Railways",
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
            best_match = ministry["name"]
            
    # Agar koi bhi keyword match na ho, toh general portal par bhej do
    if not best_match or max_matches == 0:
        best_match = "Department of Administrative Reforms and Public Grievances (General Portal)"
        
    # SYNCED WITH MAIN.PY: Key name is strictly 'ministry'
    return {"ministry": best_match}