import pymysql
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor

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
FROM eq_assessments
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

# Step 4: Correlation Analysis
correlation_matrix = processed_data.corr()

# Plot Correlation Heatmap for EQ Score
plt.figure(figsize=(12, 8))
sns.heatmap(correlation_matrix[['eq_score']], annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5)
plt.title('Correlation of Parameters with EQ Score')
plt.show()

# Step 5: Multiple Linear Regression
X = processed_data[['EyeContact', 'Behaviour', 'SocialRelationship', 'SpeechConveyance', 
                    'ConcentrationLevel', 'SelfRegulation', 'StressLevel', 'BodyMind', 
                    'Empathy', 'Motivation', 'SelfAwareness', 'Mindfulness', 'Creativity', 
                    'TimeManagement', 'Optimism']]
y = processed_data['eq_score']

# Train the Linear Regression model
linear_model = LinearRegression()
linear_model.fit(X, y)

# Get the coefficients and visualize them
coefficients = linear_model.coef_
coeff_df = pd.DataFrame(list(zip(X.columns, coefficients)), columns=['Parameter', 'Coefficient'])
coeff_df = coeff_df.sort_values(by='Coefficient', ascending=False)

# Plot the coefficients
plt.figure(figsize=(10, 6))
sns.barplot(x='Coefficient', y='Parameter', data=coeff_df)
plt.title('Effect of Each Parameter on EQ Score (Linear Regression)')
plt.xlabel('Coefficient (Impact on EQ score)')
plt.ylabel('Parameter')
plt.show()

# Step 6: Random Forest Regressor for Feature Importance
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(X, y)

# Get feature importances
feature_importance = rf_model.feature_importances_

# Create a DataFrame for feature importance
feature_importance_df = pd.DataFrame(list(zip(X.columns, feature_importance)), columns=['Parameter', 'Importance'])
feature_importance_df = feature_importance_df.sort_values(by='Importance', ascending=False)

# Plot the feature importance
plt.figure(figsize=(10, 6))
sns.barplot(x='Importance', y='Parameter', data=feature_importance_df)
plt.title('Feature Importance for Predicting EQ Score (Random Forest)')
plt.xlabel('Importance')
plt.ylabel('Parameter')
plt.show()

# Step 7: Visualizing Relationship of Each Parameter with EQ Score (Scatter Plots)
parameters = ['EyeContact', 'Behaviour', 'SocialRelationship', 'SpeechConveyance', 
              'ConcentrationLevel', 'SelfRegulation', 'StressLevel', 'BodyMind', 
              'Empathy', 'Motivation', 'SelfAwareness', 'Mindfulness', 'Creativity', 
              'TimeManagement', 'Optimism']

plt.figure(figsize=(15, 10))

for i, param in enumerate(parameters, 1):
    plt.subplot(5, 3, i)  # Arrange 5 rows and 3 columns
    plt.scatter(processed_data[param], processed_data['eq_score'], alpha=0.5)
    plt.title(f'{param} vs EQ Score')
    plt.xlabel(param)
    plt.ylabel('EQ Score')

plt.tight_layout()
plt.show()

# Step 8: Create Bell Curve for EQ Scores (with Age Groups)
# Create subsets for age groups: below 12, 12-17, and 18+
age_groups = ['Below 12', '12-17', '18+']
age_group_data = {
    'Below 12': processed_data[processed_data['age'] < 12],
    '12-17': processed_data[(processed_data['age'] >= 12) & (processed_data['age'] <= 17)],
    '18+': processed_data[processed_data['age'] > 17]
}

# Plot the bell curve for each age group
plt.figure(figsize=(12, 6))

for age_group, group_data in age_group_data.items():
    # Compute mean and standard deviation for EQ_Score for each age group
    mean_eq_score = group_data['eq_score'].mean()
    std_eq_score = group_data['eq_score'].std()

    # Create x-values for the curve
    x = np.linspace(group_data['eq_score'].min() - 10, group_data['eq_score'].max() + 10, 1000)
    y = norm.pdf(x, mean_eq_score, std_eq_score)

    # Plot the bell curve for the age group
    plt.plot(x, y, label=f'{age_group} (μ={mean_eq_score:.2f}, σ={std_eq_score:.2f})')

    # Overlay histogram of EQ Scores
    plt.hist(group_data['eq_score'], bins=15, density=True, alpha=0.6, label=f'{age_group} EQ Score Distribution')

plt.title('Bell Curve for EQ Scores by Age Group')
plt.xlabel('EQ Score')
plt.ylabel('Density')
plt.legend()
plt.grid(True)
plt.show()
