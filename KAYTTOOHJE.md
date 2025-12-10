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

### Vaihtoehto 2: Käytä molempia rinnakkain

Jos haluat pitää molemmat versiot, lisää molemmat `firebase.json`:

```json
{
  "functions": [
    {
      "source": "functions-python",
      "codebase": "python-scraper",
      "runtime": "python311"
    },
    {
      "source": "functions-python-simple",
      "codebase": "python-scraper-simple",
      "runtime": "python311"
    }
  ],
  ...
}
```

Tällöin saat kaksi funktiota:
- `scrape_website` (Scrapy-versio)
- `scrape_website_simple` (Yksinkertainen versio)

## React-sovelluksen muutokset

**EI TARVITA MUUTOKSIA!**

Funktio käyttää samaa nimeä (`scrape_website`) ja palauttaa saman datan, joten React-sovellus toimii ilman muutoksia.

Jos käytät vaihtoehtoa 2 (molemmat rinnakkain), voit vaihtaa React-koodissa:

```typescript
// services/siteScraperService.ts
const scrapeWebsite = httpsCallable<{ url: string }, ScrapedData>(
  functions, 
  'scrape_website_simple'  // Vaihda tähän jos käytät molempia
);
```

## Testaus paikallisesti

```bash
cd functions-python-simple
python -m venv venv
venv\Scripts\activate  # Windows PowerShell
pip install -r requirements.txt
python test_scraper.py https://www.sissipuukko.fi/
```

## Erot Scrapy-versioon

### Edut:
- ✅ Toimii useilla peräkkäisillä kutsuilla
- ✅ Nopeampi käynnistysaika
- ✅ Yksinkertaisempi koodi
- ✅ Vähemmän riippuvuuksia

### Haitat:
- ❌ Ei tue JavaScript-renderöintiä (ei SPA-sivustoja)
- ❌ Ei tue monisivuisia crawleja
- ❌ Ei middleware-tukea

## Kumpi versio kannattaa käyttää?

**Käytä yksinkertaista versiota jos:**
- Scrapaat perinteisiä HTML-sivustoja
- Tarvitset vain yhden sivun scrapingin
- Haluat varmistaa että se toimii useilla kutsuilla

**Käytä Scrapy-versiota jos:**
- Tarvitset monisivuisia crawleja
- Tarvitset middleware-tukea
- Haluat käyttää Scrapyn pipelineja

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

