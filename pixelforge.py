"""PixelForge: a creative studio toolkit for project ideas and color palettes."""
import argparse
import colorsys
import json
import re
import secrets
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LIBRARY = ROOT / "creative_library.json"


def load_library(path=LIBRARY):
    path = Path(path)
    if not path.exists():
        return {"projects": [], "palettes": []}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("projects"), list) or not isinstance(data.get("palettes"), list):
        raise ValueError("Invalid creative library format.")
    return data


def save_library(data, path=LIBRARY):
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def slugify(value):
    return re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-") or "untitled"


def add_project(library, name, category, description="", tags=""):
    if not name.strip() or not category.strip():
        raise ValueError("Project name and category are required.")
    item = {"id": max((p.get("id", 0) for p in library["projects"]), default=0) + 1,
            "name": name.strip(), "slug": slugify(name), "category": category.strip(),
            "description": description.strip(),
            "tags": [t.strip() for t in tags.split(",") if t.strip()],
            "created_at": datetime.now().isoformat(timespec="seconds")}
    library["projects"].append(item)
    return item


def search_projects(library, query="", category=""):
    q, c = query.casefold().strip(), category.casefold().strip()
    return [p for p in library["projects"]
            if (not q or q in " ".join([p.get("name", ""), p.get("category", ""), p.get("description", ""), *p.get("tags", [])]).casefold())
            and (not c or c in p.get("category", "").casefold())]


def hex_to_rgb(value):
    value = value.strip().lstrip("#")
    if not re.fullmatch(r"[0-9a-fA-F]{6}", value):
        raise ValueError("Use a six-digit HEX color, such as #6750A4.")
    return tuple(int(value[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#{:02X}{:02X}{:02X}".format(*(max(0, min(255, round(v))) for v in rgb))


def generate_palette(seed, count=5, scheme="analogous"):
    if not 2 <= count <= 12:
        raise ValueError("Palette size must be between 2 and 12.")
    r, g, b = (v / 255 for v in hex_to_rgb(seed))
    h, light, sat = colorsys.rgb_to_hls(r, g, b)
    offsets = {"analogous": [-1/12, 0, 1/12], "complementary": [0, .5],
               "triadic": [0, 1/3, 2/3], "sunset": [-.04, 0, .04, .08, .12]}
    if scheme == "monochrome":
        return [rgb_to_hex(tuple(v * 255 for v in colorsys.hls_to_rgb(h, .2 + .6*i/(count-1), sat))) for i in range(count)]
    if scheme not in offsets:
        raise ValueError("Scheme: analogous, complementary, triadic, sunset, or monochrome.")
    palette = []
    for i in range(count):
        off = offsets[scheme][i % len(offsets[scheme])]
        cycle = i // len(offsets[scheme])
        new_light = max(.18, min(.82, light + (cycle - count // len(offsets[scheme]) / 2) * .12))
        new_sat = max(.35, sat)
        palette.append(rgb_to_hex(tuple(v * 255 for v in colorsys.hls_to_rgb((h + off) % 1, new_light, new_sat))))
    return palette


def contrast_ratio(foreground, background):
    def lum(color):
        channels = []
        for v in hex_to_rgb(color):
            x = v / 255
            channels.append(x / 12.92 if x <= .04045 else ((x + .055) / 1.055) ** 2.4)
        return .2126*channels[0] + .7152*channels[1] + .0722*channels[2]
    a, b = sorted((lum(foreground), lum(background)), reverse=True)
    return (a + .05) / (b + .05)


def save_palette(library, name, colors, scheme):
    if not name.strip():
        raise ValueError("Palette name cannot be empty.")
    item = {"id": max((p.get("id", 0) for p in library["palettes"]), default=0) + 1,
            "name": name.strip(), "colors": colors, "scheme": scheme,
            "created_at": datetime.now().isoformat(timespec="seconds")}
    library["palettes"].append(item)
    return item


def export_css(palette, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [":root {"] + [f"  --color-{i}: {color};" for i, color in enumerate(palette["colors"], 1)] + ["}", ""]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def generate_prompt():
    rng = secrets.SystemRandom()
    subjects = ["a futuristic music studio", "a mythical Bengal tiger", "a neon rainy street", "an enchanted forest", "a floating cyberpunk city", "a dreamlike ocean temple", "a tiny robot gardener"]
    styles = ["cinematic 3D render", "retro-futurist poster", "minimal vector illustration", "surreal album-cover art", "watercolor concept art", "low-poly diorama", "bold geometric graphic design"]
    moods = ["nostalgic", "mysterious", "hopeful", "energetic", "peaceful", "dramatic"]
    lights = ["volumetric lighting", "golden-hour glow", "electric neon rim light", "moody chiaroscuro", "iridescent reflections"]
    frames = ["wide cinematic composition", "clean negative space for typography", "isometric composition", "dynamic diagonal framing", "centered symmetrical composition"]
    return f"{rng.choice(styles)} of {rng.choice(subjects)}, {rng.choice(moods)} mood, {rng.choice(lights)}, {rng.choice(frames)}, polished art direction"


def menu():
    data = load_library()
    while True:
        print("\n====== PIXELFORGE CREATIVE STUDIO ======")
        print("1 Add creative project | 2 Search projects | 3 Generate palette")
        print("4 View saved palettes | 5 Export palette CSS | 6 Art prompt idea")
        print("7 Check color contrast | 0 Exit")
        choice = input("Choose: ").strip()
        try:
            if choice == "1":
                p = add_project(data, input("Project name: "), input("Category: "), input("Description: "), input("Tags (comma-separated): "))
                save_library(data); print(f"Saved project #{p['id']} ({p['slug']}).")
            elif choice == "2":
                results = search_projects(data, input("Search (blank = all): "), input("Category filter (blank = any): "))
                if not results: print("No matching projects.")
                for p in results: print(f"#{p['id']} {p['name']} [{p['category']}] — {p['description']} | Tags: {', '.join(p['tags'])}")
            elif choice == "3":
                seed = input("Seed HEX [#6750A4]: ").strip() or "#6750A4"
                scheme = input("Scheme [analogous/complementary/triadic/sunset/monochrome]: ").strip().lower() or "analogous"
                count = int(input("Number of colors [5]: ").strip() or "5")
                colors = generate_palette(seed, count, scheme)
                for color in colors: print(f"  {color}  RGB {hex_to_rgb(color)}")
                name = input("Save palette name (blank to skip): ").strip()
                if name: save_palette(data, name, colors, scheme); save_library(data); print("Palette saved.")
            elif choice == "4":
                if not data["palettes"]: print("No saved palettes yet.")
                for p in data["palettes"]: print(f"#{p['id']} {p['name']} ({p['scheme']}): {' '.join(p['colors'])}")
            elif choice == "5":
                for p in data["palettes"]: print(f"#{p['id']} {p['name']}: {' '.join(p['colors'])}")
                pid = int(input("Palette ID: "))
                p = next((x for x in data["palettes"] if x["id"] == pid), None)
                if p: export_css(p, input("CSS path [palette.css]: ").strip() or "palette.css"); print("CSS exported.")
                else: print("Palette not found.")
            elif choice == "6": print("\n" + generate_prompt())
            elif choice == "7":
                ratio = contrast_ratio(input("Text HEX: "), input("Background HEX: "))
                print(f"Contrast: {ratio:.2f}:1 | WCAG AA normal text: {'PASS' if ratio >= 4.5 else 'FAIL'} | large text: {'PASS' if ratio >= 3 else 'FAIL'}")
            elif choice == "0": print("Keep creating!"); break
            else: print("Choose a valid option.")
        except (ValueError, OSError, json.JSONDecodeError) as exc: print("Error:", exc)

if __name__ == "__main__":
    argparse.ArgumentParser(description="PixelForge creative studio").parse_args()
    menu()
