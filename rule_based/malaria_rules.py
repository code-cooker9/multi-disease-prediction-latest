def malaria_rule_based(inputs):
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
    if temp <= 0 or temp > 115:
        return "Risky"
    if headache not in [0, 1] or vomiting not in [0, 1] or joint_pain not in [0, 1]:
        return "Risky"
    # Adjusted for actual input units
    if rbc <= 0 or rbc > 1e6:  
        return "Risky"

    # Fever rules
    if temp > 100 and (headache or vomiting or joint_pain):
        return "Risky"
    if temp > 99 and (headache or vomiting or joint_pain):
        return "Risky"

    return "Normal"