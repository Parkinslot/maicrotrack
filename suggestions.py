from datetime import datetime, timedelta
from foods import ALIMENTOS

MICRO_KEYS = [
    "magnesio_mg", "zinc_mg", "hierro_mg", "calcio_mg", "potasio_mg",
    "sodio_mg", "vitamina_c_mg", "vitamina_d_iu", "vitamina_b12_mcg", "omega3_g"
]

PLATOS = {
    "desayuno": [
        {"nombre": "Avena con banana y leche",
         "ingredientes": [("Avena (cruda)", 80), ("Banana", 100), ("Leche entera", 200)],
         "micros_fuertes": ["magnesio_mg", "potasio_mg"]},
        {"nombre": "Huevos revueltos con tostadas integrales",
         "ingredientes": [("Huevo entero (cocido)", 180), ("Pan integral", 60)],
         "micros_fuertes": ["vitamina_d_iu", "vitamina_b12_mcg", "zinc_mg"]},
        {"nombre": "Yogur griego con almendras y banana",
         "ingredientes": [("Yogur griego natural (0%)", 250), ("Almendras", 30), ("Banana", 100)],
         "micros_fuertes": ["calcio_mg", "magnesio_mg", "potasio_mg"]},
        {"nombre": "Tostadas con queso cottage y palta",
         "ingredientes": [("Pan integral", 80), ("Queso cottage", 150), ("Palta", 60)],
         "micros_fuertes": ["calcio_mg", "omega3_g"]},
    ],
    "almuerzo": [
        {"nombre": "Pechuga con arroz y brócoli",
         "ingredientes": [("Pechuga de pollo (cocida)", 250), ("Arroz blanco (cocido)", 200), ("Brócoli (cocido)", 150)],
         "micros_fuertes": ["vitamina_c_mg", "zinc_mg"]},
        {"nombre": "Carne con papa y ensalada",
         "ingredientes": [("Bife de lomo (cocido)", 250), ("Papa hervida", 250), ("Tomate", 100)],
         "micros_fuertes": ["hierro_mg", "zinc_mg", "vitamina_b12_mcg", "potasio_mg"]},
        {"nombre": "Atún con fideos y tomate",
         "ingredientes": [("Atún en agua (enlatado)", 200), ("Fideos (cocidos)", 250), ("Tomate", 100), ("Aceite de oliva", 10)],
         "micros_fuertes": ["vitamina_d_iu", "vitamina_b12_mcg", "omega3_g"]},
        {"nombre": "Salmón con batata y espinaca",
         "ingredientes": [("Salmón (cocido)", 200), ("Batata hervida", 200), ("Espinaca (cocida)", 150)],
         "micros_fuertes": ["omega3_g", "vitamina_d_iu", "hierro_mg", "magnesio_mg"]},
        {"nombre": "Pechuga con fideos y zapallo",
         "ingredientes": [("Pechuga de pollo (cocida)", 200), ("Fideos (cocidos)", 200), ("Zapallo (cocido)", 150)],
         "micros_fuertes": ["vitamina_c_mg", "zinc_mg"]},
        {"nombre": "Carne picada con arroz integral y zanahoria",
         "ingredientes": [("Carne picada magra (cocida)", 200), ("Arroz integral (cocido)", 200), ("Zanahoria", 100)],
         "micros_fuertes": ["hierro_mg", "zinc_mg", "vitamina_b12_mcg", "magnesio_mg"]},
    ],
    "merienda": [
        {"nombre": "Yogur griego con almendras",
         "ingredientes": [("Yogur griego natural (0%)", 200), ("Almendras", 30)],
         "micros_fuertes": ["calcio_mg", "magnesio_mg"]},
        {"nombre": "Pan integral con palta y huevo",
         "ingredientes": [("Pan integral", 60), ("Palta", 80), ("Huevo entero (cocido)", 60)],
         "micros_fuertes": ["omega3_g", "vitamina_d_iu"]},
        {"nombre": "Banana con maní y leche",
         "ingredientes": [("Banana", 120), ("Maní", 30), ("Leche entera", 200)],
         "micros_fuertes": ["potasio_mg", "magnesio_mg", "calcio_mg"]},
        {"nombre": "Queso cottage con manzana",
         "ingredientes": [("Queso cottage", 200), ("Manzana", 150)],
         "micros_fuertes": ["calcio_mg", "vitamina_c_mg"]},
    ],
    "cena": [
        {"nombre": "Pechuga con zapallo y zanahoria",
         "ingredientes": [("Pechuga de pollo (cocida)", 220), ("Zapallo (cocido)", 200), ("Zanahoria", 100)],
         "micros_fuertes": ["vitamina_c_mg", "zinc_mg", "potasio_mg"]},
        {"nombre": "Huevos con arroz integral y espinaca",
         "ingredientes": [("Huevo entero (cocido)", 180), ("Arroz integral (cocido)", 200), ("Espinaca (cocida)", 150)],
         "micros_fuertes": ["vitamina_d_iu", "hierro_mg", "magnesio_mg"]},
        {"nombre": "Atún con papa y brócoli",
         "ingredientes": [("Atún en agua (enlatado)", 200), ("Papa hervida", 250), ("Brócoli (cocido)", 150)],
         "micros_fuertes": ["vitamina_d_iu", "vitamina_b12_mcg", "vitamina_c_mg", "potasio_mg"]},
        {"nombre": "Carne con batata y ensalada",
         "ingredientes": [("Bife de lomo (cocido)", 200), ("Batata hervida", 200), ("Tomate", 100)],
         "micros_fuertes": ["hierro_mg", "zinc_mg", "vitamina_b12_mcg", "potasio_mg"]},
        {"nombre": "Salmón con fideos y espinaca",
         "ingredientes": [("Salmón (cocido)", 180), ("Fideos (cocidos)", 150), ("Espinaca (cocida)", 100)],
         "micros_fuertes": ["omega3_g", "vitamina_d_iu", "hierro_mg"]},
    ],
    "snack": [
        {"nombre": "Mix de frutos secos",
         "ingredientes": [("Almendras", 25), ("Maní", 25)],
         "micros_fuertes": ["magnesio_mg", "zinc_mg"]},
        {"nombre": "Manzana con maní",
         "ingredientes": [("Manzana", 150), ("Maní", 30)],
         "micros_fuertes": ["vitamina_c_mg", "magnesio_mg"]},
    ],
}


def calcular_macros_plato(ingredientes):
    macros = {"calorias": 0, "proteina": 0, "carbos": 0, "grasas": 0}
    for k in MICRO_KEYS:
        macros[k] = 0
    for nombre, gramos in ingredientes:
        if nombre in ALIMENTOS:
            datos  = ALIMENTOS[nombre]
            factor = gramos / 100
            macros["calorias"] += datos["calorias"] * factor
            macros["proteina"] += datos["proteina"] * factor
            macros["carbos"]   += datos["carbos"]   * factor
            macros["grasas"]   += datos["grasas"]   * factor
            for k in MICRO_KEYS:
                macros[k] += datos.get(k, 0) * factor
    for k in macros:
        macros[k] = round(macros[k], 1)
    return macros


def get_tipos_comidos(meals_hoy):
    tipos = set()
    for meal in meals_hoy:
        tipos.add(meal.meal_type.lower())
    return tipos


def get_micros_semana(all_meals, micro_labels):
    """Calcula el promedio de cumplimiento de micros de los últimos 7 días."""
    hoy       = datetime.now().date()
    hace_7    = hoy - timedelta(days=7)
    meals_sem = [m for m in all_meals if hace_7 <= m.created_at.date() < hoy]

    if not meals_sem:
        return {k: 0 for k in MICRO_KEYS}

    dias = max(len(set(m.created_at.date() for m in meals_sem)), 1)
    acum = {k: 0 for k in MICRO_KEYS}

    for meal in meals_sem:
        for k in MICRO_KEYS:
            acum[k] += getattr(meal, k, 0) or 0

    promedio_pct = {}
    for k in MICRO_KEYS:
        objetivo = micro_labels[k]["goal"]
        promedio = acum[k] / dias
        promedio_pct[k] = (promedio / objetivo * 100) if objetivo > 0 else 100

    return promedio_pct


def sugerir_comidas(totals, goal, micro_labels, meals_hoy=None, all_meals=None):
    if meals_hoy is None:
        meals_hoy = []
    if all_meals is None:
        all_meals = []

    cal_restantes = goal.calories - totals["calories"]
    pro_restantes = goal.protein  - totals["protein"]
    car_restantes = goal.carbs    - totals["carbs"]
    fat_restantes = goal.fats     - totals["fats"]

    if cal_restantes <= 0:
        return [{
            "tipo": "—", "nombre": "Objetivo calórico alcanzado 🎉",
            "razon": f"Ya consumiste {totals['calories']:.0f} de {goal.calories:.0f} kcal.",
            "macros": "—", "detalle_html": ""
        }]

    tipos_comidos    = get_tipos_comidos(meals_hoy)
    orden            = ["desayuno", "almuerzo", "merienda", "cena", "snack"]
    tipos_pendientes = [t for t in orden if t not in tipos_comidos]

    if not tipos_pendientes:
        return [{
            "tipo": "—", "nombre": "¡Todas las comidas registradas! 🎉",
            "razon": "Ya registraste todas las comidas del día.",
            "macros": "—", "detalle_html": ""
        }]

    # ── Micros débiles de la semana ──
    micros_semana = get_micros_semana(all_meals, micro_labels)
    # Ordenar de menor a mayor cumplimiento
    micros_debiles = sorted(micros_semana.items(), key=lambda x: x[1])
    # Los 5 micros más débiles de la semana
    top_debiles = set(k for k, v in micros_debiles[:5])

    # ── Buscar mejor combinación ──
    mejor_combo = None
    mejor_score = float("inf")

    def generar_combos(tipos, index, combo_actual, nombres_usados):
        nonlocal mejor_combo, mejor_score

        if index == len(tipos):
            sum_cal = sum(c["macros_dict"]["calorias"] for c in combo_actual)
            sum_pro = sum(c["macros_dict"]["proteina"] for c in combo_actual)
            sum_car = sum(c["macros_dict"]["carbos"]   for c in combo_actual)
            sum_fat = sum(c["macros_dict"]["grasas"]   for c in combo_actual)

            diff_cal = cal_restantes - sum_cal
            diff_pro = pro_restantes - sum_pro
            diff_car = car_restantes - sum_car
            diff_fat = fat_restantes - sum_fat

            penalty_cal = abs(diff_cal) * (2.5 if diff_cal < 0 else 1.0)
            penalty_pro = abs(diff_pro) * (6.0 if diff_pro > 0 else 1.5)
            penalty_car = abs(diff_car) * 0.5
            penalty_fat = abs(diff_fat) * 0.5

            # Bonus por cubrir micros débiles de la semana
            micro_bonus = 0
            for c in combo_actual:
                for micro_key in c.get("micros_fuertes", []):
                    if micro_key in top_debiles:
                        micro_bonus += 15

            score = penalty_cal + penalty_pro + penalty_car + penalty_fat - micro_bonus

            if score < mejor_score:
                mejor_score = score
                mejor_combo = list(combo_actual)
            return

        tipo   = tipos[index]
        platos = PLATOS.get(tipo, [])

        for plato in platos:
            nombre_base = plato["nombre"].split(" con ")[0].strip().lower()
            proteina_base = ""
            for ingr, _ in plato["ingredientes"]:
                ingr_lower = ingr.lower()
                if any(p in ingr_lower for p in ["pollo", "carne", "atún", "salmón", "huevo", "bife"]):
                    proteina_base = ingr_lower
                    break

            if nombre_base in nombres_usados or proteina_base in nombres_usados:
                continue

            macros = calcular_macros_plato(plato["ingredientes"])

            detalle_html = ""
            for nombre, gramos in plato["ingredientes"]:
                detalle_html += f"<span style='color:#6b7280; font-size:0.75rem'>• {gramos}g {nombre}</span><br>"

            entrada = {
                "tipo":          tipo.capitalize(),
                "nombre":        plato["nombre"],
                "macros_dict":   macros,
                "macros":        f"🔥 {macros['calorias']:.0f} kcal | 🥩 {macros['proteina']:.0f}g | 🍚 {macros['carbos']:.0f}g | 🥑 {macros['grasas']:.0f}g",
                "detalle_html":  detalle_html,
                "micros_fuertes": plato.get("micros_fuertes", []),
            }

            nuevos_nombres = nombres_usados | {nombre_base}
            if proteina_base:
                nuevos_nombres.add(proteina_base)

            combo_actual.append(entrada)
            generar_combos(tipos, index + 1, combo_actual, nuevos_nombres)
            combo_actual.pop()

    tipos_a_planear = tipos_pendientes[:4]
    generar_combos(tipos_a_planear, 0, [], set())

    if not mejor_combo:
        return [{
            "tipo": "—", "nombre": "No se encontraron combinaciones",
            "razon": "Agregá más alimentos a la base.",
            "macros": "—", "detalle_html": ""
        }]

    # ── Agregar resumen ──
    total_cal = sum(c["macros_dict"]["calorias"] for c in mejor_combo)
    total_pro = sum(c["macros_dict"]["proteina"] for c in mejor_combo)
    total_car = sum(c["macros_dict"]["carbos"]   for c in mejor_combo)
    total_fat = sum(c["macros_dict"]["grasas"]   for c in mejor_combo)

    # Micros que cubre esta combinación
    micros_cubiertos = set()
    for sug in mejor_combo:
        for mk in sug.get("micros_fuertes", []):
            if mk in top_debiles:
                micros_cubiertos.add(micro_labels[mk]["label"])

    micro_texto = ""
    if micros_cubiertos:
        micro_texto = f" Prioriza: {', '.join(micros_cubiertos)} (los más bajos de tu semana)."

    for sug in mejor_combo:
        sug["razon"] = (
            f"Plan: {total_cal:.0f}/{cal_restantes:.0f} kcal · "
            f"{total_pro:.0f}/{pro_restantes:.0f}g prot · "
            f"{total_car:.0f}/{car_restantes:.0f}g carbs · "
            f"{total_fat:.0f}/{fat_restantes:.0f}g grasas.{micro_texto}"
        )

    return mejor_combo

def reemplazar_plato(tipo, nombre_excluido, cal_objetivo, pro_objetivo, nombres_excluidos_global=None):
    """
    Busca un plato alternativo del mismo tipo con macros similares,
    excluyendo el plato actual y cualquier otro ya mostrado.
    """
    if nombres_excluidos_global is None:
        nombres_excluidos_global = set()

    tipo_lower = tipo.lower()
    platos     = PLATOS.get(tipo_lower, [])

    mejor       = None
    mejor_score = float("inf")

    for plato in platos:
        if plato["nombre"] == nombre_excluido:
            continue
        if plato["nombre"] in nombres_excluidos_global:
            continue

        # Verificar proteína base distinta
        proteina_base = ""
        for ingr, _ in plato["ingredientes"]:
            ingr_lower = ingr.lower()
            if any(p in ingr_lower for p in ["pollo", "carne", "atún", "salmón", "huevo", "bife"]):
                proteina_base = ingr_lower
                break

        if proteina_base in nombres_excluidos_global:
            continue

        macros = calcular_macros_plato(plato["ingredientes"])

        diff_cal = abs(macros["calorias"] - cal_objetivo)
        diff_pro = abs(macros["proteina"] - pro_objetivo)
        score    = diff_cal + diff_pro * 4

        if score < mejor_score:
            mejor_score = score
            mejor       = (plato, macros)

    if not mejor:
        return None

    plato, macros = mejor

    detalle_html = ""
    for nombre, gramos in plato["ingredientes"]:
        detalle_html += f"<span style='color:#6b7280; font-size:0.75rem'>• {gramos}g {nombre}</span><br>"

    return {
        "tipo":          tipo,
        "nombre":        plato["nombre"],
        "macros_dict":   macros,
        "macros":        f"🔥 {macros['calorias']:.0f} kcal | 🥩 {macros['proteina']:.0f}g | 🍚 {macros['carbos']:.0f}g | 🥑 {macros['grasas']:.0f}g",
        "detalle_html":  detalle_html,
        "micros_fuertes": plato.get("micros_fuertes", []),
        "razon":         f"Alternativa similar: {macros['calorias']:.0f} kcal · {macros['proteina']:.0f}g prot.",
    }