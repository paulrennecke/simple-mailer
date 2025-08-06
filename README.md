# Simple Mailer

Python-Tool zum Versenden von E-Mails mit individuellen PDF-Anhängen.

Wenn du nur eine benutzerfreundliche Webanwendung suchst, die das erledigt: [online-mailer](https://github.com/paulrennecke/online-mailer)

## Dateien

- **email_body.html** - E-Mail Inhalt (HTML-Format)
- **list.csv** - E-Mail-Adressen und Anhang-Zuordnungen
- **send_email.py** - Hauptprogramm
- **attachments/** - Ordner mit PDF-Dateien
- **.env** - E-Mail-Konfiguration (wird beim ersten Start erstellt)

## Installation

```bash
pip install pandas python-dotenv
```

## Verwendung

```bash
python send_email.py
```

Beim ersten Start werden Sie nach Ihren E-Mail-Daten gefragt.

---

*Fork von: https://github.com/aniketbote/sending-multiple-emails-attachments*