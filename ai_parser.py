import os
import json
from groq import Groq
from dotenv import load_dotenv
from foods import ALIMENTOS

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def interpretar_comida(texto):

    alimentos_disponibles = list(ALIMENTOS.keys())

    prompt = f"""
El usuario describió lo que comió: "{texto}"

Tenés esta lista de alimentos disponibles:
{json.dumps(alimentos_disponibles, ensure_ascii=False)}

Tu tarea: identificá cada alimento que mencionó el usuario y mapealo al nombre más cercano de la lista.

Devolvé ÚNICAMENTE este JSON, sin explicaciones, sin backticks:
{{
    "items": [
        {{"alimento": "nombre exacto de la lista", "gramos": 100, "en_lista": true}},
        {{"alimento": "nombre libre si no está en lista", "gramos": 100, "en_lista": false}}
    ]
}}

Reglas:
- Si el usuario dice "pechuga" → "Pechuga de pollo (cocida)"
- Si dice "arroz" → "Arroz blanco (cocido)"
- Si dice "pan lactal" → "Pan blanco"
- Si dice "carne" → "Carne picada magra (cocida)"
- Si dice "fideos" → "Fideos (cocidos)"
- Si el alimento no tiene equivalente → en_lista: false
- Para unidades (ej: "2 huevos") convertí a gramos (1 huevo = 60g)
- Para cucharadas de aceite = 14g por cucharada
- Solo el JSON
"""

    respuesta = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "Sos un nutricionista. Solo respondés con JSON válido."},
            {"role": "user",   "content": prompt}
        ],
        temperature=0,
        max_tokens=500
    )

    texto_respuesta = respuesta.choices[0].message.content.strip()
    texto_respuesta = texto_respuesta.replace("```json", "").replace("```", "").strip()
    items = json.loads(texto_respuesta)["items"]

    # ── Calcular macros por ítem y totales ──
    MICRO_KEYS_LOCAL = [
        "magnesio_mg", "zinc_mg", "hierro_mg", "calcio_mg", "potasio_mg",
        "sodio_mg", "vitamina_c_mg", "vitamina_d_iu", "vitamina_b12_mcg", "omega3_g"
    ]

    totales = {
        "calorias": 0, "proteina": 0, "carbos": 0, "grasas": 0,
        **{k: 0 for k in MICRO_KEYS_LOCAL}
    }

    items_sin_datos  = []
    detalle_items    = []

    for item in items:
        nombre   = item["alimento"]
        gramos   = item["gramos"]
        en_lista = item.get("en_lista", False)

        if en_lista and nombre in ALIMENTOS:
            datos  = ALIMENTOS[nombre]
            factor = gramos / 100

            item_macros = {
                "nombre":   nombre,
                "gramos":   gramos,
                "calorias": round(datos["calorias"]  * factor, 1),
                "proteina": round(datos["proteina"]  * factor, 1),
                "carbos":   round(datos["carbos"]    * factor, 1),
                "grasas":   round(datos["grasas"]    * factor, 1),
            }
            for k in MICRO_KEYS_LOCAL:
                item_macros[k] = round(datos.get(k, 0) * factor, 2)

            detalle_items.append(item_macros)

            totales["calorias"] += item_macros["calorias"]
            totales["proteina"] += item_macros["proteina"]
            totales["carbos"]   += item_macros["carbos"]
            totales["grasas"]   += item_macros["grasas"]
            for k in MICRO_KEYS_LOCAL:
                totales[k] += item_macros[k]

        else:
            items_sin_datos.append(item)
            detalle_items.append({
                "nombre": nombre,
                "gramos": gramos,
                "sin_datos": True
            })

    # ── Alimentos fuera de lista → calcular con IA ──
    if items_sin_datos:
        prompt_extra = f"""
Calculá macros y micronutrientes de estos alimentos:
{json.dumps(items_sin_datos, ensure_ascii=False)}

Devolvé ÚNICAMENTE este JSON, sin backticks:
{{
    "items": [
        {{
            "alimento": "nombre",
            "gramos": 100,
            "calorias": 0,
            "proteina": 0,
            "carbos": 0,
            "grasas": 0,
            "magnesio_mg": 0,
            "zinc_mg": 0,
            "hierro_mg": 0,
            "calcio_mg": 0,
            "potasio_mg": 0,
            "sodio_mg": 0,
            "vitamina_c_mg": 0,
            "vitamina_d_iu": 0,
            "vitamina_b12_mcg": 0,
            "omega3_g": 0
        }}
    ]
}}
"""
        resp_extra = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Nutricionista experto. Solo JSON válido."},
                {"role": "user",   "content": prompt_extra}
            ],
            temperature=0,
            max_tokens=600
        )

        texto_extra = resp_extra.choices[0].message.content.strip()
        texto_extra = texto_extra.replace("```json", "").replace("```", "").strip()
        extra_items = json.loads(texto_extra)["items"]

        for ei in extra_items:
            # Actualizar el item en detalle_items
            for di in detalle_items:
                if di.get("sin_datos") and di["nombre"] == ei["alimento"]:
                    di.update({
                        "calorias": round(ei.get("calorias", 0), 1),
                        "proteina": round(ei.get("proteina", 0), 1),
                        "carbos":   round(ei.get("carbos",   0), 1),
                        "grasas":   round(ei.get("grasas",   0), 1),
                    })
                    for k in MICRO_KEYS_LOCAL:
                        di[k] = round(ei.get(k, 0), 2)
                    di.pop("sin_datos", None)

            # Sumar a totales
            totales["calorias"] += ei.get("calorias", 0)
            totales["proteina"] += ei.get("proteina", 0)
            totales["carbos"]   += ei.get("carbos",   0)
            totales["grasas"]   += ei.get("grasas",   0)
            for k in MICRO_KEYS_LOCAL:
                totales[k] += ei.get(k, 0)

    # Redondear totales
    for k in totales:
        totales[k] = round(totales[k], 1)

    descripciones = [f"{i['gramos']:.0f}g de {i['nombre']}" for i in detalle_items]
    totales["descripcion"] = ", ".join(descripciones)
    totales["detalle"]     = detalle_items

    return totales