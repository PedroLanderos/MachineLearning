#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
import os
from collections import Counter

CSV_COLUMNS = ["nombre", "color", "citrica", "tropical", "con_semillas", "se_pela", "dulce"]
BOOL_FIELDS = ["citrica", "tropical", "con_semillas", "se_pela", "dulce"]
CATEGORICAL_FIELDS = ["color"]

# ---------- Normalización ----------
TRUE_TOKENS = {"sí", "si", "s", "true", "1", "x", "y", "yes"}
FALSE_TOKENS = {"no", "n", "false", "0"}

def normalize_bool(val):
    if val is None:
        return None
    if isinstance(val, bool):
        return val
    s = str(val).strip().lower()
    if s == "" or s == "?":
        return None
    if s in TRUE_TOKENS:
        return True
    if s in FALSE_TOKENS:
        return False
    return None

def normalize_color(val):
    if val is None:
        return None
    s = str(val).strip().lower()
    return s if s else None

def norm_row(d):
    out = {}
    for k in CSV_COLUMNS:
        v = d.get(k, "")
        if k in BOOL_FIELDS:
            out[k] = normalize_bool(v)
        elif k in CATEGORICAL_FIELDS:
            out[k] = normalize_color(v)
        else:
            out[k] = str(v).strip().lower()
    return out

# ---------- IO CSV ----------
def load_csv(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        if r.fieldnames != CSV_COLUMNS:
            raise ValueError(f"El CSV debe tener columnas exactas: {CSV_COLUMNS} (tiene {r.fieldnames})")
        for row in r:
            rows.append(norm_row(row))
    return rows

def append_to_csv(path, row):
    exists = os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        if not exists:
            w.writeheader()
        # CSV friendly: None -> ""
        to_write = {}
        for k in CSV_COLUMNS:
            v = row.get(k)
            to_write[k] = "" if v is None else v
        w.writerow(to_write)

# ---------- Preguntas (orden fijo) ----------
QUESTION_ORDER = [
    ("color", None),          # color es especial (entrada de texto o "?")
    ("citrica", True),
    ("tropical", True),
    ("con_semillas", True),
    ("se_pela", True),
    ("dulce", True),
]

def parse_sn(s):
    if s is None:
        return None
    s = str(s).strip().lower()
    if s in TRUE_TOKENS:
        return True
    if s in FALSE_TOKENS:
        return False
    if s in {"?", ""}:
        return None
    return None

def ask_all_questions(db):
    """
    Devuelve un dict con las respuestas del usuario en el mismo formato de la base:
    {"color": <str|None>, "citrica": <bool|None>, ...}
    """
    # Sugerir colores conocidos para ayudar
    known_colors = sorted(c for c, cnt in Counter([r["color"] for r in db if r["color"]]).items())
    known_colors_txt = ", ".join(known_colors) if known_colors else "rojo, amarillo, verde, morado, naranja, rosa, marrón, azul"

    print("Responde con s / n / ? (para desconocido).")
    print(f"Para el color, escribe el color en minúsculas (o ? si no sabes). Ej: {known_colors_txt}\n")

    answers = {}
    # 1) color (texto o ?)
    col = input("Color principal (minúsculas, o '?' si no sabes): ").strip().lower()
    answers["color"] = None if col == "?" or col == "" else normalize_color(col)

    # Booleanos en orden fijo (s/n/?)
    def ask_bool(prompt):
        ans = input(prompt).strip().lower()
        return parse_sn(ans)

    answers["citrica"] = ask_bool("¿Es cítrica? (s/n/?) ")
    answers["tropical"] = ask_bool("¿Es tropical? (s/n/?) ")
    answers["con_semillas"] = ask_bool("¿Tiene semillas? (s/n/?) ")
    answers["se_pela"] = ask_bool("¿Se pela para comer? (s/n/?) ")
    answers["dulce"] = ask_bool("¿Es dulce? (s/n/?) ")

    return answers

# ---------- Filtrado por respuestas ----------
def matches(candidate, answers):
    # color exacto si se especificó
    if answers.get("color") is not None:
        if candidate.get("color") is None or candidate["color"] != answers["color"]:
            return False
    # booleanos: si user respondió s/n, deben coincidir; si "?" (None), no filtra
    for f in BOOL_FIELDS:
        a = answers.get(f)
        if a is None:
            continue
        v = candidate.get(f)
        if v is None:
            return False  # usuario sabe el valor, pero el candidato lo tiene desconocido
        if bool(v) != bool(a):
            return False
    return True

def filter_candidates(db, answers):
    return [c for c in db if matches(c, answers)]

# ---------- Elección de conjetura ----------
def best_guess(candidates, answers):
    """
    Pondera coincidencias con las respuestas dadas (color y booleanos conocidos).
    """
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]["nombre"]

    def score(c):
        s = 0
        if answers.get("color") is not None and c.get("color") == answers.get("color"):
            s += 2  # color pesa más
        for f in BOOL_FIELDS:
            a = answers.get(f)
            if a is None:
                continue
            v = c.get(f)
            if v is not None and bool(v) == bool(a):
                s += 1
        return s

    ranked = sorted(candidates, key=lambda x: (score(x), x["nombre"]), reverse=True)
    return ranked[0]["nombre"]

# ---------- Modo aprendizaje ----------
def learning_mode(csv_path):
    print("\nNo acerté 😅. Vamos a aprender esta fruta.")
    nombre = input("Nombre: ").strip().lower()
    color = normalize_color(input("Color (minúsculas): "))
    citrica = normalize_bool(input("¿Es cítrica? (s/n/?) "))
    tropical = normalize_bool(input("¿Es tropical? (s/n/?) "))
    con_semillas = normalize_bool(input("¿Tiene semillas? (s/n/?) "))
    se_pela = normalize_bool(input("¿Se pela para comer? (s/n/?) "))
    dulce = normalize_bool(input("¿Es dulce? (s/n/?) "))

    row = {
        "nombre": nombre,
        "color": color,
        "citrica": citrica,
        "tropical": tropical,
        "con_semillas": con_semillas,
        "se_pela": se_pela,
        "dulce": dulce,
    }
    append_to_csv(csv_path, row)
    print(f"¡Gracias! Añadí '{nombre}' al CSV.\n")

# ---------- Juego principal (orden fijo) ----------
def play(csv_path):
    db = load_csv(csv_path)

    print("Piensa en una FRUTA.")
    answers = ask_all_questions(db)  # SIEMPRE pregunta en el orden fijo

    # Filtrar candidatos
    candidates = filter_candidates(db, answers)

    # Conjeturar (una sola con confirmación)
    guess = best_guess(candidates, answers)
    if guess:
        resp = input(f"¿Es {guess}? (s/n) ").strip().lower()
        if resp in TRUE_TOKENS:
            print("¡Adiviné! 🎉")
            # nº de preguntas = 6 (siempre hace todas) + 1 de confirmación
            return True, 7
        else:
            # si hay más candidatos, podríamos intentar el segundo mejor
            # Para mantenerlo simple, aprendemos si falló la mejor conjetura
            learning_mode(csv_path)
            return False, 7
    else:
        learning_mode(csv_path)
        return False, 6  # hizo todas las preguntas, sin confirmación

# ---------- Métricas (simulación orden fijo) ----------
def simulate_quality(csv_path):
    db = load_csv(csv_path)
    if not db:
        print("Base vacía.")
        return
    total_q = 0
    hits = 0

    for target in db:
        # Simular respuestas del "usuario perfecto" = valores del target
        answers = {
            "color": target.get("color"),
            "citrica": target.get("citrica"),
            "tropical": target.get("tropical"),
            "con_semillas": target.get("con_semillas"),
            "se_pela": target.get("se_pela"),
            "dulce": target.get("dulce"),
        }
        candidates = filter_candidates(db, answers)
        guess = best_guess(candidates, answers)
        ok = (guess == target["nombre"])
        # Hace siempre 6 preguntas + confirmación si hubo conjetura
        q_used = 7 if guess else 6
        hits += 1 if ok else 0
        total_q += q_used

    avg_q = total_q / len(db)
    acc = 100.0 * hits / len(db)
    print(f"\nMÉTRICAS (simulación orden fijo sobre {len(db)} frutas):")
    print(f"- Nº de preguntas promedio: {avg_q:.2f}")
    print(f"- % de acierto: {acc:.1f}%\n")

# ---------- CLI ----------
def main():
    parser = argparse.ArgumentParser(description="Akinator de frutas (orden fijo + modo aprendizaje + métricas)")
    parser.add_argument("--csv", default="frutas_inicial.csv", help="Ruta al CSV de frutas")
    parser.add_argument("--simular", action="store_true", help="Solo calcular métricas de calidad y salir")
    args = parser.parse_args()

    if not os.path.exists(args.csv):
        print(f"⚠ No se encontró {args.csv}. Crea el CSV o indica la ruta con --csv.")
        return

    if args.simular:
        simulate_quality(args.csv)
        return

    print("=== Akinator de Frutas (orden fijo) ===")
    print(f"Usando base: {args.csv}")
    while True:
        ok, q = play(args.csv)
        again = input("¿Otra vez? (s/n) ").strip().lower()
        if again not in TRUE_TOKENS:
            break

if __name__ == "__main__":
    main()
