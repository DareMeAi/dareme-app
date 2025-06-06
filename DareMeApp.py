from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__, static_url_path='', static_folder='.')
CORS(app)

# Use a writable path for Render's file system
waitlist_path = os.path.join('/tmp', 'WaitList.txt')

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')


print(f"[DEBUG] Saving to: {waitlist_path}")

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
        print(f"[✖] Error writing to file: {repr(e)}")
        return jsonify({'message': 'Failed to write to file'}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
