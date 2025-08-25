import pytesseract
from PIL import Image
import re
import json
from pathlib import Path
import pandas as pd

# Adjust to your actual install path if different:
pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"

UNIT_PAT = r'(?P<unit>zakje|blokje|teentje|g|kg|ml|l|tl|el|stuk|stuks?)'
QUANTITY_PAT = r'(?P<quantity>\d+[\d\/\.]*)'

def extract_text(image_path: Path, lang: str = 'nld') -> str:
    """Run OCR on an image and return raw text."""
    img = Image.open(image_path)
    raw = pytesseract.image_to_string(img, lang=lang)
    return raw

def split_sections(text: str) -> dict:
    """
    Very naive section splitter: attempts to separate ingredients (before
    instruction-like keywords) and instructions (after).
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    title_lines = []
    ingredients_main = []
    extras = []
    instructions = []
    
    # lowercased helpers
    lowered = [l.lower() for l in lines]
    try:
        idx_ing = next(i for i, l in enumerate(lowered) if 'ingrediënten' in l or "ingredienten" in l)
    except StopIteration:
        idx_ing = None

    try:
        idx_extra = next(i for i, l in enumerate(lowered) if 'uit jouw keuken' in l)
    except StopIteration:
        idx_extra = None    
    
    # instructions start after these keywords
    instr_keywords = ('consumeert.', 'gebruiksaanwijzing')

    # determine title
    if idx_ing is not None:
        title_lines = lines[:idx_ing]
    else:
        # fallback: take first 2 lines as title
        title_lines = lines[:2]

    # collect ingredients_main and extras
    if idx_ing is not None:
        if idx_extra is not None and idx_extra > idx_ing:
            ingredients_main = lines[idx_ing + 1 : idx_extra]
            # extras go from after 'uit jouw keuken' up until instructions begin
            after_extra = lines[idx_extra + 1 :]
        else:
            # no extras section marker; treat everything after ingredientes as main, no extras
            ingredients_main = lines[idx_ing + 1 :]
            after_extra = []
    else:
        # if no "Ingrediënten" marker, try heuristic: until instructions
        if idx_extra is not None:
            ingredients_main = lines[:idx_extra]
            after_extra = lines[idx_extra + 1 :]
        else:
            ingredients_main = lines[:]
            after_extra = []

    # seperate instructions for remaining trailing lines
    # scan after_extra and any remainder for instruction section
    remaining = after_extra if after_extra else []
    instr_start = False
    for line in remaining:
        lower = line.lower()
        if any(k in lower for k in instr_keywords):
            instr_start = True
            continue
        if instr_start:
            instructions.append(line)
        else:
            extras.append(line)

    return {
        "title": ' '.join(title_lines).strip(),
        "ingredients_main": ingredients_main, # with quantity + unit
        "extras": extras, # just items
        "instructions_raw": instructions
    }

def parse_ingredient(line: str) -> dict:
    """
    Parse a main ingredient line expected in form: item quantity unit
    Fallbacks accommodate other orders or missing pieces.
    """
    original = line.strip()
    lower = original.lower()

    # 1. Try: item + quantity + unit  (e.g., "bloem 200 g")
    pattern_item_qty_unit = rf'^(.+?)\s+{QUANTITY_PAT}\s*{UNIT_PAT}\s*$'
    m = re.match(pattern_item_qty_unit, lower, flags=re.IGNORECASE)
    if m:
        return {
            "quantity": m.group("quantity") or "",
            "unit": m.group("unit") or "",
            "item": m.group(1).strip()
        }

    # 2. Fallback: just item (no quantity/unit)
    return {"quantity": "", "unit": "", "item": original}

def build_recipe(image_path: Path, lang: str = 'nld') -> dict:
    """Extract, split and parse a recipe from a single image."""
    raw_text = extract_text(image_path, lang=lang)
    sections = split_sections(raw_text)
    parsed_main = [parse_ingredient(i) for i in sections["ingredients_main"]]
    parsed_extras = [{"quantity": "", "unit": "", "item": e} for e in sections["extras"]]
    recipe = {
        "source_image": str(image_path),
        "title": sections.get("title", ""),
        "ingredients": parsed_main + parsed_extras,
        "instructions": sections.get("instructions_raw", []),
        "raw_text": raw_text
    }
    return recipe

def main():
    # Resolve based on script location: project root is parent of parent of this file if in src/
    base_dir = Path(__file__).resolve().parent.parent
    data_dir = base_dir / "data"
    output_dir = base_dir / "extracted"
    output_dir.mkdir(exist_ok=True)

    # Choose language; could later be parameterized
    lang = 'nld'

    for img_path in sorted(data_dir.iterdir()):
        if img_path.suffix.lower() not in (".jpg", ".jpeg", ".png", ".tiff"):
            continue
        print(f"Processing {img_path.name} ...")
        recipe = build_recipe(img_path, lang=lang)
        out_file = output_dir / f"{img_path.stem}.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(recipe, f, ensure_ascii=False, indent=2)
        print(f"  Saved parsed recipe to {out_file.name}")

if __name__ == "__main__":
    main()

records = []
for f in Path("../extracted").glob("*.json"):
    r = json.load(open(f, encoding="utf-8"))
    for ing in r["ingredients"]:
        records.append({
            "source_image": r["source_image"],
            "title": r["title"],
            "quantity": ing["quantity"],
            "unit": ing["unit"],
            "item": ing["item"],
            "instructions": " | ".join(r["instructions"])
        })
df = pd.DataFrame(records)
df.to_csv("../extracted/recipes_flat.csv", index=False)






# Load one image from the data folder
image_path = "..\\data\\mediterraanse_risotto.jpg"
img = Image.open(image_path)

# Run OCR
text = pytesseract.image_to_string(img, lang='nld')

print("Extracted text: ")
print(text)