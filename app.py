from flask import Flask, render_template, session, request
import json
import random
import joblib
import pandas as pd

app = Flask(__name__)
app.secret_key = 'your_secret_key'  


def load_questions(age_group):
    if 1 <= age_group < 12:
        filename = 'questions_under_12.json'
    elif 12 <= age_group <= 17:
        filename = 'questions_12_17.json'
    elif age_group >= 18:
        filename = 'questions_above_18.json'
    else:
        return None 

    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return None  # Handle missing file gracefully

# Function to get questions based on age group
def get_questions_for_age_group(age):
    # Load questions for the given age group
    questions = load_questions(age)
    if questions is None:
        return None  # Handle missing questions gracefully

    # Select one random question for each parameter
    selected_questions = [
        {
            "parameter": parameter,
            "question": random.choice(parameter_questions)  # Randomly pick a question
        }
        for parameter, parameter_questions in questions.items()
    ]

    return selected_questions


# Function to load the appropriate model based on age
def load_model(age_group):
    try:
        if 1 <= age_group <= 12:
            return joblib.load('model/eqModelKids.pkl')
        elif 12 <= age_group <= 17:
            return joblib.load('model/eqModelTeen.pkl')
        elif age_group >= 18:
            return joblib.load('model/eqModelAdult.pkl')
    except FileNotFoundError:
        return None  

# Route to show age input
@app.route('/')
def index():
    return render_template('index.html')

# Route to show questions based on age group
@app.route('/questions', methods=['POST'])
def questions():
    try:
        age = int(request.form['age'])
        session['age'] = age  # Store age in session for future use
    except ValueError:
        return "Invalid age. Please enter a valid number."

    questions = get_questions_for_age_group(age)
    if questions is None:
        return "Invalid age group or no questions available."

    return render_template('questions.html', questions=questions, age=age)


@app.route('/predict', methods=['POST'])
def predict():
    user_input = {}
    age = session.get('age')  

    if not age:
        return "Age is missing. Please start again."

    # Process form data for questions
    for key, value in request.form.items():
        try:
            user_input[key] = int(value)
        except ValueError:
            user_input[key] = 0 
            
    print("User Inputs:", user_input) 
    model = load_model(age)
    if model is None:
        print("Model not found for age group:", age)
        return "Prediction model for the specified age group is not available."

    # Prepare input for the model
    input_values = [user_input.get(param, 0) for param in model.feature_names_in_]
    input_df = pd.DataFrame([input_values], columns=model.feature_names_in_)
    print("Input DataFrame for Model:", input_df)
    try:
        predicted_score = model.predict(input_df)[0]
        print("Predicted EQ Score:", predicted_score)
    except Exception as e:
        print("Error during model prediction:", str(e))
        return "Error during prediction. Please check your inputs or model."

    # Evaluate EQ score
    age_eval = evaluate_eq(age, predicted_score)
    average_eq = 50
    # Generate recommendations
    recommendation = generate_recommendations(age, predicted_score)
    recommendations = provide_recommendations(user_input, predicted_score, average_eq)

    return render_template(
        'result.html',
        score=predicted_score,
        age_eval=age_eval,
        age=age,
        recommendations=recommendations,
        recommendation=recommendation,

    )

# Function to evaluate EQ based on age and score
def evaluate_eq(age, score):
    if 1 <= age <= 12:
        if score < 50:
            return "Low EQ"
        elif 50 <= score <= 70:
            return "Average EQ"
        elif 70 < score <= 85:
            return "High EQ"
        else:
            return "Very High EQ"
    elif 12 <= age <= 17:
        if score < 70:
            return "Low EQ"
        elif 70 <= score <= 80:
            return "Average EQ"
        elif 80 < score <= 90:
            return "High EQ"
        else:
            return "Very High EQ"
    elif age >= 18:
        if score < 80:
            return "Low EQ"
        elif 80 <= score <= 90:
            return "Average EQ"
        elif 90 < score <= 100:
            return "High EQ"
        else:
            return "Very High EQ"
    return "Invalid age group."

# Function to generate recommendations based on age and EQ score
def generate_recommendations(age, score):
    recommendations = []

    if 1 <= age <= 12:
        if score < 50:
            recommendations = [
                "Develop better emotional regulation strategies.",
                "Engage more in social interactions to improve emotional understanding.",
                "Practice empathy and kindness in daily activities.",
            ]
        elif score <= 70:
            recommendations = [
                "Continue practicing mindfulness and empathy.",
                "Engage in collaborative activities.",
                "Practice managing emotions during stressful situations.",
            ]
        elif score <= 85:
            recommendations = [
                "You're doing great! Keep developing emotional awareness.",
                "Work on building positive relationships.",
            ]
        else:
            recommendations = [
                "Outstanding emotional intelligence! Keep mentoring others.",
            ]
    elif 12 <= age <= 17:
        if score < 70:
            recommendations = [
                "Improve emotional self-regulation.",
                "Participate in peer support programs.",
                "Focus on stress management.",
            ]
        elif score <= 80:
            recommendations = [
                "Maintain a balanced lifestyle to enhance EQ.",
                "Practice leadership in team activities.",
                "Focus on healthy communication skills.",
            ]
        elif score <= 90:
            recommendations = [
                "Excellent emotional awareness! Consider mentoring others.",
                "Explore career opportunities requiring high EQ.",
            ]
        else:
            recommendations = [
                "Mastered emotional intelligence! Inspire others.",
            ]
    elif age >= 18:
        if score < 80:
            recommendations = [
                "Develop emotional awareness in work and relationships.",
                "Practice conflict resolution and emotional regulation.",
            ]
        elif score <= 90:
            recommendations = [
                "Excellent EQ! Consider coaching others.",
                "Enhance leadership skills further.",
            ]
        elif score <= 110:
            recommendations = [
                "Very high EQ! Foster positive team dynamics.",
            ]
        else:
            recommendations = [
                "Outstanding EQ. Train others in emotional skills.",
            ]

    return recommendations
# Function to provide recommendations based on specific parameters
def provide_recommendations(user_input, predicted_score, average_eq):
    recommendations = []

    # Check for each parameter and provide relevant recommendations
    if user_input.get('Behaviour', 0) <=3:  # Anxious
        recommendations.append("Engage in relaxation exercises to manage anxiety.")
    if user_input.get('EyeContact', 0)<=3:  # Avoids
        recommendations.append("Practice maintaining eye contact during conversations.")
    if user_input.get('SocialRelationship', 0) <=3:  # Weak
        recommendations.append("Participate in team activities to improve social skills.")
    if user_input.get('SpeechConveyance', 0)<=3:  # Slurred or unclear speech
        recommendations.append("Work on speaking clearly by practicing articulation exercises.")
    if user_input.get('ConcentrationLevel', 0) <=3:  # Distracted
        recommendations.append("Try mindfulness exercises to improve your concentration.")
    if user_input.get('SelfRegulation', 0) <=3:  # Low self-regulation
        recommendations.append("Focus on techniques like breathing exercises to enhance self-control.")
    if user_input.get('StressLevel', 0) <=3:  # High stress
        recommendations.append("Manage stress by practicing relaxation techniques like deep breathing.")
    if user_input.get('BodyMind', 0) <=3:  # Poor body-mind coordination
        recommendations.append("Try activities like yoga or dancing to improve body-mind coordination.")
    if user_input.get('Empathy', 0) <=3: # Low empathy
        recommendations.append("Develop empathy by engaging in activities that require perspective-taking.")
    if user_input.get('Motivation', 0) <=3:  # Low motivation
        recommendations.append("Set small, achievable goals to increase your motivation.")
    if user_input.get('SelfAwareness', 0) <=3:  # Low self-awareness
        recommendations.append("Engage in journaling or mindfulness practices to improve self-awareness.")
    if user_input.get('Mindfulness', 0) <=3:  # Low mindfulness
        recommendations.append("Practice daily mindfulness exercises to improve awareness and focus.")
    if user_input.get('Creativity', 0) <=3:  # Low creativity
        recommendations.append("Participate in creative activities like drawing or brainstorming to boost creativity.")
    if user_input.get('TimeManagement', 0) <=3:  # Poor time management
        recommendations.append("Use tools like planners or apps to improve your time management skills.")
    if user_input.get('Optimism', 0) <=3:  # Low optimism
        recommendations.append("Focus on reframing negative thoughts to develop a more optimistic outlook.")

    # Add overall EQ-based recommendations
    if predicted_score < average_eq:
        recommendations.append("Consider focusing on areas like emotional regulation and empathy to improve your EQ.")
    elif predicted_score > average_eq + 10:
        recommendations.append("Your EQ is excellent! You can inspire others by sharing your emotional skills.")
    else:
        recommendations.append("Maintain your current practices to keep your EQ balanced and effective.")

    return recommendations


if __name__ == '__main__':
    app.run(debug=True)
