import pymysql
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm

# Step 1: Connect to SQL Database using the updated connection string
connection = pymysql.connect(
    host='localhost',      # Replace with your database host
    user='Thanya',         # Your username
    password='123Thanya',  # Your password
    database='eq_assessment_db'  # Your database name
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

# Step 4: Create Age Groups
# Split data into three age groups
below_12 = processed_data[processed_data['age'] < 12]
age_12_to_17 = processed_data[(processed_data['age'] >= 12) & (processed_data['age'] <= 17)]
age_18_plus = processed_data[processed_data['age'] >= 18]

# Function to plot Bell Curve for a given dataset
def plot_bell_curve(data, title):
    # Compute mean and standard deviation for EQ_Score
    mean_eq_score = data['eq_score'].mean()
    std_eq_score = data['eq_score'].std()

    # Create x-values for the curve
    x = np.linspace(data['eq_score'].min() - 10, 
                    data['eq_score'].max() + 10, 1000)
    y = norm.pdf(x, mean_eq_score, std_eq_score)

    # Plot Bell Curve
    plt.plot(x, y, color='blue', label=f'Normal Distribution (μ={mean_eq_score:.2f}, σ={std_eq_score:.2f})')

    # Overlay histogram of EQ Scores
    plt.hist(data['eq_score'], bins=15, density=True, alpha=0.6, color='orange', label='EQ Score Distribution')

    # Customizations
    plt.title(title)
    plt.xlabel('EQ Score')
    plt.ylabel('Density')
    plt.legend()
    plt.grid(True)

# Step 5: Plot for each age group
plt.figure(figsize=(18, 6))

# Below 12 years old
plt.subplot(1, 3, 1)
plot_bell_curve(below_12, 'EQ Score Distribution - Age < 12')

# Age 12 to 17 years
plt.subplot(1, 3, 2)
plot_bell_curve(age_12_to_17, 'EQ Score Distribution - Age 12-17')

# Age 18+ years
plt.subplot(1, 3, 3)
plot_bell_curve(age_18_plus, 'EQ Score Distribution - Age 18+')

# Show all the plots
plt.tight_layout()
plt.show()
