import pymysql
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm

# Step 1: Connect to SQL Database
connection = pymysql.connect(
    host='localhost',      # Replace with your database host
    user='Thanya',           # Replace with your username
    password='123Thanya',   # Replace with your password
    database='eq_assessment_db'    # Replace with your database name
)

# Step 2: Fetch Data from SQL
query = """
SELECT age, eq_score, EyeContact, Behaviour, SocialRelationship, SpeechConveyance, 
       ConcentrationLevel, SelfRegulation, StressLevel, BodyMind, Empathy, 
       Motivation, SelfAwareness, Mindfulness, Creativity, TimeManagement, Optimism
FROM  eq_assessments
"""
data = pd.read_sql(query, connection)
connection.close()

# Step 3: Process Data
# Select relevant columns (age, eq_score, and parameters)
columns_to_consider = ['age', 'eq_score', 'EyeContact', 'Behaviour', 'SocialRelationship',
                       'SpeechConveyance', 'ConcentrationLevel', 'SelfRegulation',
                       'StressLevel', 'BodyMind', 'Empathy', 'Motivation', 
                       'SelfAwareness', 'Mindfulness', 'Creativity', 
                       'TimeManagement', 'Optimism']
processed_data = data[columns_to_consider]

# Step 4: Calculate Bell Curve
# Compute mean and standard deviation for EQ_Score
mean_eq_score = processed_data['eq_score'].mean()
std_eq_score = processed_data['eq_score'].std()

# Create x-values for the curve
x = np.linspace(processed_data['eq_score'].min() - 10, 
                processed_data['eq_score'].max() + 10, 1000)
y = norm.pdf(x, mean_eq_score, std_eq_score)

# Step 5: Plot Bell Curve
plt.figure(figsize=(12, 6))

# Plot bell curve
plt.plot(x, y, color='blue', label=f'Normal Distribution (μ={mean_eq_score:.2f}, σ={std_eq_score:.2f})')

# Overlay histogram of EQ Scores
plt.hist(processed_data['eq_score'], bins=15, density=True, alpha=0.6, color='orange', label='EQ Score Distribution')

# Customizations
plt.title('Bell Curve for EQ Scores (Parameters and Age Considered)')
plt.xlabel('EQ Score')
plt.ylabel('Density')
plt.legend()
plt.grid(True)

# Show plot
plt.show()
