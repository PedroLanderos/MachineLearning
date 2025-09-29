#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
import os
import unicodedata

# === Esquema CSV (incluye 'apariciones') ===
CSV_COLUMNS = ["nombre", "color", "citrica", "tropical", "con_semillas", "se_pela", "dulce", "apariciones"]
BOOL_FIELDS = ["citrica", "tropical", "con_semillas", "se_pela", "dulce"]

# ===== Normalización / utilidades =====
TRUE_TOKENS = {"si", "s", "true", "1", "x", "y", "yes"}
FALSE_TOKENS = {"no", "n", "false", "0"}
BACK_TOKENS = {"regresar", "anterior", "atras", "back", "r", "a"}  # admite acentos vía to_lc

def strip_accents(text):
    if text is None:
        return None
    text = str(text)
    return "".join(ch for ch in unicodedata.normalize("NFD", text) if unicodedata.category(ch) != "Mn")

def to_lc(s):
    if s is None:
        return None
    return strip_accents(str(s).strip().lower())

def split_multivalue_cell(raw):
    if raw is None:
        return []
    s = str(raw).strip()
    if not s or s.lower() in {"none", "nan"}:
        return []
    for sep in ["|", ",", ";", "/"]:
        s = s.replace(sep, "|")
    return [p.strip() for p in s.split("|") if p.strip()]

def normalize_bool_token(s):
    if s is None:
        return None
    s = to_lc(s)
    if s in {"", "?"}:
        return None
    if s in TRUE_TOKENS:
        return True
    if s in FALSE_TOKENS:
        return False
    if s in {"true", "false"}:
        return s == "true"
    return None

def normalize_color_token(s):
    s = to_lc(s)
    return s if s else None

# ===== Representación: filas como sets + apariciones =====
def parse_row_to_sets(row_dict):
    out = {"nombre": to_lc(row_dict.get("nombre", ""))}

    # color
    color_parts = split_multivalue_cell(row_dict.get("color", ""))
    color_set = set()
    for p in color_parts:
        tok = normalize_color_token(p)
        if tok:
            color_set.add(tok)
    if "marron" in color_set:
        color_set.add("cafe")
    out["color"] = color_set

    # booleanos en sets
    for bf in BOOL_FIELDS:
        parts = split_multivalue_cell(row_dict.get(bf, ""))
        bset = set()
        for p in parts:
            b = normalize_bool_token(p)
            if b is True or b is False:
                bset.add(b)
        out[bf] = bset

    # apariciones (int, default 0)
    apar_raw = row_dict.get("apariciones", "0")
    try:
        apar = int(str(apar_raw).strip())
        if apar < 0:
            apar = 0
    except:
        apar = 0
    out["apariciones"] = apar
    return out

def merge_rows_sets(base, new):
    assert base["nombre"] == new["nombre"]
    merged = {"nombre": base["nombre"]}
    merged["color"] = set(base["color"]) | set(new["color"])
    if "marron" in merged["color"]:
        merged["color"].add("cafe")
    for bf in BOOL_FIELDS:
        merged[bf] = set(base[bf]) | set(new[bf])
    # para apariciones: sumamos (si tenías duplicados)
    merged["apariciones"] = int(base.get("apariciones", 0)) + int(new.get("apariciones", 0))
    return merged

def sets_to_csv_row(d):
    row = {"nombre": d["nombre"]}
    row["color"] = "|".join(sorted(d["color"])) if d["color"] else ""
    for bf in BOOL_FIELDS:
        bset = d[bf]
        row[bf] = "" if not bset else "|".join("True" if b else "False" for b in sorted(bset, key=lambda x: not x))
    row["apariciones"] = int(d.get("apariciones", 0))
    return row

# ===== IO CSV =====
def _ensure_columns(fieldnames):
    # Permitir CSV antiguos sin 'apariciones'
    if fieldnames == CSV_COLUMNS:
        return CSV_COLUMNS
    # si falta 'apariciones', la agregamos al guardar
    base = [c for c in CSV_COLUMNS if c != "apariciones"]
    if fieldnames == base:
        return fieldnames + ["apariciones"]
    raise ValueError(f"El CSV debe tener columnas {CSV_COLUMNS} o {base}. (tiene {fieldnames})")

def load_csv_as_sets(path):
    by_name = {}
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        _ = _ensure_columns(r.fieldnames)
        for row in r:
            if "apariciones" not in row:
                row["apariciones"] = "0"
            srow = parse_row_to_sets(row)
            name = srow["nombre"]
            if name in by_name:
                by_name[name] = merge_rows_sets(by_name[name], srow)
            else:
                by_name[name] = srow
    return list(by_name.values())

def save_sets_to_csv(path, rows_sets):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        w.writeheader()
        for d in sorted(rows_sets, key=lambda x: x["nombre"]):
            if "apariciones" not in d:
                d["apariciones"] = 0
            w.writerow(sets_to_csv_row(d))

def append_or_merge(path, row_sets):
    db = load_csv_as_sets(path)
    idx = {r["nombre"]: i for i, r in enumerate(db)}
    if row_sets["nombre"] in idx:
        db[idx[row_sets["nombre"]]] = merge_rows_sets(db[idx[row_sets["nombre"]]], row_sets)
    else:
        if "apariciones" not in row_sets:
            row_sets["apariciones"] = 0
        db.append(row_sets)
    save_sets_to_csv(path, db)

# ===== Preguntas (orden fijo) con opción de regresar =====
def parse_sn(s):
    s = to_lc(s)
    if s in BACK_TOKENS:
        return "__BACK__"
    if s in TRUE_TOKENS:
        return True
    if s in FALSE_TOKENS:
        return False
    if s in {"", "?"}:
        return None
    return None  # cualquier otra cosa se toma como desconocido

def ask_all_questions(db_rows_sets):
    """
    Pregunta en orden fijo con soporte de 'regresar/anterior/atras/back/r/a' para volver.
    Devuelve dict: {"color": str|None, booleanos ...}
    """
    known_colors = sorted({c for r in db_rows_sets for c in r["color"]})
    known_colors_txt = ", ".join(known_colors) if known_colors else "rojo, amarillo, verde, morado, naranja, rosa, marron, cafe, azul, negro"

    print("Responde con s / n / ? (desconocido). Escribe 'regresar' para volver a la pregunta anterior.")
    print(f"Para el color, escribe el color (o ?). Ej: {known_colors_txt}\n")

    # Orden de campos
    fields = ["color"] + BOOL_FIELDS
    prompts = {
        "color": "Color principal (minusculas, o '?' si no sabes): ",
        "citrica": "¿Es citrica? (s/n/?) ",
        "tropical": "¿Es tropical? (s/n/?) ",
        "con_semillas": "¿Tiene semillas? (s/n/?) ",
        "se_pela": "¿Se pela para comer? (s/n/?) ",
        "dulce": "¿Es dulce? (s/n/?) ",
    }

    answers = {"color": None, "citrica": None, "tropical": None, "con_semillas": None, "se_pela": None, "dulce": None}
    i = 0
    while 0 <= i < len(fields):
        f = fields[i]
        raw = to_lc(input(prompts[f]))

        # solicitud de volver
        if raw in BACK_TOKENS:
            if i == 0:
                print("Ya estas en la primera pregunta.\n")
            else:
                # limpiar respuesta previa y retroceder
                prev_f = fields[i - 1]
                answers[prev_f] = None
                i -= 1
            continue

        if f == "color":
            if raw in {"", "?"}:
                answers["color"] = None
                i += 1
                continue
            # normalizamos color
            color = normalize_color_token(raw)
            answers["color"] = color
            i += 1
        else:
            val = parse_sn(raw)
            if val == "__BACK__":
                if i == 0:
                    print("Ya estas en la primera pregunta.\n")
                else:
                    prev_f = fields[i - 1]
                    answers[prev_f] = None
                    i -= 1
                continue
            # almacena (True/False/None)
            answers[f] = val
            i += 1

    return answers

# ===== Matching =====
def matches_sets(candidate, answers):
    if answers.get("color") is not None:
        if not candidate["color"] or answers["color"] not in candidate["color"]:
            return False
    for bf in BOOL_FIELDS:
        a = answers.get(bf)
        if a is None:
            continue
        bset = candidate[bf]
        if not bset or a not in bset:
            return False
    return True

def filter_candidates(db_rows_sets, answers):
    return [c for c in db_rows_sets if matches_sets(c, answers)]

# ===== Aprendizaje (usa respuestas actuales) =====
def learning_mode_with_current_answers(csv_path, answers):
    print("\nNo acerte. Vamos a aprender esta fruta (solo necesito el nombre).")
    nombre = to_lc(input("Nombre: "))
    row_sets = {
        "nombre": nombre,
        "color": set([answers["color"]]) if answers.get("color") else set(),
        "apariciones": 0,  # nuevo
    }
    if "marron" in row_sets["color"]:
        row_sets["color"].add("cafe")
    for bf in BOOL_FIELDS:
        v = answers.get(bf)
        row_sets[bf] = set([v]) if v is True or v is False else set()
    append_or_merge(csv_path, row_sets)
    print(f"¡Gracias! Actualice/anadi '{nombre}' al CSV (fusion multivalor).")

# ===== Ranking por 'apariciones' y nombre =====
def rank_candidates_by_popularity(candidates):
    # más apariciones primero; empate -> nombre alfabético (asc)
    return sorted(candidates, key=lambda c: (-int(c.get("apariciones", 0)), c["nombre"]))

# ===== Actualizar apariciones =====
def update_single_aparicion(csv_path, nombre):
    """
    Sube en +1 'apariciones' para 'nombre' en el CSV.
    """
    db = load_csv_as_sets(csv_path)
    for r in db:
        if r["nombre"] == nombre:
            r["apariciones"] = int(r.get("apariciones", 0)) + 1
            break
    save_sets_to_csv(csv_path, db)

# ===== Juego =====
def play(csv_path):
    db = load_csv_as_sets(csv_path)

    print("Piensa en una FRUTA.")
    answers = ask_all_questions(db)

    candidates = filter_candidates(db, answers)
    if not candidates:
        learning_mode_with_current_answers(csv_path, answers)
        return False, 6

    ranked = rank_candidates_by_popularity(candidates)

    asked = 0
    for c in ranked:
        resp = to_lc(input(f"¿Es {c['nombre']}? (s/n) "))
        asked += 1
        if resp in TRUE_TOKENS:
            print("¡Adivine!")
            # incrementar apariciones y guardar
            update_single_aparicion(csv_path, c["nombre"])
            return True, 6 + asked
        # si el usuario escribe algo distinto a s/n, simplemente pasa al siguiente

    # Si ninguno fue: aprender
    learning_mode_with_current_answers(csv_path, answers)
    return False, 6 + asked

# ===== Métricas =====
def row_sets_to_conservative_point(r):
    pt = {"nombre": r["nombre"], "color": None if len(r["color"]) != 1 else next(iter(r["color"]))}
    for bf in BOOL_FIELDS:
        bset = r[bf]
        pt[bf] = next(iter(bset)) if len(bset) == 1 else None
    return pt

def simulate_quality(csv_path):
    db = load_csv_as_sets(csv_path)
    if not db:
        print("Base vacia.")
        return
    total_q, hits = 0, 0
    for r in db:
        pt = row_sets_to_conservative_point(r)
        answers = {
            "color": pt["color"],
            "citrica": pt["citrica"],
            "tropical": pt["tropical"],
            "con_semillas": pt["con_semillas"],
            "se_pela": pt["se_pela"],
            "dulce": pt["dulce"],
        }
        candidates = filter_candidates(db, answers)
        ranked = rank_candidates_by_popularity(candidates)
        ok = False
        for k, cand in enumerate(ranked, start=1):
            if cand["nombre"] == r["nombre"]:
                ok = True
                total_q += 6 + k
                break
        if not ok:
            total_q += 6 + len(ranked)
        if ok:
            hits += 1
    avg_q = total_q / len(db)
    acc = 100.0 * hits / len(db)
    print(f"\nMETRICAS (popularidad primero) sobre {len(db)} frutas:")
    print(f"- Nº de preguntas promedio: {avg_q:.2f}")
    print(f"- % de acierto: {acc:.1f}%\n")

def main():
    parser = argparse.ArgumentParser(description="Akinator de frutas (multivalor + popularidad + orden fijo + regresar)")
    parser.add_argument("--csv", default="frutas_multivalor.csv", help="Ruta al CSV de frutas")
    parser.add_argument("--simular", action="store_true", help="Solo calcular metricas y salir")
    args = parser.parse_args()

    if not os.path.exists(args.csv):
        print(f"⚠ No se encontro {args.csv}. Crea el CSV o indica la ruta con --csv.")
        return

    if args.simular:
        simulate_quality(args.csv)
        return

    print("=== Akinator de Frutas (multivalor) ===")
    print(f"Usando base: {args.csv}")
    while True:
        ok, q = play(args.csv)
        again = to_lc(input("¿Otra vez? (s/n) "))
        if again not in TRUE_TOKENS:
            break

if __name__ == "__main__":
    main()
