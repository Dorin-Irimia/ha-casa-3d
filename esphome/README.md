# Senzor NTC 10 kΩ / B3950 pe ESP32, cu display OLED

Partea opțională a proiectului [Casa 3D](../README.md): un termometru cu sondă NTC pe ESP32, cu ESPHome, display OLED 128×64, termostat și alarme, integrat în Home Assistant. Senzorul apare și în panoul Casa 3D, ca orice altă entitate.

| Fișier | Rol |
|---|---|
| [`senzor-ntc.yaml`](senzor-ntc.yaml) | Configurația ESPHome (firmware-ul) |
| [`secrets.example.yaml`](secrets.example.yaml) | Model pentru `secrets.yaml`: WiFi, cheia API și parolele |
| [`../home-assistant/dashboard-card.yaml`](../home-assistant/dashboard-card.yaml) | Card gata făcut pentru dashboard |
| [`../home-assistant/automatizare-alarme.yaml`](../home-assistant/automatizare-alarme.yaml) | Notificări pe telefon și mesaj pe display la alarmă sau defect |
| [`../tools/genereaza-fonturi.py`](../tools/genereaza-fonturi.py) | Regenerează fonturile previzualizării, doar dacă schimbi fonturile din YAML |

## Ce face

- Măsoară temperatura cu un NTC de 10 kΩ (B = 3950), filtrată: 16 eșantioane pe citire, apoi mediană din 5. Valoarea se actualizează la fiecare 2 s.
- Afișează pe un OLED 128×64 trei pagini:
  - **Principală**: temperatura mare, plus titlu, colț și rând de jos configurabile;
  - **Detalii**: min/max, rezistența, tensiunea ADC, offsetul, semnalul WiFi și pragurile;
  - **Grafic**: temperatura din ultima oră.
- Tot ce apare pe display se configurează din HA. Tot de acolo poți trimite mesaje pe display și seta modul noapte.
- În Home Assistant apar un **termostat** (climate), praguri de alarmă reglabile, offset de calibrare, min/max, luminozitatea și pornirea display-ului.
- Siguranță:
  - Dacă NTC-ul e întrerupt sau în scurtcircuit, temperatura devine „necunoscută”, releul se oprește și pe ecran apare `EROARE SENZOR`.
  - La depășirea pragului maxim, termostatul se oprește. Comportamentul se poate dezactiva din HA.
- Interfață web locală la `http://senzor-ntc.local`, care merge și fără Home Assistant.

## Componente

- ESP32 DevKit (ESP32-WROOM-32)
- Sondă NTC 10 kΩ @ 25 °C, B3950, cu termistorul în vârf
- Rezistor **10 kΩ, 1 %** (peliculă metalică)
- Condensator ceramic 100 nF
- OLED SSD1306 0,96" I2C (adresa 0x3C)
- *(opțional)* Modul releu comandat de 3,3 V, pentru termostat

## Conectare

```
         3V3 ───────────────┐
                            │
                       [ R 10 kΩ 1% ]
                            │
   GPIO34 (ADC) ────────────┼──────────┐
                            │          │
                        [ NTC 10k ]  [100 nF]
                            │          │
         GND ───────────────┴──────────┘
```

| ESP32 | Conectat la |
|---|---|
| 3V3 | R 10 kΩ (sus) · VCC OLED · VCC releu (dacă e modul de 3,3 V) |
| GND | NTC (jos) · 100 nF · GND OLED · GND releu |
| GPIO34 | Nodul dintre R și NTC |
| GPIO21 | SDA OLED |
| GPIO22 | SCL OLED |
| GPIO26 | IN releu |
| GPIO0 | Butonul **BOOT** de pe placă (nu trebuie cablat nimic) |

> Pinul NTC trebuie să fie pe **ADC1** (GPIO32–39). ADC2 nu funcționează cât timp WiFi-ul e activ.
> Alimentează divizorul din **3V3**, niciodată din 5 V.

## Domeniul de măsurare

Cu R = 10 kΩ, divizorul este cel mai precis în jurul temperaturii de 25 °C:

| °C | R NTC | Tensiune ADC |
|---:|---:|---:|
| −20 | 105 kΩ | 3,01 V |
| 0 | 33,6 kΩ | 2,54 V |
| 25 | 10,0 kΩ | 1,65 V |
| 60 | 2,49 kΩ | 0,66 V |
| 100 | 0,70 kΩ | 0,22 V |
| 120 | 0,41 kΩ | 0,13 V |

Domeniul util este de aproximativ **−18 … +115 °C**. Sub −18 °C sau peste ~130 °C, tensiunea iese din fereastra `v_min_valid` / `v_max_valid` și senzorul e marcat ca defect.

**Dacă vârful sondei lucrează la temperaturi mari** (de exemplu 60–150 °C), alege rezistorul fix egal cu rezistența NTC-ului la mijlocul domeniului care te interesează. De exemplu, **1 kΩ** pentru zona de ~90 °C. Apoi schimbă în `substitutions`:

```yaml
r_serie: 1kOhm
v_min_valid: "0.15"
v_max_valid: "3.00"   # cu 1 kΩ: 3,0 V ≈ 25 °C, deci limita de jos devine ~25 °C
```

## Instalare

1. În Home Assistant: **Setări → Suplimente → ESPHome Builder** → instalează și pornește.
2. **+ New device → Continue → Skip**, apoi **Edit** pe dispozitivul creat. Înlocuiește tot conținutul cu [`senzor-ntc.yaml`](senzor-ntc.yaml).
3. Din **SECRETS** (dreapta sus) adaugă cheile din [`secrets.example.yaml`](secrets.example.yaml), cu valorile tale: `wifi_ssid`, `wifi_password` (de obicei există deja), `senzor_ntc_api_key`, `senzor_ntc_ota_password`, `senzor_ntc_ap_password`.
4. **Install → Plug into this computer** pentru prima programare prin USB. Următoarele actualizări merg wireless (**Install → Wirelessly**).
5. HA descoperă automat dispozitivul (**Setări → Dispozitive → Descoperite → Senzor NTC**). Când ți se cere cheia de criptare, introdu valoarea `senzor_ntc_api_key`.
6. Adaugă cardul din [`home-assistant/dashboard-card.yaml`](../home-assistant/dashboard-card.yaml) și, dacă vrei notificări pe telefon, automatizarea din [`home-assistant/automatizare-alarme.yaml`](../home-assistant/automatizare-alarme.yaml) (înlocuiește `notify.mobile_app_telefonul_meu` cu telefonul tău).
7. Activează configuratorul display-ului (secțiunea următoare).

Fără HA, din terminal: `pip install esphome`, apoi, din acest folder, `cp secrets.example.yaml secrets.yaml` (completează-l) și `esphome run senzor-ntc.yaml`.

## Pagina de configurare a display-ului

Pagina vine cu integrarea **Casa 3D** (vezi [README-ul principal](../README.md)): în **Setări → Dispozitive și servicii → Casa 3D → Configurează** bifează **„Adaugă și configuratorul display-ului NTC”**. În bara laterală apare panoul **Display NTC**.

- **Previzualizare a OLED-ului.** Fonturile sunt generate cu FreeType exact ca în ESPHome, iar desenarea reproduce lambda-ul display-ului. Textul și graficul arată deci pixel cu pixel ca pe ecranul real.
  - Poți comuta între paginile Principală, Detalii, Grafic, Mesaj, Eroare și Test.
  - Poți alege culoarea modulului: alb, albastru sau galben + albastru.
  - Poți simula scenarii (alarmă, releu pornit, fără HA) fără să le provoci în realitate.
- **Modificările de afișare se adună într-o ciornă.** Le vezi în previzualizare, iar pe display ajung doar când apeși **Aplică pe display**. Cu **Renunță** revii la ce e pe display.
- **Funcții auxiliare:**
  - mesaje pe display, cu verificarea dacă încap în 3 rânduri;
  - test de pixeli, resetare min/max, repornire;
  - configurații salvate în browser, export/import JSON și revenire la valorile implicite;
  - termostat (mod, țintă, preset), offset și praguri de alarmă, care se aplică imediat.

**Fără integrare:** copiază [`ntc-display.html`](../custom_components/casa_3d/frontend/ntc-display.html) în `/config/www/`, apoi **Setări → Panouri de control → Adaugă panou → Pagină web**, cu URL-ul `/local/ntc-display.html?v=1`. Pagina folosește automat sesiunea HA în care e deschisă, fără token. Browserul ține fișierele din `/local/` în cache: după o versiune nouă, schimbă `?v=1` în `?v=2`.

Dacă deschizi pagina direct în browser, în afara HA, intră în **Conexiune și entități** și introdu adresa HA plus un token de lungă durată (Profil → Securitate). Fără conexiune, pagina rulează în **mod demo**, cu date simulate.

Dacă ai schimbat numele dispozitivului (`friendly_name`) sau ID-urile entităților, le poți corecta în **Conexiune și entități**. Tabelul de acolo arată ce entitate a fost găsită și ce lipsește.

**Mesaje din automatizări.** Aceeași acțiune se poate folosi oriunde în HA:

```yaml
action: esphome.senzor_ntc_afiseaza_mesaj
data:
  mesaj: "Ușa cuptorului e deschisă"
  durata: 30          # secunde (1-3600)
```

Mai există `esphome.senzor_ntc_sterge_mesaj` și `esphome.senzor_ntc_test_display` (cu parametrul `durata`, 1-30 s).

> Previzualizarea reproduce firmware-ul din acest folder. Dacă modifici lambda-ul display-ului sau fonturile din YAML, actualizează și funcția `renderDisplay` din pagină, respectiv rulează [`tools/genereaza-fonturi.py`](../tools/genereaza-fonturi.py).

## Entități în Home Assistant

| Entitate | Tip | Ce face |
|---|---|---|
| Temperatură | senzor | Valoarea principală, cu offsetul aplicat |
| Temperatură minimă / maximă | senzor | Extreme de la pornire sau de la ultima resetare |
| Termostat | climate | Mod Încălzire/Oprit, temperatură țintă, preseturi *Normal* (40 °C) și *Eco* (30 °C) |
| Prag alarmă maximă / minimă | number | Pragurile alarmelor, cu histerezis de 1 °C |
| Alarmă temperatură maximă / minimă | binary | Pornite când temperatura trece de prag |
| Defect senzor | binary | NTC întrerupt sau în scurtcircuit |
| Offset calibrare | number | Corecție ±10 °C |
| Oprire termostat la alarmă maximă | switch | Pune termostatul pe *Oprit* la alarma maximă |
| Display / Luminozitate display | switch / number | Stingere display și contrast |
| Display titlu, colț dreapta, format temperatură, rând jos, text personalizat, indicator | text / select | Ce apare pe pagina principală |
| Display pagini în rotație, rotire automată, pagina curentă, întors | select / number / switch | Paginile afișate și orientarea ecranului |
| Display mod noapte, noapte de la/până la ora, luminozitate noapte | switch / number | Luminozitate redusă sau display stins noaptea |
| Display mod noapte activ | diagnostic | Arată dacă acum e în vigoare modul noapte |
| Resetare minim și maxim | button | Resetează extremele |
| Rezistență NTC, Tensiune ADC, Semnal WiFi… | diagnostic | Pentru depanare |

Termostatul pornește pe **Oprit** la primul boot. Îl activezi din HA (modul *Heat*). Releul pornește la țintă − 0,5 °C și se oprește la țintă + 0,5 °C. Între comutări trec minim 20 s.

## Butonul de pe placă (BOOT / GPIO0)

- **Apăsare scurtă**: trece la următoarea pagină din rotație. Dacă pe ecran e un mesaj, îl închide.
- **Apăsare lungă (2–6 s)**: resetează min/max.

## Calibrare

1. **Măsoară rezistorul fix** cu multimetrul și trece valoarea exactă în `r_serie` (de exemplu `9.96kOhm`). Este cea mai mare sursă de eroare.
2. **Verifică la 0 °C**: pune vârful sondei în apă cu gheață mărunțită, amestecată, timp de 3–5 min. Diferența față de 0 °C o treci în *Offset calibrare*.
3. Dacă eroarea crește odată cu temperatura (de exemplu e corectă la 0 °C, dar greșește cu 2 °C la 80 °C), atunci **B-ul real diferă** de 3950. Valori uzuale: 3435, 3950, 3977. Ajustează `ntc_beta`.

## Răcire în loc de încălzire

În blocul `climate:` înlocuiește:

- `heat_action` → `cool_action`
- `min_heating_off_time` / `min_heating_run_time` → `min_cooling_off_time` / `min_cooling_run_time`
- `heat_deadband` / `heat_overrun` → `cool_deadband` / `cool_overrun`
- în preseturi, `default_target_temperature_low` → `default_target_temperature_high`

## Siguranță

- Dacă releul comută 230 V, folosește un modul cu optocuptor, o carcasă închisă și o siguranță fuzibilă pe fază. Nu lucra cu montajul sub tensiune.
- Pentru încălzitoare nesupravegheate, adaugă și un **termostat mecanic / siguranță termică** independentă în serie cu rezistența de încălzire. Protecția software nu ține locul uneia fizice.
