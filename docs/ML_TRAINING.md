ML & Rule-Based Prediction System – Clear Explanation (Points Only)
1. Project Structure Overview:
    This project predicts multiple diseases using two approaches:
    Machine Learning (CSV-based models)
    Rule-based logic (medical threshold rules)
    Each disease uses only one approach, not mixed.

2. Diseases Using Machine Learning (CSV-based)

    The following 4 diseases use CSV data and ML models:
        Diabetes
        Heart Disease
        Kidney Disease
        Liver Disease

    For these diseases:
        Data is read from CSV files
        Models are trained using that data
        Predictions depend on learned patterns, not hard rules

3. Diseases Using Rule-Based Logic

    The following 3 diseases use pure rule-based logic:
        Malaria
        Thyroid
        Pneumonia

    For these diseases:
        No CSV file is used
        No ML model is used
        Decisions are made using fixed numeric medical ranges

4. Machine Learning Algorithm Used

    Algorithm: Random Forest Classifier
    Library: scikit-learn
    Purpose:
        Classify patient data into:
            Normal 
            Risky

5. CSV-Based Training Data

    Each CSV file contains:
        Input parameters (features)
        One target column (Outcome, target, classification, or Dataset)

    Example:
        Heart → target
        Kidney → classification
        Liver → Dataset

6. Feature Selection

    Input parameters for each disease are fixed
        Feature lists are defined in:
        ml_pipeline.py → MODEL_FEATURES

    The same feature order is used:
            During training
            During prediction

7. Data Preprocessing (CSV-based Diseases)

    Before training:
        Missing values are replaced using mean
        Data is scaled using StandardScaler
        These steps are saved and reused during prediction

8. Model Training Logic

    For each ML disease:
        CSV is read
        Features are extracted
        Target column is separated
        Preprocessing is applied
        Random Forest is trained
        Model + scaler + imputer are saved as .pkl files

    Saved files:
    <disease>_model.pkl
    <disease>_scaler.pkl
    <disease>_imputer.pkl

9. How Prediction Works (ML Diseases)

    User inputs values from the web form
    Inputs are converted to numbers
    Values are arranged exactly like CSV columns
    Saved imputer and scaler are applied
    Model predicts:
        0 → Normal
        1 → Risky

10. Why Some Risky Inputs Show “Normal” (ML Diseases)

    ML learns patterns from CSV data
    If CSV data contains:
        Weak separation
        Overlapping values
    Then:
        Some clinically risky values may still appear Normal
        This is model behavior, not a coding error.

11. Rule-Based Disease Logic

    For Malaria, Thyroid, and Pneumonia:
        Inputs are checked using if-else conditions
        Only numeric values are accepted
        Any value outside safe medical range → Risky

    Example logic:
        High fever + symptoms → Risky
        Hormone values outside range → Risky

12. No CSV Used for Rule-Based Diseases

    Rule-based diseases:

        Do not load CSV files
        Do not use ML models
        Do not depend on training data
        Output is 100% deterministic

13. Why Rule-Based Outputs Are Stable

    Same input → same output
    No randomness
    No learning
    Easy to explain during presentation

14. Why ML Outputs Can Feel Inconsistent

     ML models depend on:

        Data quality
        Data distribution
        Feature correlation
        Predictions are probabilistic, not absolute

15. Current System Status

    App is functioning correctly
    CSV loading is correct
    Rule-based logic is correct
    Models are predicting as trained


