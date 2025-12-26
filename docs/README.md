# Multi-Disease Prediction System

A web-based healthcare application that uses machine learning to predict various diseases and provide personalized health insights. The system can predict multiple diseases including diabetes, heart disease, liver disease, kidney disease, and more.

## 🌟 Features

- **Multi-Disease Prediction**: Support for various diseases including:
  - Diabetes
  - Heart Disease
  - Kidney Disease
  - Liver Disease
  - Malaria
  - Pneumonia
  - Thyroid

- **User Management**:
  - Secure user authentication
  - Personal dashboard
  - Prediction history tracking

- **Professional Consultation**:
  - Doctor directory
  - Specialist recommendations
  - Contact system

- **Health Insights**:
  - Personalized health suggestions
  - Risk level assessment
  - Natural remedy recommendations

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

### Environment Setup

1. Clone the repository:
```bash
git clone https://github.com/code-cooker9/multi-disease-prediction.git
cd multi-disease-prediction
```

2. Create and activate a virtual environment:

Windows:
```powershell
python -m venv venv
.\venv\Scripts\activate
```

Linux/Mac:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

### Database Setup

1. Initialize the database:
```bash
flask initdb
```

This will create the necessary tables for:
- User management
- Prediction history
- Contact messages

### Running the Application

1. Set the Flask environment:

Windows (PowerShell):
```powershell
$env:FLASK_APP="app.py"
$env:FLASK_ENV="development"
flask run
```

Linux/Mac:
```bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

2. Access the application at: http://127.0.0.1:5000

## 📋 Usage Guide

1. **Create an Account**:
   - Click "Sign Up" in the navigation bar
   - Enter your details
   - Verify your account through the success message

2. **Disease Prediction**:
   - Login to your account
   - Navigate to "Detect" page
   - Select the disease you want to check
   - Fill in the required parameters
   - Get instant prediction results

3. **View History**:
   - Access your dashboard
   - View all your previous predictions
   - Track your health progress

4. **Consult Specialists**:
   - Visit the "Consult" page
   - Find relevant specialists
   - Get their contact information

## 🔒 Security Features

- Password hashing using bcrypt
- Session management
- SQL injection prevention
- CSRF protection
- Input validation and sanitization

## 📁 Project Structure

```
multi-disease-prediction/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── ml_pipeline.py        # ML model utilities
├── database/
│   └── schema.sql       # Database schema
├── models/              # ML models and preprocessors
├── src/
│   └── prediction_service.py  # Prediction logic
├── static/
│   ├── css/            # Stylesheets
│   ├── js/            # JavaScript files
│   └── images/        # Image assets
└── templates/         # HTML templates
    ├── user/         # User-specific templates
    └── *.html        # Main templates
```

## 🤝 Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/improvement`)
3. Make your changes
4. Commit your changes (`git commit -am 'Add new feature'`)
5. Push to the branch (`git push origin feature/improvement`)
6. Create a Pull Request

## ⚠️ Disclaimer

This system is designed for educational purposes and should not be used as a substitute for professional medical advice. Always consult with healthcare professionals for medical decisions.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Flask framework
- scikit-learn
- Bootstrap
- All contributors and testers

## 💡 Support

For support, questions, or feedback:
1. Open an issue in the repository
2. Use the contact form in the application
3. Reach out to the maintainers