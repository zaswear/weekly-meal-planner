#!/usr/bin/env python3
"""
Convierte los libros de recetas en markdown a recetas.json
Fuentes: Arguiñano (1069 recetas) + El Comidista (202 mejores recetas)
"""

import re
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
RECETAS_DIR = os.path.join(BASE, "recetas")


# ──────────────────────────────────────────────
#  UTILIDADES
# ──────────────────────────────────────────────

def normalize(text):
    """Colapsa espacios y tabs múltiples, elimina artefactos de conversión."""
    text = re.sub(r'\t+', ' ', text)
    text = re.sub(r'  +', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def split_ingredient(raw):
    """
    Separa cantidad de nombre en un ingrediente.
    Ej: '200 g de harina' → {'qty': '200 g', 'name': 'harina'}
    """
    raw = raw.strip().lstrip('•–-').strip()
    if not raw:
        return None

    qty_re = re.compile(
        r'^([\d½¼¾⅓⅔]+[\d\s\/\.,-]*'
        r'(?:g|kg|ml|cl|l|cdas?\.?|cucharad(?:as?|itas?)?\.?|cdtas?\.?'
        r'|tazas?|vasos?|lonchas?|rodajas?|dientes?|ramas?|hojas?|pizca(?:s)?'
        r'|puñad(?:o|os)|manojo(?:s)?|unidades?|uds?\.?|ud\.?'
        r'|rebanadas?|filetes?|porciones?|sobres?|latas?|botes?'
        r'|\%)?\s*(?:de\s+)?)',
        re.IGNORECASE
    )
    m = qty_re.match(raw)
    if m and m.group(0).strip():
        qty = m.group(0).strip()
        name = raw[m.end():].strip()
        if name:
            return {'qty': qty, 'name': name}

    return {'qty': '', 'name': raw}


def parse_steps_numbered(text):
    """Extrae pasos numerados: '1. Paso...' o '1.- Paso...'"""
    steps = re.split(r'\n\s*\d+[.\-]\s+', '\n' + text.strip())
    steps = [s.replace('\n', ' ').strip() for s in steps if s.strip()]
    return steps


def parse_steps_paragraph(text):
    """Divide texto de elaboración en párrafos como pasos."""
    paras = re.split(r'\n{1,2}', text.strip())
    steps = []
    for p in paras:
        p = p.replace('\n', ' ').strip()
        if p and len(p) > 10 and not re.match(r'^\d+\s*$', p):
            steps.append(p)
    return steps if steps else [text.replace('\n', ' ').strip()]


# ──────────────────────────────────────────────
#  PARSER: Arguiñano
#  Patrón: "N – NOMBRE\nIngredientes:\n...\nElaboración:\n..."
# ──────────────────────────────────────────────

def parse_arguinano(filepath):
    with open(filepath, encoding='utf-8') as f:
        raw = f.read()

    text = normalize(raw)
    recipes = []

    # Dividir en bloques por "N – NOMBRE"
    blocks = re.split(r'\n(?=\d+[\.\s]*[–—-]\s+[A-ZÁÉÍÓÚÜÑ])', text)

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        # Título: "26 – AGUACATES RELLENOS..."
        title_m = re.match(r'^[\d\.\s]+[–—-]\s+(.+)', block)
        if not title_m:
            continue
        name = title_m.group(1).strip()

        # Ingredientes
        ing_m = re.search(r'Ingredientes?:\s*\n(.*?)(?=\nElaboraci[oó]n:|\Z)', block, re.DOTALL | re.IGNORECASE)
        if not ing_m:
            continue

        ing_raw = ing_m.group(1)
        # Los ingredientes de Arguiñano a veces están en una línea separados por espacios
        # o cada uno en su línea
        ing_lines = []
        for line in ing_raw.split('\n'):
            line = line.strip()
            if not line or re.match(r'^\d+\s*$', line):
                continue
            # Si la línea parece contener varios ingredientes (sin separador claro), tratar como párrafo
            ing_lines.append(line)

        # Combinar en un solo texto y re-tokenizar por unidades de medida
        ing_text = ' '.join(ing_lines)
        # Intentar dividir por patrón de cantidad al inicio
        raw_ings = re.split(
            r'(?<=[a-záéíóúüñA-ZÁÉÍÓÚÜÑ\)\.])\s+(?=\d|una? |dos |tres |cuatro |½|¼|¾)',
            ing_text
        )
        ingredients = []
        for ri in raw_ings:
            parsed = split_ingredient(ri)
            if parsed and parsed['name']:
                ingredients.append(parsed)

        # Elaboración
        elab_m = re.search(r'Elaboraci[oó]n:\s*\n(.*?)(?=\n\n\d+[\.\s]*[–—-]|\Z)', block, re.DOTALL | re.IGNORECASE)
        if not elab_m:
            continue
        elab_text = elab_m.group(1).strip()

        # ¿tiene pasos numerados?
        if re.search(r'\n\s*\d+[.\-]\s+', elab_text):
            steps = parse_steps_numbered(elab_text)
        else:
            steps = parse_steps_paragraph(elab_text)

        if not ingredients or not steps:
            continue

        recipes.append({
            'name': name.title(),
            'ingredients': ingredients,
            'steps': steps,
            'tip': '',
        })

    return recipes


# ──────────────────────────────────────────────
#  PARSER: El Comidista (202 mejores recetas)
#  Patrón: "Nombre\n\nINGREDIENTES\n• ...\nPREPARACIÓN\n1. ..."
# ──────────────────────────────────────────────

def parse_comidista_202(filepath):
    with open(filepath, encoding='utf-8') as f:
        raw = f.read()

    text = normalize(raw)
    recipes = []

    # Cada receta termina justo antes de la siguiente o al final
    pattern = re.compile(
        r'^(.+?)\n\nINGREDIENTES\n\n(.*?)\nPREPARACIÓN\n\n(.*?)(?=\n\n.+?\n\nINGREDIENTES|\Z)',
        re.DOTALL | re.MULTILINE
    )

    for i, m in enumerate(pattern.finditer(text)):
        name_block = m.group(1).strip()
        ing_block  = m.group(2).strip()
        prep_block = m.group(3).strip()

        # Tomar solo la última línea del bloque de nombre
        # (puede haber texto de receta anterior antes del título)
        name = name_block.split('\n')[-1].strip()

        # Filtrar nombres de páginas o secciones
        if re.match(r'^P[aá]gina\s+\d+$', name, re.IGNORECASE):
            continue
        if len(name) < 4 or name.isupper() and len(name) < 10:
            continue

        # Ingredientes: líneas con •
        ing_lines = [l for l in ing_block.split('\n') if l.strip().startswith('•')]
        if not ing_lines:
            continue

        ingredients = []
        for line in ing_lines:
            parsed = split_ingredient(line)
            if parsed and parsed['name']:
                ingredients.append(parsed)

        # Pasos numerados
        steps = parse_steps_numbered(prep_block)
        if not steps:
            steps = parse_steps_paragraph(prep_block)

        # Consejo (Plan B)
        tip_m = re.search(r'Plan\s+B\s*\n+(.+?)(?=\n\n|\Z)', prep_block, re.DOTALL)
        tip = tip_m.group(1).replace('\n', ' ').strip() if tip_m else ''

        if not ingredients or not steps:
            continue

        recipes.append({
            'name': name,
            'ingredients': ingredients,
            'steps': steps,
            'tip': tip,
        })

    return recipes


# ──────────────────────────────────────────────
#  PARSER: El Comidista (La cocina pop)
#  Similar al anterior
# ──────────────────────────────────────────────

def parse_comidista_pop(filepath):
    # Mismo patrón que 202 mejores
    return parse_comidista_202(filepath)


# ──────────────────────────────────────────────
#  MAIN
# ──────────────────────────────────────────────

def main():
    all_recipes = []

    sources = [
        (parse_arguinano,     "LIBRO DE ARGUIÑANO AL COMPLETO 1069 RECETAS.md"),
        (parse_comidista_202, "Las 202 mejores recetas de El Comidista.md"),
        (parse_comidista_pop, "La cocina pop de El Comidista.md"),
        (parse_comidista_pop, "Las recetas de El Comidista.md"),
    ]

    for parser_fn, filename in sources:
        filepath = os.path.join(RECETAS_DIR, filename)
        if not os.path.exists(filepath):
            print(f"  [SKIP] {filename} — no encontrado")
            continue
        try:
            recipes = parser_fn(filepath)
            print(f"  [OK]  {filename}: {len(recipes)} recetas")
            all_recipes.extend(recipes)
        except Exception as e:
            print(f"  [ERR] {filename}: {e}")

    # Deduplicar por nombre (insensible a mayúsculas)
    seen = set()
    unique = []
    for r in all_recipes:
        key = r['name'].lower().strip()
        if key not in seen and len(r['ingredients']) >= 2 and len(r['steps']) >= 1:
            seen.add(key)
            unique.append(r)

    # Asignar IDs
    for i, r in enumerate(unique):
        r['id'] = f'r{i+1:04d}'

    output_path = os.path.join(BASE, "recetas.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(unique, f, ensure_ascii=False, indent=2)

    print(f"\n✓ {len(unique)} recetas únicas → recetas.json")


if __name__ == '__main__':
    main()
