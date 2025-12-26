from datetime import datetime
import pandas as pd
import numpy as np
import pickle
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, roc_auc_score, f1_score

# --- Define Features for all 7 Diseases ---
MODEL_FEATURES = {

    'diabetes': [
        'Pregnancies',
        'Glucose',
        'BloodPressure',
        'BMI',
        'Age'
    ],

    'kidney': [
        'sg',
        'al',
        'rbc',
        'pc',
        'hemo',
        'wc',
        'rc',
        'bp'
    ],

    'heart': [
        'age',
        'sex',
        'cp',
        'trestbps',
        'chol',
        'thalach',
        'exang'
    ],

    'liver': [
        'Age',
        'Gender',
        'Total_Bilirubin',
        'Direct_Bilirubin',
        'Alkaline_Phosphotase',
        'Alamine_Aminotransferase',
        'Aspartate_Aminotransferase'
    ],

    'malaria': [
        'Temperature',
        'Headache',
        'Vomiting',
        'Joint_Pain',
        'rbc_count'
    ],

    'thyroid': [
        'Age',
        'Sex',
        'TSH',
        'T3',
        'T4',
        'Thyroxine'
    ],

    'pneumonia': [
        'Age',
        'Cough_Severity',
        'WBC_Count',
        'Oxygen_Saturation',
        'Fever'
    ]
}


def create_and_save_reliable_model(disease_name, features):
    """
    Creates ML models.
    - Uses REAL CSV for kidney
    - Uses simulated data for others
    """

    print(f"Creating model for {disease_name}...")

    # ============================================================
    # ✅ STEP 3 FIX — REAL KIDNEY CSV TRAINING
    # ============================================================
    if disease_name == "kidney":
        csv_path = "data/kidney_simple.csv"

        if not os.path.exists(csv_path):
            raise FileNotFoundError("kidney_simple.csv not found in data/ folder")

        df = pd.read_csv(csv_path)
        X = df[features]
        y = df["classification"]

    # ============================================================
    # SIMULATED DATA FOR OTHER DISEASES (UNCHANGED LOGIC)
    # ============================================================
    else:
        n_samples = 1000
        np.random.seed(42 + hash(disease_name) % 100)

        data = {}
        for feature in features:
            if 'Age' in feature or 'age' in feature:
                data[feature] = np.random.randint(20, 70, n_samples)
            elif 'Glucose' in feature:
                data[feature] = np.random.randint(70, 200, n_samples)
            elif 'BMI' in feature:
                data[feature] = np.random.uniform(18.5, 40, n_samples)
            elif 'TSH' in feature:
                data[feature] = np.random.uniform(0.5, 15.0, n_samples)
            else:
                data[feature] = np.random.rand(n_samples) * 100

        df = pd.DataFrame(data)

        target_score = 0.0

        if disease_name == 'diabetes' and 'Glucose' in features:
            target_score = (df['Glucose'] / 200) * 0.4 + (df.get('BMI', 0) / 40) * 0.3

        elif disease_name == 'heart' and 'chol' in features:
            target_score = (df['chol'] / 300) * 0.4 + (df.get('age', 0) / 100) * 0.3

        elif disease_name == 'liver' and 'Total_Bilirubin' in features:
            target_score = (df['Total_Bilirubin'] / df['Total_Bilirubin'].max()) * 0.6

        elif disease_name == 'thyroid' and 'TSH' in features:
            target_score = (df['TSH'] / df['TSH'].max()) * 0.5

        else:
            feat1 = features[0]
            feat2 = features[1]
            target_score = (df[feat1] / df[feat1].max()) * 0.3 + (df[feat2] / df[feat2].max()) * 0.3

        target_prob = np.clip(target_score + np.random.normal(0, 0.15, n_samples), 0, 1)
        df['Outcome'] = (target_prob > 0.5).astype(int)

        if df['Outcome'].nunique() < 2:
            df.loc[df.index[:10], 'Outcome'] = 1
            df.loc[df.index[-10:], 'Outcome'] = 0

        X = df[features]
        y = df['Outcome']

    # ============================================================
    # PREPROCESSING
    # ============================================================
    imputer = SimpleImputer(strategy='mean')
    X_imputed = imputer.fit_transform(X)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_imputed)

    # ============================================================
    # MODEL TRAINING
    # ============================================================
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        random_state=42,
        class_weight='balanced'
    )
    model.fit(X_scaled, y)

    # ============================================================
    # SAFE EVALUATION
    # ============================================================
    y_pred = model.predict(X_scaled)
    y_prob = model.predict_proba(X_scaled)[:, 1]

    accuracy = accuracy_score(y, y_pred)
    f1 = f1_score(y, y_pred)
    auc = roc_auc_score(y, y_prob)

    print(f"  > Metrics: Acc={accuracy:.3f}, F1={f1:.3f}, AUC={auc:.3f}")

    # ============================================================
    # SAVE MODEL FILES
    # ============================================================
    model_dir = "models"
    os.makedirs(model_dir, exist_ok=True)

    with open(os.path.join(model_dir, f"{disease_name}_model.pkl"), "wb") as f:
        pickle.dump(model, f)

    with open(os.path.join(model_dir, f"{disease_name}_scaler.pkl"), "wb") as f:
        pickle.dump(scaler, f)

    with open(os.path.join(model_dir, f"{disease_name}_imputer.pkl"), "wb") as f:
        pickle.dump(imputer, f)

    print(f"Successfully created and saved components for {disease_name}.")


if __name__ == "__main__":

    for disease, features in MODEL_FEATURES.items():
        create_and_save_reliable_model(disease, features)

    with open("models/model_features.pkl", "wb") as f:
        pickle.dump(MODEL_FEATURES, f)

    print("\n✅ ML Pipeline execution complete. All models ready.")
