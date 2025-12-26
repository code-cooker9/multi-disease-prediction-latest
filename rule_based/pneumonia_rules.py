def pneumonia_rule_based(inputs):
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
