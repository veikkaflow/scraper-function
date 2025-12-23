# Testi scraper, flowbotin käytössä
## Rakenne

```
functions-python-simple/
├── main.py              # Pääfunktio joka scrapaa sivuston
├── requirements.txt     # Python-riippuvuudet
└── README.md           # Tämä tiedosto
```

## Miten se toimii?

1. **HTTP-pyyntö saapuu** → `scrape_website` funktio
2. **URL validoidaan** → Tarkistetaan että URL on validi
3. **Sivusto haetaan** → `requests.get()` hakee HTML-sisällön
4. **HTML parsitaan** → `BeautifulSoup` parsii HTML:n
5. **Data poimitaan**:
   - **Title**: `<title>` tagista
   - **Text**: Pääsisällöstä (`main`, `article`, `.content`, `#content`, tai `body`)
   - **Logos**: Logo-kuvista ja faviconeista
   - **Colors**: CSS-väreistä (`style`-attribuuteista ja `<style>`-tageista)
6. **Data palautetaan** → Sama muoto kuin Scrapy-versio

## Deployaus

```bash
# 1. Varmista että olet projektin juuressa
cd "C:\Users\Veikka\OneDrive\Desktop\flowbot 1.12"

# 2. Deployaa funktio
firebase deploy --only functions:scrape_website_simple
```

Jos haluat käyttää tätä versiota, päivitä `firebase.json`:

```json
{
  "functions": [
    {
      "source": "functions-python-simple",
      "codebase": "python-scraper-simple",
      "runtime": "python311"
    }
  ]
}
```

Ja deployaa:
```bash
firebase deploy --only functions
```

## Testaus

Voit testata funktiota paikallisesti:

```bash
cd functions-python-simple
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python -c "from main import scrape_website; print(scrape_website('https://example.com'))"
```

