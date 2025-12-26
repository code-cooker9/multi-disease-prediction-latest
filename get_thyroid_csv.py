import pandas as pd
import os

# Make sure 'data/' folder exists
os.makedirs("data", exist_ok=True)

# Dictionary of datasets with their source URL or local path, and key columns
datasets = {
    "diabetes": {
        "url": "D:\Sanguine\Downloads\multi-disease-prediction2\multi-disease-prediction-main\l_models\diabetes.csv",
        "columns": ['Pregnancies', 'Glucose', 'BloodPressure','BMI', 'Age', 'Outcome']
    },
    "heart": {
        "url": "D:\Sanguine\Downloads\multi-disease-prediction2\multi-disease-prediction-main\l_models\heart.csv",
        "columns": ['age', 'sex', 'cp', 'trestbps', 'chol', 'thalach', 'exang', 'target']
    },
    "liver": {
        "url": "D:\Sanguine\Downloads\multi-disease-prediction2\multi-disease-prediction-main\l_models\indian_liver_patient.csv",
        "columns": ['Age', 'Gender', 'Total_Bilirubin', 'Direct_Bilirubin', 'Alkaline_Phosphotase', 'Alamine_Aminotransferase', 'Aspartate_Aminotransferase', 'Dataset']
    },
    "kidney": {
        "url": "D:\Sanguine\Downloads\multi-disease-prediction2\multi-disease-prediction-main\l_models\kidney_disease.csv",
        "columns": ['sg','al','rbc','pc','hemo','wc','rc','bp','classification']
    },
    
}

for name, info in datasets.items():
    try:
        print(f"Processing {name} dataset...")
        df = pd.read_csv(info['url'])
        simple_df = df[info['columns']]
        csv_path = f"data/{name}_simple.csv"
        simple_df.to_csv(csv_path, index=False)
        print(f"Simplified {name} dataset saved to: {csv_path}")
    except Exception as e:
        print(f"[Error] Failed to process {name}: {e}")
