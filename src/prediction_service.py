# src/prediction_service.py

import os
import pickle
import numpy as np

# Rule-based imports
from rule_based.thyroid_rules import predict_thyroid
from rule_based.pneumonia_rules import predict_pneumonia
from rule_based.malaria_rules import predict_malaria

# Models folder
MODEL_DIR = os.path.join(os.path.dirname(__file__), "../models")

# ---------------------------
# Model-based prediction (4 diseases)
# ---------------------------
def load_model_files(disease):
    try:
        model_path = os.path.join(MODEL_DIR, f"{disease}_model.pkl")
        scaler_path = os.path.join(MODEL_DIR, f"{disease}_scaler.pkl")
        imputer_path = os.path.join(MODEL_DIR, f"{disease}_imputer.pkl")

        if not all(os.path.exists(p) for p in [model_path, scaler_path, imputer_path]):
            raise FileNotFoundError(f"Model files missing for {disease}")

        with open(model_path, "rb") as f:
            model = pickle.load(f)
        with open(scaler_path, "rb") as f:
            scaler = pickle.load(f)
        with open(imputer_path, "rb") as f:
            imputer = pickle.load(f)

        return model, scaler, imputer
    except Exception as e:
        print(f"[Error] Failed to load model files for {disease}: {e}")
        return None, None, None


def predict_model(disease, input_features):
    """
    disease: str -> 'diabetes', 'heart', 'liver', 'kidney'
    input_features: list or np.array of input values
    """
    model, scaler, imputer = load_model_files(disease)
    if not model:
        return None

    try:
        # Convert to 2D array
        arr = np.array(input_features).reshape(1, -1)
        # Impute missing values
        arr = imputer.transform(arr)
        # Scale features
        arr = scaler.transform(arr)
        # Predict
        pred = model.predict(arr)
        return pred[0]
    except Exception as e:
        print(f"[Error] Prediction failed for {disease}: {e}")
        return None


# ---------------------------
# Rule-based prediction (3 diseases)
# ---------------------------
def predict_rule_based(disease, input_dict):
    """
    disease: str -> 'thyroid', 'pneumonia', 'malaria'
    input_dict: dictionary of features
    """
    try:
        if disease == "thyroid":
            return predict_thyroid(input_dict)
        elif disease == "pneumonia":
            return predict_pneumonia(input_dict)
        elif disease == "malaria":
            return predict_malaria(input_dict)
        else:
            raise ValueError("Unknown rule-based disease")
    except Exception as e:
        print(f"[Error] Rule-based prediction failed for {disease}: {e}")
        return None


# ---------------------------
# Main interface
# ---------------------------
def predict(disease, input_data):
    """
    Unified prediction interface
    disease: str -> one of 7 diseases
    input_data: list (for model-based) or dict (for rule-based)
    """
    if disease in ["diabetes", "heart", "liver", "kidney"]:
        return predict_model(disease, input_data)
    elif disease in ["thyroid", "pneumonia", "malaria"]:
        return predict_rule_based(disease, input_data)
    else:
        raise ValueError("Unknown disease")


# Example usage
if __name__ == "__main__":
    # Model-based example
    diabetes_features = [5, 166, 72, 19, 0, 0, 0, 0]  # example values
    print("Diabetes prediction:", predict("diabetes", diabetes_features))

    # Rule-based example
    thyroid_features = {'TSH': 5.0, 'T3': 0.8, 'on_thyroxine': 0, 'age': 45, 'sex': 'M'}
    print("Thyroid prediction:", predict("thyroid", thyroid_features))
