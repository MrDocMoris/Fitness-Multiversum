# Fitness-Multiversum

Deine eigene Ernährungs- und Fitness-App, ähnlich wie Yazio, aber nur für dich und komplett auf deinem Handy. Gleicher Stil und gleicher Update-Weg wie TCG Multiversum, Familien-Multiversum, Metin2-Multiversum und Finanz-Multiversum.

## Funktionen
- **Tagebuch**: Kalorien-Ring („kcal übrig“), Eiweiß, Kohlenhydrate und Fett mit Tageszielen, vier Mahlzeiten, Wasser-Zähler (Gläser antippen), frühere Tage durchblättern, „Wie gestern“ übernimmt eine Mahlzeit vom Vortag
- **Lebensmittel finden**: gespeicherte, zuletzt benutzte und Favoriten sofort, rund 70 Grundnahrungsmittel eingebaut, Online-Suche in **Open Food Facts** (freie Datenbank mit vielen deutschen Produkten)
- **Barcode-Scanner** mit der Handykamera (EAN/UPC). Unbekannte Produkte kannst du selbst anlegen
- **Mengen** in Gramm/ml oder Portionen, Schnellwahl-Knöpfe, Nährwerte live; „Nur Kalorien“ für Kantine & Co.
- **Eigene Lebensmittel** mit Nährwerten, Portion und Barcode
- **Ziele**: Kalorienbedarf nach Mifflin-St Jeor (Geschlecht, Alter, Größe, Gewicht, Aktivität), Ziel abnehmen/halten/zunehmen, Nährstoff-Verteilung, voraussichtliches Datum fürs Zielgewicht, Kalorienziel auf Wunsch auch manuell
- **Körper**: Gewicht mit Verlauf (30 Tage bis alles), Zielgewicht-Fortschritt, BMI, Körperfett
- **Garmin** (offizielle Personal API): Schritte, Aktiv- und Gesamtkalorien, Ruhepuls, Body Battery, Stress, Schlaf, Gewicht (Garmin-Waage) und Aktivitäten. Sport-Kalorien werden dem Tagesziel gutgeschrieben (0/50/100 %). Automatischer Abgleich beim Öffnen (höchstens alle 30 Minuten)
- **Yazio-Import**: Ernährungstagebuch (Lebensmittel, Mengen, Mahlzeiten) und Gewicht aus Yazio übernehmen, bis zu 2 Jahre zurück; doppelte Einträge werden übersprungen
- **Auswertung**: Kalorien pro Tag gegen das Ziel, Tage im Ziel, Kalorienbilanz mit rechnerischem Fettverlust, Durchschnitt der Nährstoffe, Gewicht, Schritte, größte Kalorienquellen
- **Eigene Gerichte & Rezepte**: Zutaten zusammenstellen, Portionen und Gewicht des fertigen Topfs angeben, mit einem Tipp eintragen. Eine Mahlzeit lässt sich direkt „als Gericht speichern“
- **Nährwert-Etikett abfotografieren**: Texterkennung (Google ML Kit, direkt auf dem Handy) liest kcal, Eiweiß, Kohlenhydrate, Fett, Zucker, Ballaststoffe und Salz und legt das Lebensmittel an
- **Schnell per Text oder Sprache**: „200 g Hähnchen, 150 g Reis, 2 Eier“ wird erkannt, Unbekanntes wird in Open Food Facts nachgeschlagen, alles in einem Rutsch eintragen
- **Intervallfasten-Timer** (14:10 bis 24 h) mit Fortschritt, Push am Ende und Verlauf
- **Gewichts-Trend**: geglättete Trendlinie, kg pro Woche und voraussichtliche Wochen bis zum Zielgewicht
- **Lernendes Kalorienziel**: Aus 4 Wochen Tagebuch und Gewichtstrend rechnet die App deinen echten Verbrauch aus und nutzt ihn auf Wunsch als Ziel
- **Zucker, Ballaststoffe, Salz** pro Tag mit Richtwerten
- **Sport ohne Garmin eintragen** (12 Sportarten, Kalorien geschätzt nach MET und Gewicht)
- **Startbildschirm-Widget**: kcal übrig, Gegessen/Ziel, Wasser, Knöpfe „+ Essen“ und „💧 +1 Glas“
- **Nur-Wasser-Zähler** mit Countdown bis Rock am Ring: Feiertage (NRW) und Geburtstage zählen als Ausnahme, die App fragt nach, wenn ein Softdrink, Saft oder Alkohol eingetragen wird
- **Körpermaße** (Bauch, Hüfte, Brust, Oberarm, Oberschenkel, Hals) und **Fortschrittsfotos** mit Vorher-nachher-Vergleich (bleiben privat in der App)
- **Serien & Abzeichen**: Tage in Folge eingetragen, im Ziel, Wasser-Ziel; 25 Abzeichen
- **Erinnerungen** (optional): Mahlzeiten (nur wenn noch leer), morgens wiegen, Wasser alle 2 Stunden
- Automatische Sicherung in *Dokumente/Fitness-Multiversum*, Kopieren/Einfügen, Update-Prüfung

## Garmin einrichten
1. Garmin Connect im Browser öffnen → Einstellungen → **Personal API** → Schlüssel erstellen (am besten 1 Jahr gültig)
2. Schlüssel kopieren (er wird nur einmal angezeigt)
3. In der App: Zahnrad → Garmin → Schlüssel einfügen → Verbinden

Der Schlüssel bleibt nur auf dem Handy und wird nicht mitgesichert. Garmin schickt dir eine E-Mail, bevor er abläuft.

## Yazio übernehmen
Zahnrad → Yazio → E-Mail und Passwort eingeben → Zeitraum wählen. Die Zugangsdaten werden nicht gespeichert. Yazio hat keine offizielle Schnittstelle, deshalb kann das irgendwann nicht mehr funktionieren. Für den Umstieg reicht ein einmaliger Import.

## Datenschutz
Kein eigener Server. Alle Daten liegen nur auf deinem Handy (und in der Sicherungsdatei). Dieses Repo enthält nur den App-Code, keine persönlichen Daten.

## Aufbau
- `fitness.html`: die komplette App (HTML/CSS/JS), läuft zum Testen auch im Browser (Garmin und Yazio dort nicht, weil die Server Browser-Anfragen blockieren)
- `assets/icon.svg`: App-Icon
- `native/`: eigene Android-Bausteine (Widget, Spracheingabe, Texterkennung mit ML Kit)
- `.github/workflows/build-apk.yml`: baut bei jeder Änderung die Android-App (Capacitor 7, natives HTTP für Garmin/Yazio/Open Food Facts, ZXing als Barcode-Ersatz), signiert sie mit `signing/debug.keystore` (wird beim ersten Lauf angelegt), veröffentlicht sie als Release und schreibt `app/version.json`
