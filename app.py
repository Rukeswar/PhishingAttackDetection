from flask import Flask, render_template, request, jsonify
import pandas as pd
import joblib
from feature_extraction import extract_features  # Import the feature extraction function

app = Flask(__name__)

# Load the pre-trained model
try:
    model = joblib.load('model.pkl')

except Exception as e:
    print(f"Error loading model: {e}")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    try:
        url_input = request.form['url']
        print(f"Received URL: {url_input}")  # Debugging line

        if not url_input:
            return render_template('index.html', prediction_text='Error: URL is required.')

        # Feature extraction and prediction
        features = extract_features(url_input)
        print(f"Extracted Features: {features}")  # Debugging line
        features_df = pd.DataFrame([features])

        # Predict using the model
        y_pred = model.predict(features_df)
        print(f"Model Prediction: {y_pred[0]}")  # Debugging line

        # Result determination based on prediction
        if y_pred[0] == 0:
            result = 'The URL is legitimate.'
        else:
            result = 'The URL is phishing.'

        return render_template('index.html', prediction_text=result)

    except Exception as e:
        print(f"Error occurred: {e}")  # Debugging line
        return render_template('index.html', prediction_text=f'Error: {e}')

    
if __name__ == "__main__":
    app.run(debug=True)

