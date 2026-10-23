# PixelForge — Creative Studio

PixelForge is a creative productivity toolkit for designers, video editors, musicians, and developers. Organize projects, generate color palettes, export CSS variables, check color contrast, and brainstorm visual prompt ideas.

## Features
- Creative project library with categories, tags, and search
- HEX palettes: analogous, complementary, triadic, sunset, and monochrome
- Save projects and palettes in a local JSON library
- Export palettes as CSS custom properties
- WCAG AA text/background contrast checker
- Random art prompt idea generator
- Automated unit tests

## Requirements
Python 3.9 or newer. No external packages required.

## Run
```bash
python pixelforge.py
```
Use `python3 pixelforge.py` if needed. The library JSON is created when you save your first item.

## Tests
```bash
python -m unittest discover -s tests -v
```

## Project structure
```text
PixelForge-Creative-Studio/
├── pixelforge.py
├── tests/test_pixelforge.py
├── README.md
├── LICENSE
└── .gitignore
```

## Privacy
Your library is stored locally in `creative_library.json`. Avoid committing private project notes to a public repository.

## License
MIT License. See `LICENSE`.
