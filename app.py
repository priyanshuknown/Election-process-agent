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
    
    import google.generativeai as genai
    from dotenv import load_dotenv
    
    # Load env vars
    load_dotenv()
    
    # Try to initialize Gemini
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return jsonify({
            "response": "I'm sorry, my advanced AI brain is currently offline (Missing API Key). Please set up your GEMINI_API_KEY to enable intelligent chatting!||SUGGESTION:Go to Voting Journey"
        })
        
    try:
        genai.configure(api_key=api_key)
        
        system_instruction = """
        You are VoteMate, an intelligent, helpful, and friendly AI election assistant for Indian voters.
        Your goal is to guide first-time voters and answer questions about the Indian election process.
        
        Current Context:
        - It is currently May 2026.
        - Ongoing Elections: West Bengal State Assembly (Phase 1-3 done, final phases remaining), Tamil Nadu State Assembly, Kerala State Assembly.
        - Upcoming Elections: UP (2027), Punjab (2027), Gujarat (2027).
        - Completed Elections: 2024 Lok Sabha (NDA won), Bihar (2025), Delhi (2025).
        
        Capabilities of this App:
        - We have a "Timeline" page for election dates.
        - We have a "Booth Finder" where users enter their 6-digit PIN code to find their polling booth.
        - We have a "Voting Journey" step-by-step guide.
        - We have a "Document Guide" for valid ID proofs (Voter ID, Aadhaar, PAN, Driving License, Passport).
        
        Rules:
        - Be concise, direct, and conversational.
        - If the user asks about timelines or results, use the context provided above.
        - If the user asks how to find a polling booth, tell them to use the Booth Finder feature and enter their PIN code.
        - Do not generate fake election results. If you don't know, say so.
        
        You can append one of the following exact strings at the VERY END of your response to suggest a quick link to the user:
        ||SUGGESTION:Go to Voting Journey
        ||SUGGESTION:Go to Booth Finder
        ||SUGGESTION:View Document Guide
        ||SUGGESTION:Check Timeline
        
        Only append ONE suggestion if it makes sense for the user's query.
        """
        
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system_instruction
        )
        
        response = model.generate_content(message)
        return jsonify({"response": response.text})
        
    except Exception as e:
        return jsonify({
            "response": f"I experienced an error connecting to my AI brain. Please try again later. ({str(e)})"
        })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
