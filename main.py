from flask import Flask, request, session
import smtplib

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Create a dictionary to store the session data
sessions = {}

# Route to receive GPS information and start a new session
@app.route('/start_session', methods=['POST'])
def start_session():
    data = request.json
    session['email'] = data['email']
    session['start_location'] = data['location']
    session['start_time'] = data['time']
    session['end_password'] = data['end_password']
    session['gps_data'] = []
    sessions[session['end_password']] = session.copy()
    return 'Session started'

# Route to add GPS data to the session
@app.route('/add_data', methods=['POST'])
def add_data():
    data = request.json
    session['gps_data'].append(data)
    sessions[session['end_password']] = session.copy()
    return 'Data added'

# Route to end the session
@app.route('/end_session', methods=['POST'])
def end_session():
    data = request.json
    if data['end_password'] == session['end_password']:
        session['end_time'] = data['time']
        sessions[session['end_password']] = session.copy()
        del sessions[session['end_password']]
        return 'Session ended'
    else:
        return 'Invalid password'

# Function to send warning email if a session has not been ended
def send_warning_email():
    for password, session_data in sessions.items():
        if 'end_time' not in session_data:
            email = session_data['email']
            message = 'Your session started at {} from {} is still active. Please end your session with the password: {}'.format(session_data['start_time'], session_data['start_location'], session_data['end_password'])
            # Replace the placeholders below with your own email and password
            sender_email = 'your_email_here'
            sender_password = 'your_password_here'
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, message)
            server.quit()

# Run the send_warning_email function every 30 minutes
# Replace the placeholders below with your own email and password
if __name__ == '__main__':
    import threading
    import time
    sender_email = 'your_email_here'
    sender_password = 'your_password_here'
    threading.Timer(1800.0, send_warning_email).start()
    app.run(debug=True)
