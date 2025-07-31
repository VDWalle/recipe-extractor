# Recipe Extractor

A Python-based tool to create a structured recipe database by extracting text (ingredients, instructions, etc.) from photos of a cookbook using OCR.

---

## 📂 Project Structure

recipe-extractor/
├── data/ # Input images (cookbook photos)
├── extracted/ # Output (parsed recipes, JSON/CSV)
├── src/ # Python scripts (OCR, parsing, saving)
├── README.md # Project overview and instructions
├── requirements.txt# Python dependencies
├── .gitignore # Files/folders to ignore in Git
└── .gitattributes # Normalize line endings for cross-platform use

## ⚙️ Setup

1. **Clone the repo**
```bash
git clone https://github.com/VDWalle/recipe-extractor.git
cd recipe-extractor
```

2. **Create and activate a virtual environment**
```bash
python -m venv venv
source venv/Scripts/activate       # Git Bash on Windows
# or: venv\Scripts\activate        # PowerShell on Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

## 🚀 Usage
Put cookbook photos into the data/ folder.

Run the OCR script (will be in src/) to extract recipes.

Processed recipes will appear in the extracted/ folder as JSON or CSV.

## 🛠 Development Notes
Update requirements.txt after installing new packages:

```bash
pip freeze > requirements.txt
```
The venv/ folder and any large output files are ignored by Git.

Line endings are normalized using .gitattributes for cross-platform consistency.