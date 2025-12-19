# MVP
1. Entwicklung eines einfachen CLI-Tools zur Abfrage von Nährwertinformationen von OpenFoodFacts (https://publicapis.io/open-food-facts-api, https://platform.fatsecret.com/platform-api). Nach Lebensmitteln suchen und Nährwertangaben anzeigen. 
   - Suchkriterien sind Name und Hersteller.
2. Anlegen von Rezepten mit Nährwertberechnung.
   - Nutzer können Rezepte eingeben, und das Tool berechnet die Gesamt-Nährwerte basierend auf den Zutaten.
   - Zutaten werden durch die Produktsuche selektiert. Mengen der Zutaten im Rezept müssen angegeben werden. Eventuell mit Angabe der Anzahl der Personen, für die das Rezept gedacht ist.
   - Die Rezepte werden als JSON-Datei gespeichert und können später wieder geladen werden.
   - Die Mengenangaben werden pro Person persistiert.

# Optionale Features
3. Erstellung eines Speiseplans für die Woche aus den Rezepten.
   - Nutzer können Rezepte einem Wochentag zuordnen.
4. Generierung einer Einkaufsliste basierend auf dem Speiseplan.
   - Das Tool erstellt eine Einkaufsliste mit den benötigten Zutaten und Mengen.
   - Die Anzahl der Personen muss angegeben werden, um die Mengen korrekt zu skalieren.
5. Einkaufsliste bei Google Keep speichern.
   - Integration mit Google Keep API, um die Einkaufsliste direkt in Google Keep zu speichern.