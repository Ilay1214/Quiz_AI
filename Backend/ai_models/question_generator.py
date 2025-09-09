# Backend/ai_models/question_generator.py
import os
import json
from groq import Groq

def generate_quiz_questions(text: str, num_questions: int, mode: str) -> dict:
    """
    Generates quiz questions using the Groq API based on the provided text.
    """
    # Initialize Groq client
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY environment variable not set.")
    
    client = Groq(api_key=groq_api_key)

    # Construct the prompt
    system_message = f"""
    You are an AI assistant specialized in creating engaging and informative quiz questions from provided text.
    Your task is to generate {num_questions} quiz questions based on the following text.
    The quiz should be in '{mode}' mode.

    For each question, provide:
    - An 'id' (unique string)
    - The 'question' text
    - The 'type' of question (e.g., 'single' for multiple choice with one correct answer, 'multiple' for multiple choice with multiple correct answers, or 'text' for a short answer question).
    - 'options' (an array of strings) if the type is 'single' or 'multiple'.
    - 'correctAnswers' (an array of strings) containing the correct answer(s).
    - An 'explanation' (string) for the correct answer.

    The output should be a JSON array of quiz question objects.
    Example JSON structure:
    [
        {{
            "id": "q1",
            "question": "What is [Concept A]?",
            "type": "single",
            "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
            "correctAnswers": ["Option 2"],
            "explanation": "Explanation for Concept A."
        }},
        {{
            "id": "q2",
            "question": "Describe [Concept B].",
            "type": "text",
            "correctAnswers": ["Key aspects of Concept B"],
            "explanation": "Explanation for Concept B."
        }}
    ]
    """

    user_message = f"Generate {num_questions} quiz questions from the following text:\n\n{text}"

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system_message,
            },
            {
                "role": "user",
                "content": user_message,
            },
        ],
        model="llama-3.3-70b-versatile", # You can choose a different Groq model if preferred
        response_format={"type": "json_object"}, # Request JSON output
        temperature=0.7,
        max_tokens=2048, # Adjust based on expected question length and number
    )

    try:
        # The AI's response will be a string containing JSON
        quiz_data = json.loads(chat_completion.choices[0].message.content)
        # Assuming the AI returns a list of questions directly
        return {"questions": quiz_data}
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON from Groq API response: {e}")
        print(f"Raw AI response: {chat_completion.choices[0].message.content}")
        raise RuntimeError("Failed to parse quiz questions from AI response.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise

if __name__ == '__main__':
    # Example usage (for testing purposes)
    sample_text = """
    Artificial intelligence (AI) is intelligence demonstrated by machines,
    as opposed to the natural intelligence displayed by animals including humans.
    Leading AI textbooks define the field as the study of "intelligent agents":
    any device that perceives its environment and takes actions that maximize its chance of successfully achieving its goals.
    """
    try:
        generated_quiz = generate_quiz_questions(sample_text, 2, "practice")
        print(json.dumps(generated_quiz, indent=2))
    except Exception as e:
        print(f"Error generating quiz: {e}")