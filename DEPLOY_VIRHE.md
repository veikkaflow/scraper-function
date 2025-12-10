# Deployausvirheen ratkaisu

## Ongelma

Firebase yrittää aktivoida `venv`-ympäristön joka ei ole olemassa:
```
Error: spawn "C:\Users\Veikka\OneDrive\Desktop\flowbot 1.12\functions-python-simple\venv\Scripts\activate.bat" ENOENT
```

## Ratkaisu

Firebase Functions Python **ei tarvitse** venv:ää deployauksessa. Firebase buildaa riippuvuudet automaattisesti `requirements.txt`:stä.

### Vaihtoehto 1: Poista venv-kansio (Suositeltu)

```powershell
cd functions-python-simple
Remove-Item -Recurse -Force venv -ErrorAction SilentlyContinue
```

Sitten deployaa:
```powershell
cd ..
firebase deploy --only functions
```

### Vaihtoehto 2: Luodaan oikea venv (Jos vaihtoehto 1 ei toimi)

```powershell
cd functions-python-simple
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
deactivate
cd ..
firebase deploy --only functions
```

### Vaihtoehto 3: Käytä samaa venv:ää kuin functions-python

```powershell
# Kopioi venv functions-python kansiosta (ei suositeltu, mutta voi toimia)
```

## Tarkista funktio

Varmista että funktio on oikein määritelty `main.py` tiedostossa:

```python
@https_fn.on_request()
def scrape_website(req: https_fn.Request) -> https_fn.Response:
    # ... funktio koodi ...
```

## Debuggaus

Jos deployaus ei toimi, kokeile:

1. **Tarkista että kaikki tiedostot ovat olemassa:**
   ```powershell
   cd functions-python-simple
   dir
   ```
   Pitäisi näkyä: `main.py`, `requirements.txt`, `.gcloudignore`

2. **Tarkista että funktio on oikein:**
   ```powershell
   python -c "from main import scrape_website; print('OK')"
   ```

3. **Deployaa debug-moodissa:**
   ```powershell
   firebase deploy --only functions --debug
   ```

4. **Tarkista Firebase CLI versio:**
   ```powershell
   firebase --version
   ```
   Pitäisi olla vähintään 11.0.0

## Jos mikään ei auta

1. Poista vanha funktio:
   ```powershell
   firebase functions:delete scrape_website
   ```

2. Deployaa uudelleen:
   ```powershell
   firebase deploy --only functions
   ```

3. Tarkista logit:
   ```powershell
   firebase functions:log
   ```

