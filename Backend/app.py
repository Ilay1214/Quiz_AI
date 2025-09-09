from flask import Flask, request, jsonify 
import os
from flask_cors import CORS 
from dotenv import load_dotenv

# Import AI processing functions
from ai_models.text_processor import extract_text_from_file
from ai_models.question_generator import generate_quiz_questions

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# In-memory store for job statuses and results (replace with a proper database/cache in production)
job_statuses = {}

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
        
        # Initialize job status
        job_statuses[job_id] = {
            "status": "pending",
            "filepath": filepath,
            "num_questions": num_questions,
            "duration": duration,
            "mode": mode,
            "session": None,
            "error": None
        }

        # In a real application, you would ideally start a background task here
        # that calls extract_text_from_file and generate_quiz_questions.
        # For simplicity, we'll run it synchronously for now, but be aware
        # this will block the request until AI processing is done.
        try:
            extracted_text = extract_text_from_file(filepath)
            generated_quiz_data = generate_quiz_questions(extracted_text, num_questions, mode)
            
            # Assuming generated_quiz_data is like {"questions": [...]}
            # We need to construct a full QuizSession object that matches frontend's api.ts
            quiz_session = {
                "id": job_id, # Use job_id as session_id for simplicity
                "questions": generated_quiz_data.get("questions", []),
                "mode": mode,
                "duration": duration if mode == 'exam' else None,
                "startTime": "2023-10-27T10:00:00Z" # You might want to generate this dynamically
            }

            job_statuses[job_id]["status"] = "completed"
            job_statuses[job_id]["session"] = quiz_session
        except Exception as e:
            job_statuses[job_id]["status"] = "failed"
            job_statuses[job_id]["error"] = str(e)
            print(f"Error processing job {job_id}: {e}")
        finally:
            # Clean up the uploaded file after processing
            if os.path.exists(filepath):
                os.remove(filepath)


        return jsonify({"jobId": job_id}), 202

@app.route('/api/job-status/<job_id>', methods=['GET'])
def get_job_status(job_id):
    job_info = job_statuses.get(job_id)

    if not job_info:
        return jsonify({"error": "Job not found"}), 404
    
    response_data = {
        "status": job_info["status"],
    }

    if job_info["status"] == "completed":
        response_data["session"] = job_info["session"]
    elif job_info["status"] == "failed":
        response_data["error"] = job_info["error"]
    
    return jsonify(response_data), 200

if __name__ == '__main__':
    app.run(debug=True, port=8000)

