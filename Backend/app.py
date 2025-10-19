from flask import Flask, request, jsonify
import os
import sys
# Add the project root to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import json # Added import for json

# import AI processing functions (from ai_models folder)
from ai_models.text_processor import extract_text_from_file
from ai_models.question_generator import generate_quiz_questions

# import database setup
from Database.database_setup import (
    setup_database, get_db_config, get_pooled_connection,
    DB_NAME, DB_HOST, DB_USER, DB_PASSWORD, DB_PORT
)

# load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# In-memory store for job statuses and results (replace with a proper database/cache in production)
job_statuses = {}

# Database connection helper with error handling
def get_db_connection():
    """Get database connection or None if database is unavailable."""
    try:
        # Use pooled connections to avoid creating a new TCP connection each request
        conn = get_pooled_connection()
        return conn
    except mysql.connector.Error as err:
        print(f"Failed to get pooled DB connection: {err}")
        return None
    except Exception as e:
        print(f"Unexpected error getting pooled DB connection: {e}")
        return None

def check_db_connection():
    """Check if database is available and return status."""
    # Perform a quick live check rather than relying on a startup-time flag
    try:
        conn = get_pooled_connection()
        if conn:
            conn.close()  # return to pool
            return True
        return False
    except Exception as e:
        print(f"Database connectivity check failed: {e}")
        return False

@app.route('/api/register', methods=['POST'])
def register_user():
    data = request.get_json()
    mail = data.get('mail')
    password = data.get('password')

    if not mail or not password:
        return jsonify({"error": "Mail and password are required"}), 400

    # Check if database is available
    if not check_db_connection():
        return jsonify({
            "error": "Database connection unavailable",
            "message": "Registration service is temporarily unavailable. Please try again later."
        }), 503

    hashed_password = generate_password_hash(password)

    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                "error": "Database connection failed",
                "message": "Unable to connect to the database. Please try again later."
            }), 503
            
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (mail, password) VALUES (%s, %s)", (mail, hashed_password))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "User registered successfully"}), 201
    except mysql.connector.Error as err:
        if err.errno == 1062: # Duplicate entry for UNIQUE constraint
            return jsonify({"error": "Mail already registered"}), 409
        print(f"Error during registration: {err}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/login', methods=['POST'])
def login_user():
    data = request.get_json()
    mail = data.get('mail')
    password = data.get('password')

    if not mail or not password:
        return jsonify({"error": "Mail and password are required"}), 400

    # Check if database is available
    if not check_db_connection():
        return jsonify({
            "error": "Database connection unavailable",
            "message": "Login service is temporarily unavailable. You can still use the app in demo mode."
        }), 503

    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                "error": "Database connection failed",
                "message": "Unable to connect to the database. Please try again later."
            }), 503
            
        cursor = conn.cursor(dictionary=True) # Return rows as dictionaries
        cursor.execute("SELECT * FROM users WHERE mail = %s", (mail,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user['password'], password):
            # In a real app, you'd generate a session token or JWT here
            return jsonify({"message": "Login successful", "user_id": user['user_id'], "mail": user['mail']}), 200
        else:
            return jsonify({"error": "Invalid mail or password"}), 401
    except mysql.connector.Error as err:
        print(f"Error during login: {err}")
        return jsonify({"error": "Internal server error"}), 500
    except Exception as e:
        print(f"Unexpected error during login: {e}")
        return jsonify({"error": "Internal server error"}), 500

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
        print(f"DEBUG: File saved to {filepath}") # Added debug print

        num_questions = request.form.get('numQuestions', type=int)
        duration = request.form.get('duration', type=int)
        mode = request.form.get('mode')
        user_id = request.form.get('userId', type=int) # Get user_id from form data
        quiz_title = request.form.get('quizTitle') # Get quizTitle from form data

        if not user_id:
            return jsonify({"error": "User ID is required to save a quiz."}), 400
        if not quiz_title:
            return jsonify({"error": "Quiz title is required."}), 400

        print(f"DEBUG: Quiz parameters - numQuestions: {num_questions}, duration: {duration}, mode: {mode}, userId: {user_id}, quizTitle: {quiz_title}") # Added debug print

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
            print(f"DEBUG: Starting text extraction for job {job_id}...") # Added debug print
            extracted_text = extract_text_from_file(filepath)
            print(f"DEBUG: Text extracted. Length: {len(extracted_text)} characters. First 200 chars: {extracted_text[:200]}...") # Added debug print

            # --- CRITICAL: Check if extracted_text is actually sufficient ---
            if not extracted_text or (len(extracted_text) < 100 and num_questions > 1):
                raise ValueError("The provided text is too short to generate meaningful quiz questions. Please provide more content.")

            print(f"DEBUG: Generating quiz questions for job {job_id} with Groq...") # Added debug print
            generated_quiz_data = generate_quiz_questions(extracted_text, num_questions, mode)
            print(f"DEBUG: Groq API response (generated_quiz_data): {generated_quiz_data}") # Added debug print
            
            # --- NEW LOGIC: Handle Groq's error response ---
            # Check if the overall response from Groq indicates an error
            if generated_quiz_data and 'questions' in generated_quiz_data and isinstance(generated_quiz_data['questions'], dict) and 'error' in generated_quiz_data['questions']:
                groq_error = generated_quiz_data['questions']['error']
                raise RuntimeError(f"Groq API returned an error: {groq_error}")

            # Ensure questions are always an array, even if Groq returns a single object
            raw_questions = generated_quiz_data.get("questions", [])
            
            if isinstance(raw_questions, dict):
                # If Groq returned a single question object directly under "questions", wrap it in a list
                questions_list = [raw_questions]
            elif isinstance(raw_questions, list):
                # If Groq returned a list of questions (as intended), use it directly
                questions_list = raw_questions
            else:
                # Fallback for unexpected format, default to empty list and log a warning
                print(f"WARNING: Unexpected format for questions from Groq, defaulting to empty list: {type(raw_questions)}")
                questions_list = []

            # Check if any questions were actually generated
            if not questions_list:
                raise RuntimeError("Groq API generated no questions, or the output format was unexpected/empty.")

            print(f"DEBUG: Final questions_list before session creation: {questions_list}") # Added debug print

            # --- NEW LOGIC: Validate number of generated questions ---
            if len(questions_list) < num_questions:
                print(f"WARNING: Groq API generated {len(questions_list)} questions, but {num_questions} were requested for job {job_id}.")
            
            # We need to construct a full QuizSession object that matches frontend's api.ts
            quiz_session = {
                "id": job_id, # Use job_id as session_id for simplicity
                "questions": questions_list, # Use the ensured list of questions
                "mode": mode,
                "duration": duration if mode == 'exam' else None,
                "startTime": "2023-10-27T10:00:00Z" # You might want to generate this dynamically
            }

            job_statuses[job_id]["status"] = "completed"
            job_statuses[job_id]["session"] = quiz_session
            print(f"DEBUG: Job {job_id} completed successfully.") # Added debug print

            # Save the generated quiz to the database if available
            if check_db_connection():
                try:
                    conn = get_db_connection()
                    if conn:
                        cursor = conn.cursor()
                        insert_query = """
                        INSERT INTO quizzes (user_id, title, quiz_data, mode, duration)
                        VALUES (%s, %s, %s, %s, %s)
                        """
                        cursor.execute(insert_query, (
                            user_id,
                            quiz_title,
                            json.dumps(quiz_session), # Store quiz_session as JSON string
                            mode,
                            duration if mode == 'exam' else None
                        ))
                        conn.commit()
                        quiz_id = cursor.lastrowid
                        cursor.close()
                        conn.close()
                        print(f"DEBUG: Quiz saved to database with ID: {quiz_id}")
                        job_statuses[job_id]["quiz_id"] = quiz_id # Store quiz_id in job_statuses
                    else:
                        print("WARNING: Could not save quiz to database - connection failed")
                        job_statuses[job_id]["db_save_warning"] = "Quiz generated but not saved to database"
                except mysql.connector.Error as db_err:
                    print(f"WARNING: Database error while saving quiz: {db_err}")
                    # Don't fail the entire job, just warn about DB save failure
                    job_statuses[job_id]["db_save_warning"] = "Quiz generated but could not be saved to database"
            else:
                print("INFO: Database not available - quiz generated but not saved")
                job_statuses[job_id]["db_save_warning"] = "Database unavailable - quiz not saved"

        except (ValueError, RuntimeError) as e: # Catch specific errors for better handling
            job_statuses[job_id]["status"] = "failed"
            job_statuses[job_id]["error"] = str(e)
            print(f"ERROR: Job {job_id} failed: {e}")
        except Exception as e:
            job_statuses[job_id]["status"] = "failed"
            job_statuses[job_id]["error"] = "An unexpected error occurred during quiz generation."
            print(f"ERROR: Job {job_id} failed with an unexpected error: {e}")
        finally:
            # Clean up the uploaded file after processing
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"DEBUG: Cleaned up uploaded file: {filepath}") # Added debug print


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
        if "quiz_id" in job_info: # Include quiz_id if available
            response_data["quizId"] = job_info["quiz_id"]
    elif job_info["status"] == "failed":
        response_data["error"] = job_info["error"]
    
    return jsonify(response_data), 200

@app.route('/api/quizzes/user/<int:user_id>', methods=['GET'])
def get_user_quizzes(user_id):
    # Check if database is available
    if not check_db_connection():
        return jsonify({
            "error": "Database connection unavailable",
            "message": "Quiz history is temporarily unavailable. The app can still generate new quizzes.",
            "quizzes": []  # Return empty array so frontend can handle gracefully
        }), 503
    
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                "error": "Database connection failed",
                "message": "Unable to retrieve quiz history at this time.",
                "quizzes": []
            }), 503
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT quiz_id, title, mode, duration, created_at, quiz_data FROM quizzes WHERE user_id = %s", (user_id,))
        quizzes = cursor.fetchall()
        cursor.close()
        conn.close()

        if not quizzes:
            return jsonify({"message": "No quizzes found for this user"}), 404

        # Parse quiz_data JSON for each quiz
        for quiz in quizzes:
            quiz['quiz_data'] = json.loads(quiz['quiz_data'])
        
        return jsonify(quizzes), 200
    except mysql.connector.Error as err:
        print(f"Error fetching user quizzes: {err}")
        return jsonify({"error": "Internal server error"}), 500
    except Exception as e:
        print(f"Unexpected error fetching user quizzes: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/quizzes/<int:quiz_id>', methods=['GET'])
def get_quiz_by_id(quiz_id):
    # Check if database is available
    if not check_db_connection():
        return jsonify({
            "error": "Database connection unavailable",
            "message": "Quiz retrieval is temporarily unavailable."
        }), 503
    
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                "error": "Database connection failed",
                "message": "Unable to retrieve quiz at this time."
            }), 503
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT quiz_id, title, mode, duration, created_at, quiz_data FROM quizzes WHERE quiz_id = %s", (quiz_id,))
        quiz = cursor.fetchone()
        cursor.close()
        conn.close()

        if not quiz:
            return jsonify({"error": "Quiz not found"}), 404

        # Parse quiz_data JSON
        quiz['quiz_data'] = json.loads(quiz['quiz_data'])
        
        return jsonify(quiz), 200
    except mysql.connector.Error as err:
        print(f"Error fetching quiz by ID: {err}")
        return jsonify({"error": "Internal server error"}), 500
    except Exception as e:
        print(f"Unexpected error fetching quiz by ID: {e}")
        return jsonify({"error": "Internal server error"}), 500
    
#############
### tests ###
#############


@app.route("/api/health")
def health_check():
    """Health check endpoint that also reports database status."""
    db_status = "connected" if check_db_connection() else "disconnected"
    
    response = {
        "status": "ok",
        "database": db_status,
        "message": "Application is running"
    }
    
    if db_status == "disconnected":
        response["warning"] = "Database is not available. Some features may be limited."
    
    return jsonify(response), 200

@app.route("/api/db-status")
def db_status():
    """Check database connectivity status."""
    if check_db_connection():
        # Try an actual connection to verify
        try:
            conn = get_pooled_connection()
            if conn:
                conn.close()  # return to pool
                return jsonify({
                    "status": "connected",
                    "message": "Database is available and responding",
                    "host": DB_HOST,
                    "port": DB_PORT
                }), 200
        except:
            pass
    
    return jsonify({
        "status": "disconnected",
        "message": "Database is not available. Application is running in limited mode.",
        "warning": "User registration, login, and quiz history features are unavailable."
    }), 503


#############
###  run  ###
#############



if __name__ == '__main__':
    # Try to setup database but continue even if it fails
    db_setup_success = setup_database()
    
    if not db_setup_success:
        print("\n" + "="*60)
        print("WARNING: Starting application without database")
        print("The following features will be unavailable:")
        print("  - User registration and login")
        print("  - Saving quiz history")
        print("  - Retrieving past quizzes")
        print("\nQuiz generation will still work!")
        print("="*60 + "\n")
    
    app.run(host='0.0.0.0', debug=True, port=8000)
