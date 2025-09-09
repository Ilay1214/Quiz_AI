from flask import Flask, request, jsonify 
import os
from flask_cors import CORS 

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/api/generate-questions', methods=['POST'])
def generate_questions():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        num_questions = request.form.get('numQuestions', type=int)
        duration = request.form.get('duration', type=int)
        mode = request.form.get('mode')
        
        job_id = f"job_{os.urandom(16).hex()}"

        return jsonify({"jobId": job_id}), 202

@app.route('/api/job-status/<job_id>', methods=['GET'])
def get_job_status(job_id):
    import time
    time.sleep(2) # Simulate processing time

    dummy_session = {
        "id": "quiz_session_123",
        "questions": [
            {
                "id": "q1",
                "question": "What is the capital of France?",
                "type": "single",
                "options": ["Berlin", "Madrid", "Paris", "Rome"],
                "correctAnswers": ["Paris"],
                "explanation": "Paris is the capital and most populous city of France."
            },
            {
                "id": "q2",
                "question": "Which of these are programming languages?",
                "type": "multiple",
                "options": ["Python", "HTML", "CSS", "JavaScript"],
                "correctAnswers": ["Python", "JavaScript"],
                "explanation": "Python and JavaScript are widely used programming languages. HTML and CSS are markup and stylesheet languages, respectively."
            }
        ],
        "mode": "practice",
        "startTime": "2023-10-27T10:00:00Z"
    }

    return jsonify({"status": "completed", "session": dummy_session}), 200

if __name__ == '__main__':
    app.run(debug=True, port=8000)

