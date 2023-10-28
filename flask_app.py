from flask import Flask, request, jsonify
from database import get_milestone_data, insert_milestone_data, update_milestone_data
from flask_cors import CORS
import pickle
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import pymongo
from datetime import datetime


app = Flask(__name__)
CORS(app)



@app.route('/get_milestone', methods=['GET'])
def get_milestone():
    age = request.args.get('age')
    milestone_data = get_milestone_data(age)
    
    # Convert ObjectId to string for JSON serialization
    if milestone_data and '_id' in milestone_data:
        milestone_data['_id'] = str(milestone_data['_id'])
        
    return jsonify(milestone_data)


@app.route('/insert_milestone', methods=['POST'])
def insert_milestone():
    data = request.json
    insert_milestone_data(data['age'], data['emotional'], data['language'], data['cognitive'], data['physical'])
    return jsonify({'message': 'Milestone data added successfully'})

@app.route('/update_milestone', methods=['PUT'])
def update_milestone():
    data = request.json
    age = data['age']
    update_milestone_data(age, data['emotional'], data['language'], data['cognitive'], data['physical'])
    return jsonify({'message': 'Milestone data updated successfully'})



# Load the trained model using pickle
with open('child_growth_classifier.pkl', 'rb') as model_file:
    loaded_model = pickle.load(model_file)

# Create label encoders for categorical variables
label_encoders = {}  # Initialize an empty dictionary to store label encoders


# MongoDB connection details
client = pymongo.MongoClient("mongodb+srv://it20405090:j030Ndw8@predictions.nvnsowv.mongodb.net/?retryWrites=true&w=majority")
db = client["growth_prediction"]
collection = db["new_predictions"]



# Define the categorical columns
categorical_cols = [
    'gross_motor', 'fine_motor', 'communication', 'problem_solving', 'emotional_dev', 'attention',
    'overactivity', 'passivity', 'planning', 'perception', 'perception_vf', 'memory', 'spoken',
    'reading', 'social_skills', 'emotional_prob'
]

# Add label encoders for each categorical variable
for col in categorical_cols:
    label_encoders[col] = LabelEncoder()

# Define the feature names in the same order as during training
feature_names = [
    'age', 'height', 'weight', 'gross_motor', 'fine_motor', 'communication', 'problem_solving',
    'emotional_dev', 'attention', 'overactivity', 'passivity', 'planning', 'perception',
    'perception_vf', 'memory', 'spoken', 'reading', 'social_skills', 'emotional_prob'
]

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json  # User input in JSON format
    try:
        # Create a DataFrame from user input
        user_data = pd.DataFrame(data)

        # Convert all columns to Python integers
        user_data = user_data.applymap(int)

        # Reorganize columns to match the feature names order
        user_data = user_data[feature_names]

        # Reset the index of user_data
        user_data.reset_index(drop=True, inplace=True)

        # Reshape user_data to a two-dimensional array
        user_data = user_data.values.reshape(1, -1)

        # Make a prediction
        user_prediction = loaded_model.predict(user_data)

        # Convert NumPy int64 to Python int
        prediction = int(user_prediction[0])

        # Include the current date
        current_date = datetime.now().strftime('%Y-%m-%d')

        # Create a dictionary with user data and prediction
        prediction_data = {
            'user_data': data,
            'prediction': prediction,
            'date': current_date
        }

        # Save the prediction to MongoDB
        collection.insert_one(prediction_data)

        # Return the prediction as JSON
        return jsonify({'prediction': prediction})

    except Exception as e:
        return jsonify({'error': str(e)})
    

@app.route('/predictions', methods=['GET'])
def get_predictions():
    # Retrieve all predictions from the database
    predictions = list(collection.find({}, {'_id': 0}))

    return jsonify({'predictions': predictions})



if __name__ == '__main__':
    app.run(debug=True)
