def calcular_macros(peso, altura, edad, sexo, actividad, objetivo):
    """
    Calcula calorías y macros personalizados.
    Fórmula: Harris-Benedict revisada (Mifflin-St Jeor)
    """

    # ── PASO 1: TMB (Tasa Metabólica Basal) ──
    if sexo == "Masculino":
        tmb = 10 * peso + 6.25 * altura - 5 * edad + 5
    else:
        tmb = 10 * peso + 6.25 * altura - 5 * edad - 161

    # ── PASO 2: Factor de actividad ──
    factores = {
        "Sedentario (sin ejercicio)":         1.2,
        "Ligero (1-3 días/semana)":           1.375,
        "Moderado (3-5 días/semana)":         1.55,
        "Intenso (6-7 días/semana)":          1.725,
        "Muy intenso (doble turno/trabajo físico)": 1.9,
    }
    tdee = tmb * factores[actividad]

    # ── PASO 3: Ajuste según objetivo ──
    if objetivo == "Perder grasa":
        calorias = tdee - 400
    elif objetivo == "Ganar músculo":
        calorias = tdee + 300
    else:  # Mantener
        calorias = tdee

    # ── PASO 4: Distribución de macros ──
    if objetivo == "Perder grasa":
        proteina = peso * 2.2      # alta proteína para preservar músculo
        grasas = peso * 0.8
        carbos = (calorias - proteina * 4 - grasas * 9) / 4

    elif objetivo == "Ganar músculo":
        proteina = peso * 2.0
        grasas = peso * 1.0
        carbos = (calorias - proteina * 4 - grasas * 9) / 4

    else:  # Mantener
        proteina = peso * 1.8
        grasas = peso * 0.9
        carbos = (calorias - proteina * 4 - grasas * 9) / 4

    # Asegurar que carbos no sea negativo
    carbos = max(carbos, 50)

    return {
        "calorias": round(calorias),
        "proteina": round(proteina),
        "carbos":   round(carbos),
        "grasas":   round(grasas),
    }