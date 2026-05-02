# VoteMate – Smart Election Guide Assistant 🇮🇳🗳️

VoteMate is an interactive, user-friendly web application designed to help Indian citizens—especially first-time voters—navigate the complex democratic election process. From checking eligibility and finding polling booths to tracking real-time election timelines and asking questions to an AI assistant, VoteMate covers everything a voter needs to know.

---

## ✨ Features

- 🧠 **AI Election Assistant**: Powered by the **Google Gemini API**, a smart chatbot that provides dynamic, context-aware answers about the election process, current election timelines, and guides users to relevant app features.
- 🎯 **Eligibility Checker**: A quick tool to check if a user meets the age and citizenship criteria to vote in India.
- 🗺️ **Step-by-Step Voting Journey**: A guided, interactive checklist (with backend progress tracking) that takes a voter from registration to casting their ballot.
- 📅 **Dynamic Election Timeline**: Tracks ongoing, upcoming, and recently completed elections across various Indian states, complete with countdowns and historical results.
- 📍 **Smart Polling Booth Finder**: Uses the user's 6-digit PIN code to generate mock polling booth locations, augmented with real district/state data via the PostalPincode API.
- 📄 **Document Guide**: Clear instructions on valid IDs and forms needed (Form 6, Form 8, etc.).
- ❓ **Election Quiz**: A fun, interactive quiz to test your knowledge of Indian democracy.

---

## 🛠️ Technology Stack

- **Frontend**: HTML5, Vanilla JavaScript, Bootstrap 5 (Custom Glassmorphism UI)
- **Backend**: Python, Flask, Werkzeug
- **Database**: SQLite (for persistent user journey tracking)
- **AI & APIs**: Google Generative AI (Gemini 2.5 Flash), PostalPincode.in API

---

## 🚀 Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/priyanshuknown/Election-process-agent.git
cd Election-process-agent
```

### 2. Install Dependencies
Ensure you have Python installed. Install the required Python packages:
```bash
pip install -r requirements.txt
```

### 3. Set Up the AI API Key
For the AI Assistant to function, you need a Google Gemini API Key.
1. Create a file named `.env` in the root directory.
2. Get your free API key from [Google AI Studio](https://aistudio.google.com/).
3. Add it to the `.env` file like this:
```env
GEMINI_API_KEY="your_api_key_here"
```
*(Note: The `.env` file is included in `.gitignore` to prevent secret leakage).*

### 4. Run the Application
Start the Flask development server:
```bash
python app.py
```
Open your web browser and navigate to `http://127.0.0.1:5000` to start using VoteMate!

---

## 🔒 Security Notice
Do not push your `.env` file to public repositories. If your API key is exposed, Google will automatically detect the leak and revoke it. Ensure your `.gitignore` contains `.env`.
