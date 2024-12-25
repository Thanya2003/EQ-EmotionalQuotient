from flask import Flask, render_template, session, request
import json
import random
import joblib
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, Float, DateTime, String, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import numpy as np
from scipy import stats

# Database Setup
Base = declarative_base()

class EQAssessment(Base):
    __tablename__ = 'eq_assessments'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50))
    age = Column(Integer)
    eq_score = Column(Float)
    EyeContact=Column(Integer, default=0)
    Behaviour=Column(Integer, default=0)
    SocialRelationship=Column(Integer, default=0)
    SpeechConveyance=Column(Float, default=0)
    ConcentrationLevel=Column(Integer, default=0)
    SelfRegulation=Column(Integer, default=0)
    StressLevel=Column(Integer, default=0)
    BodyMind=Column(Integer, default=0)
    Empathy=Column(Integer, default=0)
    Motivation=Column(Integer, default=0)
    SelfAwareness=Column(Integer, default=0)
    Mindfulness=Column(Integer, default=0)
    Creativity=Column(Integer, default=0)
    TimeManagement=Column(Integer, default=0)
    Optimism=Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow)
    age_eval = Column(String(50)) 
    recommendations = Column(JSON)

app = Flask(__name__)
app.secret_key = 'thanya'

# Database setup
DATABASE_URI = "mysql+pymysql://Thanya:123Thanya@localhost/eq_assessment_db"
engine = create_engine(DATABASE_URI)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

class EQAnalyzer:
    def __init__(self, db_session):
        self.session = db_session
    
    def save_assessment(self, user_id, age, eq_score, parameter_scores, recommendations, age_eval):
        """Save assessment results to database"""
        assessment = EQAssessment(
            user_id=user_id,
            age=age,
            eq_score=eq_score,
            EyeContact=parameter_scores.get("EyeContact", 0),
            Behaviour=parameter_scores.get("Behaviour", 0),
            SocialRelationship=parameter_scores.get("SocialRelationship", 0),
            SpeechConveyance=parameter_scores.get("SpeechConveyance", 0),
            ConcentrationLevel=parameter_scores.get("ConcentrationLevel", 0),
            SelfRegulation=parameter_scores.get("SelfRegulation", 0),
            StressLevel=parameter_scores.get("StressLevel", 0),
            BodyMind=parameter_scores.get("BodyMind", 0),
            Empathy=parameter_scores.get("Empathy", 0),
            Motivation=parameter_scores.get("Motivation", 0),
            SelfAwareness=parameter_scores.get("SelfAwareness", 0),
            Mindfulness=parameter_scores.get("Mindfulness", 0),
            Creativity=parameter_scores.get("Creativity", 0),
            TimeManagement=parameter_scores.get("TimeManagement", 0),
            Optimism=parameter_scores.get("Optimism", 0),
            age_eval=age_eval,
            recommendations=recommendations
        )
        self.session.add(assessment)
        self.session.commit()
        return assessment.id
        

    def get_user_progress(self, user_id):
        """Get historical progress for a user"""
        assessments = self.session.query(EQAssessment)\
            .filter(EQAssessment.user_id == user_id)\
            .order_by(EQAssessment.timestamp)\
            .all()
        
        return {
            'scores': [a.eq_score for a in assessments],
            'timestamps': [a.timestamp for a in assessments],
            'EyeContact': [a.EyeContact for a in assessments],
            'Behaviour': [a.Behaviour for a in assessments],
            'SocialRelationship': [a.SocialRelationship for a in assessments],
            'SpeechConveyance': [a.SpeechConveyance for a in assessments],
            'ConcentrationLevel': [a.ConcentrationLevel for a in assessments],
            'SelfRegulation': [a.SelfRegulation for a in assessments],
            'StressLevel': [a.StressLevel for a in assessments],
            'BodyMind': [a.BodyMind for a in assessments],
            'Empathy': [a.Empathy for a in assessments],
            'Motivation': [a.Motivation for a in assessments],
            'SelfAwareness': [a.SelfAwareness for a in assessments],
            'Mindfulness': [a.Mindfulness for a in assessments],
            'Creativity': [a.Creativity for a in assessments],
            'TimeManagement': [a.TimeManagement for a in assessments],
            'Optimism': [a.Optimism for a in assessments],
        }

    def analyze_improvement_areas(self, user_id):
        """Analyze areas needing improvement based on historical data"""
        assessments = self.session.query(EQAssessment)\
            .filter(EQAssessment.user_id == user_id)\
            .order_by(EQAssessment.timestamp)\
            .all()
        
        if not assessments:
            return None
        
        latest = assessments[-1]
        improvement_areas = []
        
        parameters = {
            "EyeContact": latest.EyeContact,
            "Behaviour": latest.Behaviour,
            "SocialRelationship": latest.SocialRelationship,
            "SpeechConveyance": latest.SpeechConveyance,
            "ConcentrationLevel": latest.ConcentrationLevel,
            "SelfRegulation": latest.SelfRegulation,
            "StressLevel": latest.StressLevel,
            "BodyMind": latest.BodyMind,
            "Empathy": latest.Empathy,
            "Motivation": latest.Motivation,
            "SelfAwareness": latest.SelfAwareness,
            "Mindfulness": latest.Mindfulness,
            "Creativity": latest.Creativity,
            "TimeManagement": latest.TimeManagement,
            "Optimism": latest.Optimism,
        }
        
        for param, score in parameters.items():
            if score <= 3:  # Threshold for low score
                historical_scores = [
                    getattr(a, param) 
                    for a in assessments
                ]
                improvement_areas.append({
                    'parameter': param,
                    'current_score': score,
                    'historical_avg': np.mean(historical_scores)
                })
        
        return improvement_areas

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
    pass

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
    pass

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
    pass

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/questions', methods=['POST'])
def questions():
    try:
        age = int(request.form['age'])
        user_id = request.form.get('user_id', str(random.randint(1000, 9999)))  # Generate random user_id if not provided
        session['age'] = age
        session['user_id'] = user_id
    except ValueError:
        return "Invalid age. Please enter a valid number."

    questions = get_questions_for_age_group(age)
    if questions is None:
        return "Invalid age group or no questions available."

    return render_template('questions.html', questions=questions, age=age)

def load_recommendations_file(age):
    if 1 <= age <= 12:
        file_name = "rec_under12.json"
    elif 13 <= age <= 17:
        file_name = "rec_12_17.json"
    elif age >= 18:
        file_name = "rec_above18.json"
    else:
        return None
    
    try:
        with open(file_name, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: {file_name} not found.")
        return None

# Function to generate recommendations
def generate_recommendations(age, score, parameter_scores):
    recommendations_data = load_recommendations_file(age)
    if not recommendations_data:
        return ["No recommendations available due to missing data."]


    # Determine score category
    if 1 <= age <= 12:
        if score < 50:
            score_category = "Emerging"
        elif 50 <= score <= 70:
            score_category = "Balanced"
        elif 70 < score <= 85:
            score_category = "Impressive"
        else:
            score_category = "Outstanding"
    elif 13 <= age <= 17:
        if score < 70:
            score_category = "Emerging"
        elif 70 <= score <= 80:
            score_category = "Balanced"
        elif 80 < score <= 90:
            score_category = "Impressive"
        else:
            score_category = "Outstanding"
    elif age >= 18:
        if score < 80:
            score_category = "Emerging"
        elif 80 <= score <= 90:
            score_category = "Balanced"
        elif 90 < score <= 100:
            score_category = "Impressive"
        else:
            score_category = "Outstanding"
    recommendations =[]
    if score_category in recommendations_data: 
        for parameter, param_score in parameter_scores.items(): 
            if param_score < 3 and parameter in recommendations_data[score_category]: 
                recommendations.append(random.choice(recommendations_data[score_category][parameter]))
    else: # Log missing key information for debugging 
        print(f"Missing key '{score_category}' in recommendations data.") 
        print(f"Available keys: {list(recommendations_data.keys())}") 
        recommendations.append("Practice mindfulness to enhance focus.") 
        
    return recommendations
def evaluate_eq(age, score):
    if 1 <= age <= 12:
        if score < 50:
            return "Emerging EQ"
        elif 50 <= score <= 70:
            return "Balanced EQ"
        elif 70 < score <= 85:
            return "Impressive EQ"
        else:
            return "Outstanding EQ"
    elif 13 <= age <= 17:
        if score < 60:
            return "Emerging EQ"
        elif 60 <= score <= 80:
            return "Balanced EQ"
        elif 80 < score <= 90:
            return "Impressive EQ"
        else:
            return "Outstanding EQ"
    elif age >= 18:
        if score < 70:
            return "Emerging EQ"
        elif 70 <= score <= 85:
            return "Balanced EQ"
        elif 90 < score <= 95:
            return "Impressive EQ"
        else:
            return "Outstanding EQ"
    return "Invalid age group."

# Route for EQ prediction
@app.route('/predict', methods=['POST'])
def predict():
    db_session = SessionLocal()
    analyzer = EQAnalyzer(db_session)
    
    try:
        user_id = session.get('user_id')
        age = session.get('age')
        
        if not age or not user_id:
            return "Session expired. Please start again."

        # Process form data into parameter scores
        parameter_scores = {}
        for key, value in request.form.items():
            try:
                parameter_scores[key] = int(value)
            except ValueError:
                parameter_scores[key] = 0

        # Load the appropriate model based on age
        model = load_model(age)
        if model is None:
            return "Prediction model not available."

        # Prepare input data for prediction
        input_values = [parameter_scores.get(param, 0) for param in model.feature_names_in_]
        input_df = pd.DataFrame([input_values], columns=model.feature_names_in_)

        # Predict the EQ score
        predicted_score = model.predict(input_df)[0]

        # Generate recommendations
        age_eval = evaluate_eq(age, predicted_score)
        general_recommendations = generate_recommendations(age, predicted_score, parameter_scores)

        # Save assessment to database
        analyzer.save_assessment(
            user_id=user_id,
            age=age,
            age_eval=age_eval,
            eq_score=predicted_score,
            parameter_scores=parameter_scores,
            recommendations=general_recommendations
        )

        # Get historical progress and improvement areas
        progress = analyzer.get_user_progress(user_id)
        improvement_areas = analyzer.analyze_improvement_areas(user_id)

        # Render results page
        return render_template(
            'result.html',
            score=predicted_score,
            age_eval=age_eval,
            age=age,
            recommendations=general_recommendations,
            progress=progress,
            improvement_areas=improvement_areas
        )

    finally:
        db_session.close()

if __name__ == '__main__':
    app.run(debug=True)