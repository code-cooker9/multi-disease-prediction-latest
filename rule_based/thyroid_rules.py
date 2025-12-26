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

