from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__, static_url_path='', static_folder='.')
CORS(app)

waitlist_path = os.path.join(os.path.dirname(__file__), 'WaitList.txt')

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/submit-email', methods=['POST'])
def submit_email():
    data = request.get_json()
    email = data.get('email', '').strip()

    if not email or '@' not in email or '.' not in email:
        print("[!] Invalid email blocked:", email)
        return jsonify({'message': 'Invalid email format'}), 400

    # Count entries fresh from file
    entry_number = 1
    if os.path.exists(waitlist_path):
        with open(waitlist_path, 'r') as f:
            lines = f.readlines()
            entry_number = len(lines) + 1
            for line in lines:
                if f", {email}\n" == line or line.strip().endswith(f", {email}"):
                    print(f"[=] Duplicate email blocked: {email}")
                    return jsonify({'message': 'Email already submitted'}), 409

    # Save new email
    try:
        with open(waitlist_path, 'a') as f:
            f.write(f"{entry_number}, {email}\n")
            print(f"[+] Saved: {entry_number}, {email}")
            return jsonify({
                'message': 'Email saved successfully',
                'entry': entry_number
            })
    except Exception as e:
        print("[✖] Error writing to file:", e)
        return jsonify({'message': 'Failed to write to file'}), 500

if __name__ == '__main__':
    app.run()
