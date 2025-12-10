# Käyttöohje - Yksinkertainen Scraper

## Miten vaihtaa Scrapy-versiosta tähän?

### Vaihtoehto 1: Vaihda firebase.json (Suositeltu)

Päivitä `firebase.json` tiedosto projektin juuressa:

```json
{
  "functions": [
    {
      "source": "functions-python-simple",
      "codebase": "python-scraper-simple",
      "runtime": "python311"
    }
  ],
  "firestore": {
    "rules": "firestore.rules"
  },
  "hosting": {
    "public": "dist",
    "ignore": [
      "firebase.json",
      "**/.*",
      "**/node_modules/**"
    ],
    "rewrites": [
      {
        "source": "**",
        "destination": "/index.html"
      }
    ]
  }
}
```

Sitten deployaa:
```bash
firebase deploy --only functions
```

## Testaus paikallisesti

```bash
cd functions-python-simple
python -m venv venv
venv\Scripts\activate  # Windows PowerShell
pip install -r requirements.txt
python test_scraper.py https://www.sissipuukko.fi/
```

## Ongelmatilanteet

### "ModuleNotFoundError: No module named 'requests'"
Ratkaisu: Asenna riippuvuudet
```bash
cd functions-python-simple
pip install -r requirements.txt
```

### "Function not found"
Ratkaisu: Varmista että deployasit oikean version
```bash
firebase deploy --only functions
```

### "Timeout error"
Ratkaisu: Sivusto voi olla hidas. Tarkista Firebase Functions -logit:
```bash
firebase functions:log
```

