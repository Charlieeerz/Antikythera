#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génère toutes les combinaisons ON/OFF des calques d'un SVG et exporte en PNG.
- Détecte les calques Inkscape (g inkscape:groupmode="layer")
- On peut fournir une liste de 6 calques à utiliser (order important)
- Exporte 2^n images en nommant les fichiers par bitmask (ex: 010101.png)
"""

import argparse
import os
from itertools import product
from lxml import etree
import cairosvg
from tqdm import tqdm

INKSCAPE_NS = "http://www.inkscape.org/namespaces/inkscape"
SVG_NS = "http://www.w3.org/2000/svg"
NSMAP = {"svg": SVG_NS, "inkscape": INKSCAPE_NS}

def parse_args():
    p = argparse.ArgumentParser(description="Export toutes les combinaisons de calques d'un SVG en PNG.")
    p.add_argument("input_svg", help="Chemin du fichier SVG source")
    p.add_argument("output_dir", help="Dossier de sortie pour les PNG")
    p.add_argument("--layers", nargs="+", default=None,
                   help="Noms (label) des calques à combiner, dans l'ordre (6 noms). "
                        "Si omis : utilise les 6 premiers calques détectés.")
    p.add_argument("--dpi", type=int, default=300, help="DPI d'export PNG (défaut 300)")
    p.add_argument("--scale", type=float, default=1.0, help="Facteur d'échelle optionnel (1.0 = taille originale)")
    p.add_argument("--prefix", default="", help="Préfixe des fichiers de sortie (ex: v_)")
    p.add_argument("--keep_style", action="store_true",
                   help="Conserver le style original et seulement surcharger display. "
                        "Par défaut, réécrit display proprement.")
    return p.parse_args()

def load_svg(path):
    parser = etree.XMLParser(remove_comments=False, strip_cdata=False)
    with open(path, "rb") as f:
        return etree.parse(f, parser)

def find_layers(tree):
    # Calques Inkscape: <g inkscape:groupmode="layer" inkscape:label="...">
    return tree.findall(".//svg:g[@inkscape:groupmode='layer']", namespaces=NSMAP)

def set_layer_visibility(elem, visible, keep_style=False):
    # On force display: inline (visible) ou display: none (caché)
    disp = "inline" if visible else "none"

    # Certains SVG mettent la visibilité via l'attribut 'display' ou dans 'style'
    if not keep_style:
        # Nettoyage: fixe display dans l'attribut 'style' (créé ou modifié)
        style = elem.get("style", "")
        # retire anciens 'display:...' s'il y en a
        parts = [s.strip() for s in style.split(";") if s.strip() and not s.strip().startswith("display:")]
        parts.append(f"display:{disp}")
        elem.set("style", ";".join(parts))
        # Supprime l'attribut display direct si présent, pour éviter les conflits
        if "display" in elem.attrib:
            del elem.attrib["display"]
    else:
        # Conserver le style tel quel et juste poser/écraser l'attribut display
        elem.set("display", disp)

def svg_to_png_bytes(svg_tree, dpi=300, scale=1.0):
    # Sérialise le SVG actuel
    svg_bytes = etree.tostring(svg_tree, encoding="utf-8", xml_declaration=True)
    # Export PNG
    return cairosvg.svg2png(bytestring=svg_bytes, dpi=dpi, scale=scale)

def main():
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)
    base_tree = load_svg(args.input_svg)

    all_layers = find_layers(base_tree)
    if len(all_layers) < 6 and (not args.layers):
        raise SystemExit(f"On n'a trouvé que {len(all_layers)} calques Inkscape, il en faut 6.")

    # Crée un mapping label -> element
    by_label = {}
    for g in all_layers:
        label = g.get(f"{{{INKSCAPE_NS}}}label") or g.get("id") or ""
        by_label[label] = g

    # Détermine les 6 calques à utiliser (et leur ordre)
    if args.layers:
        chosen_labels = args.layers
        if len(chosen_labels) != 6:
            raise SystemExit("Veuillez fournir exactement 6 noms de calque avec --layers.")
        missing = [x for x in chosen_labels if x not in by_label]
        if missing:
            raise SystemExit(f"Calques introuvables: {missing}\nCalques disponibles: {list(by_label.keys())}")
        chosen = [by_label[l] for l in chosen_labels]
    else:
        # Prend les 6 premiers calques détectés dans l'ordre du document
        chosen = all_layers[:6]
        chosen_labels = [(g.get(f"{{{INKSCAPE_NS}}}label") or g.get('id') or f"Layer{i}") for i, g in enumerate(chosen)]

    print("Calques choisis (ordre des bits, MSB->LSB):")
    for i, lab in enumerate(chosen_labels):
        print(f"  {i}: {lab}")

    # Pour chaque combinaison binaire sur 6 bits (0/1 = OFF/ON)
    n = 6
    combos = list(product([0,1], repeat=n))
    for combo in tqdm(combos, desc="Export PNG", unit="img"):
        # Crée une copie fraîche du SVG pour éviter accumulation de styles
        tree = load_svg(args.input_svg)
        layers_current = find_layers(tree)

        # Reconstitue le mapping label -> element sur cette copie
        current_by_label = {}
        for g in layers_current:
            lab = g.get(f"{{{INKSCAPE_NS}}}label") or g.get("id") or ""
            current_by_label[lab] = g

        # Applique visibilité selon combo
        for idx, lab in enumerate(chosen_labels):
            visible = bool(combo[idx])
            elem = current_by_label.get(lab)
            if elem is None:
                raise SystemExit(f"Calque '{lab}' manquant dans la copie du document.")
            set_layer_visibility(elem, visible, keep_style=args.keep_style)

        # Nom de fichier: bitmask MSB->LSB (ex: 101100.png)
        bitmask = "".join(str(b) for b in combo)
        out_name = f"{args.prefix}{bitmask}.png"
        out_path = os.path.join(args.output_dir, out_name)

        png_bytes = svg_to_png_bytes(tree, dpi=args.dpi, scale=args.scale)
        with open(out_path, "wb") as f:
            f.write(png_bytes)


   #print(f"Export terminé: {count} images dans '{args.output_dir}'.")

if __name__ == "__main__":
    main()
