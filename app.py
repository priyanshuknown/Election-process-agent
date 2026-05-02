import os
import sqlite3
from flask import Flask, render_template, request, jsonify, g

app = Flask(__name__)
DATABASE = 'database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS progress (
                session_id TEXT PRIMARY KEY,
                step1 INTEGER DEFAULT 0,
                step2 INTEGER DEFAULT 0,
                step3 INTEGER DEFAULT 0,
                step4 INTEGER DEFAULT 0,
                step5 INTEGER DEFAULT 0
            )
        ''')
        db.commit()

# Ensure DB is created
with app.app_context():
    init_db()

# ---- ROUTES ----

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/eligibility')
def eligibility():
    return render_template('eligibility.html')

@app.route('/journey')
def journey():
    return render_template('journey.html')

@app.route('/timeline')
def timeline():
    return render_template('timeline.html')

@app.route('/booth')
def booth():
    return render_template('booth.html')

@app.route('/documents')
def documents():
    return render_template('documents.html')

@app.route('/quiz')
def quiz():
    return render_template('quiz.html')

# ---- API ENDPOINTS ----

@app.route('/api/progress/<session_id>', methods=['GET'])
def get_progress(session_id):
    db = get_db()
    cur = db.execute('SELECT * FROM progress WHERE session_id = ?', (session_id,))
    row = cur.fetchone()
    if row:
        return jsonify(dict(row))
    else:
        # Create default
        db.execute('INSERT INTO progress (session_id) VALUES (?)', (session_id,))
        db.commit()
        return jsonify({'session_id': session_id, 'step1': 0, 'step2': 0, 'step3': 0, 'step4': 0, 'step5': 0})

@app.route('/api/progress/<session_id>', methods=['POST'])
def update_progress(session_id):
    data = request.json
    step = data.get('step')
    status = data.get('status') # 1 or 0
    
    if step not in ['step1', 'step2', 'step3', 'step4', 'step5']:
        return jsonify({'error': 'Invalid step'}), 400
        
    db = get_db()
    
    # Ensure exists
    cur = db.execute('SELECT * FROM progress WHERE session_id = ?', (session_id,))
    if not cur.fetchone():
        db.execute('INSERT INTO progress (session_id) VALUES (?)', (session_id,))
        
    db.execute(f'UPDATE progress SET {step} = ? WHERE session_id = ?', (status, session_id))
    db.commit()
    return jsonify({'success': True})

@app.route('/api/booth', methods=['POST'])
def find_booth():
    data = request.json
    pincode = data.get('pincode', '').strip()
    
    # Mock Database for booths returning multiple results per pincode
    mock_db = {
        "110001": [
            {"name": "Connaught Place Govt School", "address": "Block A, CP, New Delhi, Delhi", "distance": "0.5 km"},
            {"name": "NDMC Primary School", "address": "Block C, CP, New Delhi, Delhi", "distance": "1.1 km"},
            {"name": "Town Hall Polling Center", "address": "Parliament Street, New Delhi, Delhi", "distance": "2.0 km"}
        ],
        "400001": [
            {"name": "Fort Municipal School", "address": "Fort, Mumbai, Maharashtra", "distance": "1.2 km"},
            {"name": "Colaba Public School", "address": "Colaba Causeway, Mumbai, Maharashtra", "distance": "2.5 km"}
        ],
        "560001": [
            {"name": "MG Road Primary School", "address": "MG Road, Bengaluru, Karnataka", "distance": "0.8 km"},
            {"name": "Cubbon Park Community Hall", "address": "Cubbon Park, Bengaluru, Karnataka", "distance": "1.6 km"},
            {"name": "Shivaji Nagar Ward Office", "address": "Shivaji Nagar, Bengaluru, Karnataka", "distance": "3.1 km"}
        ]
    }
    
    if pincode in mock_db:
        return jsonify({"found": True, "booths": mock_db[pincode]})
    elif len(pincode) == 6 and pincode.isdigit():
        import random
        import urllib.request
        import json
        
        # Seed the random number generator with the pincode so the same pincode always gives the same results
        random.seed(int(pincode))
        
        # Try to fetch real city/state from free API
        city_state = ""
        try:
            req = urllib.request.Request(f'https://api.postalpincode.in/pincode/{pincode}', headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=3) as response:
                data = json.loads(response.read().decode())
                if data and data[0]['Status'] == 'Success':
                    post_office = data[0]['PostOffice'][0]
                    district = post_office.get('District', '')
                    state = post_office.get('State', '')
                    if district and state:
                        city_state = f", {district}, {state}"
        except Exception:
            pass # Silently fallback if API fails
            
        prefixes = ["Government", "St. Mary's", "DAV", "Kendriya Vidyalaya", "Municipal", "Public", "Saraswati", "Adarsh", "National"]
        suffixes = ["Primary School", "High School", "Community Center", "Degree College", "Polytechnic", "Inter College"]
        roads = ["Main Road", "Station Road", "Temple Road", "Market Street", "Hospital Road", "Link Road"]
        
        num_booths = random.randint(2, 4)
        generated_booths = []
        
        for i in range(num_booths):
            name = f"{random.choice(prefixes)} {random.choice(suffixes)}"
            base_address = f"{random.randint(1, 100)}, {random.choice(roads)}, Sector {random.randint(1, 15)}"
            address = f"{base_address} - {pincode}{city_state}"
            distance = f"{round(random.uniform(0.5, 4.5), 1)} km"
            
            generated_booths.append({
                "name": name,
                "address": address,
                "distance": distance
            })
            
        return jsonify({
            "found": True, 
            "booths": generated_booths
        })
    else:
        return jsonify({"found": False, "error": "Invalid PIN code format. Please enter a valid 6-digit PIN."})

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '').lower()
    
    # Simple Rule-based Dictionary
    rules = {
        "hello": "Hi there! I am VoteMate. How can I help you with the election process today?",
        "hi": "Hello! I am VoteMate. Ask me anything about voting in India.",
        "voter id": "To get a Voter ID, you need to fill Form 6. You can do this online at the NVSP portal or through the Voter Helpline App.",
        "lost": "If you lost your Voter ID, you can apply for a duplicate one using Form 8 on the NVSP portal.",
        "documents": "Valid documents include Voter ID (EPIC), Aadhaar Card, PAN Card, Driving License, Passport, etc. Want to see the full list in the Document Guide?",
        "age": "You must be 18 years or older on the qualifying date (usually Jan 1st of the year) to be eligible to vote.",
        "where to vote": "You can find your polling booth using your PIN code in our Polling Booth finder, or check your EPIC number on the Election Commission website.",
        "nri": "NRIs can vote! They need to fill Form 6A to register as an overseas elector. However, they must be physically present at the polling booth to vote.",
        "online voting": "Currently, India does not allow online voting. You must visit your designated polling booth to cast your vote.",
        "first time": "Welcome, first-time voter! I recommend going to the 'Voting Journey' tab. It will guide you step-by-step from registration to voting day!"
    }
    
    response = "I'm not quite sure about that. Could you try rephrasing? You can ask me about 'voter ID', 'documents', 'age eligibility', or 'where to vote'."
    
    for key in rules:
        if key in message:
            response = rules[key]
            
            # Smart Suggestion logic
            if key == "voter id" or key == "first time":
                response += "||SUGGESTION:Go to Voting Journey"
            elif key == "where to vote":
                response += "||SUGGESTION:Go to Booth Finder"
            elif key == "documents":
                response += "||SUGGESTION:View Document Guide"
            break
            
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
