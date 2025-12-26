from pydoc import html
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import pickle
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from ml_pipeline import MODEL_FEATURES  # features per disease

try:
    import bcrypt
    _HAS_BCRYPT = True
except Exception:
    bcrypt = None
    _HAS_BCRYPT = False

# --------------------------------------------------
# App setup
# --------------------------------------------------
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "dev_secret_key")
DATABASE = "database.db"

# --------------------------------------------------
# Database helper
# --------------------------------------------------
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# --------------------------------------------------
# Context processor for datetime
# --------------------------------------------------
@app.context_processor
def inject_now():
    return {"now": datetime.now()}

# --------------------------------------------------
# Load ML models
# --------------------------------------------------
ML_DISEASES = ["diabetes", "kidney", "heart", "liver"]
MODEL_COMPONENTS = {}
for disease in ML_DISEASES:
    try:
        MODEL_COMPONENTS[disease] = {
            "model": pickle.load(open(f"models/{disease}_model.pkl", "rb")),
            "scaler": pickle.load(open(f"models/{disease}_scaler.pkl", "rb")),
            "imputer": pickle.load(open(f"models/{disease}_imputer.pkl", "rb"))
        }
    except Exception:
        pass

# --------------------------------------------------
# RULE-BASED LOGIC
# --------------------------------------------------
def thyroid_rule(inputs):
    """
    Numerical-only Thyroid Risk Assessment

    Inputs (all numbers):
    - Age (years)
    - Sex (0 = Male, 1 = Female)
    - TSH (0.5 - 4.5 is normal)
    - T3 (0.8 - 2.0 is normal)
    - TT4 (4.5 - 12.0 is normal)
    - On_Thyroxine (0 = No, 1 = Yes)

    Returns:
    - "Normal" or "Risky"
    """
    try:
        age = float(inputs.get('Age', 0))
        sex = int(inputs.get('Sex', -1))              # 0 or 1
        tsh = float(inputs.get('TSH', 0))
        t3 = float(inputs.get('T3', 0))
        t4 = float(inputs.get('T4', 0))
        thyroxine = int(inputs.get('Thyroxine', 0))
    except:
        return "Risky"

    # Check age
    if age <= 0 or age > 120:
        return "Risky"

    # Check sex
    if sex not in [0, 1]:
        return "Risky"

    # On Thyroxine abnormal
    if thyroxine not in [0, 1]:
        return "Risky"

    # Lab ranges
    if 0.5 <= tsh <= 4.5 and 0.8 <= t3 <= 2.0 and 4.5 <= t4 <= 12.0:
        return "Normal"
    else:
        return "Risky"



def malaria_rule(inputs):
    """
    Numerical-only Malaria Risk Assessment

    Inputs (all numbers):
    - Temperature (°F)
    - Headache (1 = yes, 0 = no)
    - Vomiting (1 = yes, 0 = no)
    - Joint Pain (1 = yes, 0 = no)
    - RBC count (million/µL)

    Returns:
    - "Normal" or "Risky"
    """
    try:
        temp = float(inputs.get('Temperature', 0))
        headache = int(inputs.get('Headache', 0))
        vomiting = int(inputs.get('Vomiting', 0))
        joint_pain = int(inputs.get('Joint_Pain', 0))
        rbc = float(inputs.get('rbc_count', 0))
    except:
        return "Risky"

    # Check numerical ranges
    if temp <= 0 or temp > 115:   # realistic human range
        return "Risky"
    if headache not in [0, 1] or vomiting not in [0, 1] or joint_pain not in [0, 1]:
        return "Risky"
    if rbc <= 0 or rbc > 1e6:      # realistic RBC count
        return "Risky"

    # Rule: Fever > 100°F with any symptom => Risky
    if temp > 100 and (headache or vomiting or joint_pain):
        return "Risky"

    # Moderate fever with symptoms can also be risky
    if temp > 99 and (headache or vomiting or joint_pain):
        return "Risky"

    # Otherwise normal
    return "Normal"

def pneumonia_rule(inputs):
    """
    Pneumonia Risk Assessment:
    Returns 'Normal' or 'Risky' based on multiple clinical parameters.
    """

    # Convert inputs safely
    age = float(inputs.get('Age', 0))
    cough = int(inputs.get('Cough', 0))           # severity 0-3
    fever = float(inputs.get('Fever', 0))         # °C
    wbc = float(inputs.get('WBC', 0))             # cells per µL
    oxygen = float(inputs.get('Oxygen_Saturation', 0))  # %

    risk_factors = 0

    # Age risk
    if age > 60:
        risk_factors += 1

    # Cough severity
    if cough >= 2:
        risk_factors += 1

    # Fever
    if fever > 38:
        risk_factors += 1

    # WBC count (leukocytosis)
    if wbc > 11000:
        risk_factors += 1

    # Oxygen saturation
    if oxygen < 92:
        risk_factors += 1

    # If any risk factor exists, mark as Risky
    if risk_factors > 0:
        return "Risky"

    return "Normal"

def heart_rule(inputs):
    """
    Heart Disease Risk Assessment
    
    Inputs:
    - age (years)
    - sex (0 = Male, 1 = Female)
    - cp (chest pain type: 0-3)
    - trestbps (resting blood pressure)
    - chol (cholesterol)
    - thalach (max heart rate achieved)
    - exang (exercise induced angina: 0 = No, 1 = Yes)
    
    Returns: "Normal" or "Risky"
    """
    try:
        age = float(inputs.get('age', 0))
        sex = int(inputs.get('sex', -1))
        cp = int(inputs.get('cp', -1))
        trestbps = float(inputs.get('trestbps', 0))
        chol = float(inputs.get('chol', 0))
        thalach = float(inputs.get('thalach', 0))
        exang = int(inputs.get('exang', -1))
    except:
        return "Risky"
    
    risk_factors = 0
    
    # Age risk (higher risk for older patients)
    if age > 55:
        risk_factors += 1
    
    # High cholesterol
    if chol > 240:
        risk_factors += 1
    elif chol > 200:
        risk_factors += 0.5
    
    # High blood pressure
    if trestbps > 140:
        risk_factors += 1
    elif trestbps > 130:
        risk_factors += 0.5
    
    # Low max heart rate (indicates poor cardiac fitness)
    if thalach < 100:
        risk_factors += 1
    
    # Exercise induced angina (chest pain with exercise)
    if exang == 1:
        risk_factors += 2
    
    # Chest pain type (type 0 is typical angina, higher risk)
    if cp == 0 or cp == 1:
        risk_factors += 1
    
    # Risk assessment
    if risk_factors >= 3:
        return "Risky"
    else:
        return "Normal"

def kidney_rule(inputs):
    try:
        sg = float(inputs.get('sg', 0))
        al = float(inputs.get('al', 0))
        rbc = float(inputs.get('rbc', 0))
        pc = float(inputs.get('pc', 0))
        hemo = float(inputs.get('hemo', 0))
        wc = float(inputs.get('wc', 0))
        rc = float(inputs.get('rc', 0))
        bp = float(inputs.get('bp', 0))
    except:
        return "Risky"

    if sg < 1.005 or sg > 1.030:
        return "Risky"
    if al > 2:
        return "Risky"
    if rbc < 3.5 or rbc > 5.5:
        return "Risky"
    if pc < 150 or pc > 450:
        return "Risky"
    if hemo < 13.5 or hemo > 17.5:
        return "Risky"
    if wc < 4000 or wc > 11000:
        return "Risky"
    if rc < 4.2 or rc > 5.4:
        return "Risky"
    if bp < 90 or bp > 140:
        return "Risky"
    return "Normal"
def liver_rule(inputs):
    """
    Liver Risk Assessment (Rule-Based)

    Accepts keys:
    - 'Age'
    - 'Total Bilirubin'
    - 'Direct Bilirubin'
    - 'Alkaline Phosphotase'
    - 'Alamine Aminotransferase'
    - 'Aspartate Aminotransferase'
    - 'Total Proteins' (optional)
    - 'Albumin' (optional)

    Returns "Normal" or "Risky"
    """
    try:
        age = float(str(inputs.get('Age', 0)).strip())
        tb = float(str(inputs.get('Total_Bilirubin', 0)).strip())
        db = float(str(inputs.get('Direct_Bilirubin', 0)).strip())
        alkphos = float(str(inputs.get('Alkaline_Phosphotase', 0)).strip())
        sgpt = float(str(inputs.get('Alamine_Aminotransferase', 0)).strip())
        sgot = float(str(inputs.get('Aspartate_Aminotransferase', 0)).strip())
         # default normal
    except Exception:
        return "Risky"

    # Age check
    if age <= 0 or age > 120:
        return "Risky"

    # Liver lab ranges (realistic)
    if not (0.3 <= tb <= 1.2):
        return "Risky"
    if not (0.1 <= db <= 0.5):
        return "Risky"
    if not (30 <= alkphos <= 120):
        return "Risky"
    if not (7 <= sgpt <= 56):
        return "Risky"
    if not (10 <= sgot <= 40):
        return "Risky"

    return "Normal"



RULE_BASED = {
    'thyroid': thyroid_rule,
    'malaria': malaria_rule,
    'pneumonia': pneumonia_rule,
    'kidney': kidney_rule,
    'liver': liver_rule,
    'heart': heart_rule
}
RECOMMENDATIONS = {
    'diabetes': {
        'Normal': "Keep a balanced diet and exercise regularly to maintain healthy blood sugar levels.",
        'Risky': "Consult a doctor for blood sugar management, maintain a healthy diet, and monitor glucose levels."
    },
    'heart': {
        'Normal': "Maintain cardiovascular health through exercise, low salt intake, and regular checkups.",
        'Risky': "Seek immediate medical consultation. Monitor blood pressure, cholesterol, and heart health."
    },
    'kidney': {
        'Normal': "Stay hydrated, avoid excessive salt, and maintain kidney-friendly habits.",
        'Risky': "Consult a nephrologist. Monitor kidney function and avoid high-risk foods or medications."
    },
    'liver': {
        'Normal': "Maintain a healthy lifestyle, avoid excess alcohol, and eat a balanced diet.",
        'Risky': "Consult a hepatologist. Avoid alcohol, fatty foods, and get liver function tests regularly."
    },
    'malaria': {
        'Normal': "Use mosquito protection and maintain hygiene to prevent infection.",
        'Risky': "Seek immediate medical attention. Take prescribed antimalarial medications."
    },
    'thyroid': {
        'Normal': "Maintain a balanced diet with adequate iodine. Routine checkups are recommended.",
        'Risky': "Consult an endocrinologist. Follow prescribed medications and monitor hormone levels."
    },
    'pneumonia': {
        'Normal': "Practice good hygiene and maintain a healthy immune system.",
        'Risky': "Seek medical attention. Rest, hydrate, and follow doctor's instructions."
    }
}
SUGGESTIONS = {

    'diabetes': {
        'Normal': {
            'clinical': [
                "Maintain healthy body weight.",
                "Monitor blood glucose periodically.",
                "Balanced diet and regular exercise.",
                "Limit refined sugars and processed foods."
            ],
            'herbal': [
                "Fenugreek seeds may support glucose balance.",
                "Cinnamon may improve insulin sensitivity.",
                "Bitter gourd juice is traditionally used.",
                "Daily walking or yoga is beneficial."
            ]
        },
        'Risky': {
            'clinical': [
                "Consult an endocrinologist immediately.",
                "Regular blood sugar monitoring is required.",
                "Follow prescribed medical treatment strictly.",
                "Reduce carbohydrate and sugar intake."
            ],
            'herbal': [
                "Neem leaves may help control blood sugar.",
                "Amla supports metabolic health.",
                "Avoid sugary and fried foods.",
                "Practice stress management techniques."
            ]
        }
    },

    'heart': {
        'Normal': {
            'clinical': [
                "Maintain healthy cholesterol levels.",
                "Regular cardiovascular exercise.",
                "Routine blood pressure monitoring."
            ],
            'herbal': [
                "Garlic supports heart health.",
                "Omega-3 rich foods like flaxseed are beneficial.",
                "Meditation improves cardiovascular wellness."
            ]
        },
        'Risky': {
            'clinical': [
                "Immediate cardiologist consultation required.",
                "Strict blood pressure and cholesterol control.",
                "Medication adherence is essential."
            ],
            'herbal': [
                "Arjuna bark traditionally supports heart function.",
                "Reduce salt and saturated fats.",
                "Smoking cessation is critical."
            ]
        }
    },

    'kidney': {
        'Normal': {
            'clinical': [
                "Stay well hydrated.",
                "Routine kidney function tests.",
                "Maintain normal blood pressure."
            ],
            'herbal': [
                "Coconut water supports hydration.",
                "Cranberry may support urinary health.",
                "Low-sodium diet is beneficial."
            ]
        },
        'Risky': {
            'clinical': [
                "Consult a nephrologist immediately.",
                "Monitor creatinine and kidney markers.",
                "Limit protein and salt intake as advised."
            ],
            'herbal': [
                "Punarnava traditionally supports kidney health.",
                "Avoid painkillers without prescription.",
                "Maintain adequate fluid intake."
            ]
        }
    },

    'liver': {
        'Normal': {
            'clinical': [
                "Maintain healthy liver enzyme levels.",
                "Avoid unnecessary medications.",
                "Limit alcohol consumption."
            ],
            'herbal': [
                "Turmeric supports liver detoxification.",
                "Milk thistle is hepatoprotective.",
                "Balanced diet supports liver function."
            ]
        },
        'Risky': {
            'clinical': [
                "Consult a hepatologist immediately.",
                "Regular liver function tests required.",
                "Avoid alcohol completely."
            ],
            'herbal': [
                "Amla supports liver regeneration.",
                "Kutki is traditionally used for liver care.",
                "Avoid fatty and fried foods."
            ]
        }
    },

    'malaria': {
        'Normal': {
            'clinical': [
                "Prevent mosquito exposure.",
                "Maintain immunity and hydration."
            ],
            'herbal': [
                "Neem-based mosquito repellents.",
                "Papaya leaf juice traditionally used.",
                "Adequate hydration is essential."
            ]
        },
        'Risky': {
            'clinical': [
                "Immediate medical treatment required.",
                "Antimalarial drugs are essential.",
                "Monitor platelet count closely."
            ],
            'herbal': [
                "Papaya leaf extract may support platelet recovery.",
                "Tulsi supports immune function.",
                "Complete rest and hydration."
            ]
        }
    },

    'thyroid': {
        'Normal': {
            'clinical': [
                "Annual thyroid profile testing.",
                "Maintain balanced iodine intake."
            ],
            'herbal': [
                "Ashwagandha supports thyroid balance.",
                "Selenium-rich foods are beneficial.",
                "Stress reduction is important."
            ]
        },
        'Risky': {
            'clinical': [
                "Consult an endocrinologist.",
                "Strict medication adherence required.",
                "Regular TSH monitoring."
            ],
            'herbal': [
                "Avoid excess soy intake.",
                "Yoga and pranayama may help.",
                "Ensure adequate sleep."
            ]
        }
    },

    'pneumonia': {
        'Normal': {
            'clinical': [
                "Maintain respiratory hygiene.",
                "Annual flu vaccination recommended."
            ],
            'herbal': [
                "Steam inhalation improves breathing.",
                "Tulsi and ginger tea support immunity.",
                "Breathing exercises are helpful."
            ]
        },
        'Risky': {
            'clinical': [
                "Immediate medical treatment required.",
                "Antibiotics or oxygen support if prescribed.",
                "Monitor oxygen saturation."
            ],
            'herbal': [
                "Licorice supports respiratory health.",
                "Honey and ginger soothe airways.",
                "Complete bed rest is essential."
            ]
        }
    }

}


# --------------------------------------------------
# Routes
# --------------------------------------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/detect')
def detect():
    diseases = list(MODEL_FEATURES.keys())
    DISEASE_PARAMETERS = MODEL_FEATURES
    return render_template('detect.html', diseases=diseases, DISEASE_PARAMETERS=DISEASE_PARAMETERS)

@app.route('/consult')
def consult():
    doctors = [
        {"name": "Dr. Alice Smith", "specialty": "Cardiology", "experience": "10 years", "phone": "1234567890"},
        {"name": "Dr. Bob Johnson", "specialty": "Nephrology", "experience": "8 years", "phone": "0987654321"},
        # add more doctors
    ]
    return render_template('consult.html', doctors=doctors)


@app.route('/about')
def about():
    return render_template('about.html')

# --------------------------------------------------
# Signup
# --------------------------------------------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if not username or not password or not email:
            return render_template('signup.html', error="All fields are required.")

        # Hash password securely using pbkdf2:sha256
        password_hash = generate_password_hash(password, method='pbkdf2:sha256')

        conn = get_db_connection()
        # Check if username already exists
        existing = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        if existing:
            conn.close()
            return render_template('signup.html', error="Username already exists. Choose another.")
        
        conn.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, password_hash)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('login'))
    return render_template('signup.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        conn.close()

        if not user:
            return render_template('login.html', error="Invalid username or password")

        stored_hash = user['password_hash']

        # Skip login if hash is empty
        if not stored_hash or stored_hash.strip() == '':
            return render_template('login.html', error="Password not set for this user. Please sign up again.")

        # Ensure hash is string
        if isinstance(stored_hash, (bytes, bytearray)):
            try:
                stored_hash = stored_hash.decode('utf-8')
            except Exception:
                # keep as bytes for bcrypt
                pass

        # Detect bcrypt-style hashes (they start with $2a/$2b/$2y)
        try:
            is_bcrypt = False
            if isinstance(stored_hash, (bytes, bytearray)):
                is_bcrypt = bytes(stored_hash).startswith(b'$2')
            elif isinstance(stored_hash, str):
                is_bcrypt = stored_hash.startswith('$2')

            if is_bcrypt:
                if not _HAS_BCRYPT:
                    return render_template('login.html', error='Server misconfiguration: bcrypt not available')
                hash_bytes = stored_hash if isinstance(stored_hash, (bytes, bytearray)) else stored_hash.encode('utf-8')
                if bcrypt.checkpw(password.encode('utf-8'), hash_bytes):
                    session['user_id'] = user['id']
                    session['username'] = username
                    return redirect(url_for('dashboard'))
                else:
                    return render_template('login.html', error='Invalid username or password')
            else:
                # Use werkzeug for pbkdf2 / scrypt etc.
                if check_password_hash(stored_hash, password):
                    session['user_id'] = user['id']
                    session['username'] = username
                    return redirect(url_for('dashboard'))
        except ValueError:
            # Raised by werkzeug if stored hash is malformed
            return render_template('login.html', error='Stored password hash is invalid')

        return render_template('login.html', error="Invalid username or password")

    return render_template('login.html')


# --------------------------------------------------
# Dashboard
# --------------------------------------------------
@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    conn = get_db_connection()
    history = conn.execute(
        "SELECT * FROM predictions WHERE user_id=? ORDER BY timestamp DESC", (user_id,)
    ).fetchall()
    conn.close()
    return render_template('dashboard.html', history=history)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# --------------------------------------------------
# Prediction route
# --------------------------------------------------
@app.route('/predict/<disease_name>', methods=['POST'])
def predict(disease_name):
    inputs = request.form.to_dict()

    # ---------- RULE BASED ----------
    if disease_name in RULE_BASED:
        result = RULE_BASED[disease_name](inputs)

    # ---------- ML BASED ----------
    elif disease_name in ML_DISEASES:
        components = MODEL_COMPONENTS.get(disease_name)
        if not components:
            return jsonify({'status': 'error', 'error': f'Model for {disease_name} not found.'})

        features = MODEL_FEATURES[disease_name]
        X_dict = {}

        for f in features:
            try:
                X_dict[f] = [float(inputs.get(f, 0))]
            except:
                X_dict[f] = [0.0]

        X_df = pd.DataFrame(X_dict)
        X_imputed = components['imputer'].transform(X_df)
        X_scaled = components['scaler'].transform(X_imputed)

        pred = components['model'].predict(X_scaled)[0]
        prob = components['model'].predict_proba(X_scaled)[0][1]

        # ---------- STEP 4: MEDICAL SANITY LOGIC (KIDNEY ONLY) ----------
   
        if disease_name == 'kidney':
            try:
                sg = float(inputs.get('sg', 0))
                al = float(inputs.get('al', 0))
                rbc = float(inputs.get('rbc', 0))
                pc = float(inputs.get('pc', 0))
                hemo = float(inputs.get('hemo', 0))
                wc = float(inputs.get('wc', 0))
                rc = float(inputs.get('rc', 0))
                bp = float(inputs.get('bp', 0))
            except:
                result = "Risky"
            else:
                # Kidney normal ranges
                if sg < 1.005 or sg > 1.030:
                    result = "Risky"
                elif al > 2:
                    result = "Risky"
                elif rbc < 3.5 or rbc > 5.5:
                    result = "Risky"
                elif pc < 150 or pc > 450:
                    result = "Risky"
                elif hemo < 13.5 or hemo > 17.5:
                    result = "Risky"
                elif wc < 4000 or wc > 11000:
                    result = "Risky"
                elif rc < 4.2 or rc > 5.4:
                    result = "Risky"
                elif bp < 90 or bp > 140:
                    result = "Risky"
                else:
                    result = "Normal"
        else:
            result = "Normal" if pred == 0 else "Risky"


    else:
        return jsonify({'status': 'error', 'error': 'Disease not recognized.'})

    # ---------- SUGGESTIONS ----------
    suggestion_block = SUGGESTIONS.get(disease_name, {}).get(result, {})
    clinical = suggestion_block.get('clinical', [])
    herbal = suggestion_block.get('herbal', [])

    # ---------- SAVE PREDICTION ----------
    user_id = session.get('user_id')
    if user_id:
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO predictions (user_id, disease, input_data, result) VALUES (?, ?, ?, ?)",
            (user_id, disease_name, str(inputs), result)
        )
        conn.commit()
        conn.close()

    # ---------- STYLED HTML OUTPUT ----------
    html = f"""
    <div class="result-box {'normal-box' if result=='Normal' else 'risk-box'}">
        <h3>{disease_name.title()} Prediction</h3>
        <p class="result-text">{result}</p>
    </div>

    <div class="recommendation-grid">
        <div class="recommendation-card clinical-card">
            <h4>Clinical Recommendations</h4>
            <ul>
                {''.join(f"<li>{c}</li>" for c in clinical)}
            </ul>
        </div>

        <div class="recommendation-card herbal-card">
            <h4>Herbal & Lifestyle Support</h4>
            <ul>
                {''.join(f"<li>{h}</li>" for h in herbal)}
            </ul>
        </div>
    </div>

    <p class="disclaimer">
        Herbal suggestions are supportive only and do not replace medical treatment.
    </p>
    """

    return jsonify({'status': 'success', 'html': html})





# --------------------------------------------------
# Run app
# --------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)

