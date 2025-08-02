import smtplib
import pandas as pd
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders
import traceback
import logging
from dotenv import load_dotenv

# Create .env file if it doesn't exist
env_file_path = '.env'
if not os.path.exists(env_file_path):
    print("Willkommen beim Simple Mailer Setup!")
    print("Die .env Datei wurde nicht gefunden. Bitte geben Sie Ihre E-Mail-Konfiguration ein:")
    print()
    
    # Interactive input for email configuration
    email_login = input("E-Mail Adresse (z.B. ihre@email.de): ").strip()
    email_password = input("E-Mail Passwort: ").strip()
    smtp_server = input("SMTP Server (z.B. mail.example.de): ").strip()
    smtp_port = input("SMTP Port (Standard: 465): ").strip() or "465"
    email_subject = input("E-Mail Betreff: ").strip()
    
    print("\nErstelle .env Datei mit Ihren Eingaben...")
    with open(env_file_path, 'w', encoding='utf-8') as env_file:
        env_file.write(f"""# Email configuration
EMAIL_LOGIN={email_login}
EMAIL_PASSWORD={email_password}
SMTP_SERVER={smtp_server}
SMTP_PORT={smtp_port}
EMAIL_SUBJECT={email_subject}
""")
    print(f"✓ {env_file_path} wurde erfolgreich erstellt!")
    print("Das Skript wird nun mit Ihrer Konfiguration fortfahren...\n")

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Read email addresses and attachment filenames from CSV
email_data = pd.read_csv('list.csv')
df = pd.DataFrame(email_data)

# Email account configuration
login_acc = os.getenv('EMAIL_LOGIN')
login_pass = os.getenv('EMAIL_PASSWORD')
smtp_server = os.getenv('SMTP_SERVER')
smtp_port = int(os.getenv('SMTP_PORT', 465))
email_subject = os.getenv('EMAIL_SUBJECT')

# Validate that all required environment variables are set
required_vars = {
    'EMAIL_LOGIN': login_acc,
    'EMAIL_PASSWORD': login_pass,
    'SMTP_SERVER': smtp_server,
    'EMAIL_SUBJECT': email_subject
}

missing_vars = [var for var, value in required_vars.items() if not value or value.strip() == '']

if missing_vars:
    print(f"Fehler: Die folgenden Umgebungsvariablen sind nicht konfiguriert in der .env Datei:")
    for var in missing_vars:
        print(f"  - {var}")
    print("Bitte bearbeiten Sie die .env Datei mit Ihren korrekten E-Mail-Daten.")
    input("Drücken Sie Enter zum Beenden...")
    exit()

# Read email body
with open('email_body.html', 'r', encoding='utf8') as f:
    email_body = f.read()

# Attachments folder path
attachments_folder = 'attachments'

try:
    # Use SMTP_SSL for port 465 instead of SMTP with starttls
    server = smtplib.SMTP_SSL(smtp_server, smtp_port)
    server.login(login_acc, login_pass)
    
    # Preview emails and attachments before sending
    print("\n" + "="*60)
    print("VORSCHAU - E-MAIL VERSAND")
    print("="*60)
    print(f"Betreff: {email_subject}")
    print(f"Absender: {login_acc}")
    print(f"Anzahl Empfänger: {len(df)}")
    print("\nEmpfänger und Anhänge:")
    print("-" * 60)
    
    valid_emails = []
    invalid_emails = []
    
    for index, row in df.iterrows():
        email = row['emails']
        attachment_filename = row['attachments'] + '.pdf'
        attachment_path = os.path.join(attachments_folder, attachment_filename)
        
        attachment_status = "✓ Gefunden" if os.path.exists(attachment_path) else "✗ FEHLT"
        
        print(f"{index+1:2d}. {email:<35} | {attachment_filename:<20} | {attachment_status}")
        
        if os.path.exists(attachment_path):
            valid_emails.append((email, attachment_filename, attachment_path))
        else:
            invalid_emails.append((email, attachment_filename))
    
    print("-" * 60)
    print(f"✓ Gültige E-Mails: {len(valid_emails)}")
    if invalid_emails:
        print(f"✗ E-Mails mit fehlenden Anhängen: {len(invalid_emails)}")
        print("  (Diese werden übersprungen)")
    
    print("\n" + "="*60)
    
    # Ask for confirmation
    if len(valid_emails) == 0:
        print("FEHLER: Keine gültigen E-Mails zum Versenden gefunden!")
        input("Drücken Sie Enter zum Beenden...")
        server.quit()
        exit()
    
    confirmation = input(f"Möchten Sie {len(valid_emails)} E-Mail(s) versenden? (j/N): ").strip().lower()
    
    if confirmation not in ['j', 'ja', 'y', 'yes']:
        print("E-Mail-Versand abgebrochen.")
        server.quit()
        exit()
    
    print(f"\nStarte E-Mail-Versand an {len(valid_emails)} Empfänger...")
    print("-" * 60)

    # Process each valid email
    sent_count = 0
    for email, attachment_filename, attachment_path in valid_emails:
        try:
            # Create a new message for each email
            msg = MIMEMultipart()
            msg['From'] = login_acc
            msg['To'] = email
            msg['Subject'] = email_subject
            
            # Add the logo image as inline attachment
            try:
                with open('ticketree.png', 'rb') as img:
                    image = MIMEImage(img.read())
                    image.add_header('Content-ID', '<ticketree-logo>')
                    image.add_header('Content-Disposition', 'inline', filename='ticketree-logo.png')
                    msg.attach(image)
            except Exception as img_err:
                logging.error(f"Failed to attach logo image: {str(img_err)}")
                print(f"Warning: Could not attach logo image: {str(img_err)}")
            
            # Attach the email body
            msg.attach(MIMEText(email_body, 'html'))
            
            # Create the attachment for this specific email
            with open(attachment_path, 'rb') as attachment_file:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment_file.read())
                encoders.encode_base64(part)
                # Add .pdf extension to the attachment filename
                part.add_header('Content-Disposition', f'attachment; filename="{attachment_filename}"')
                msg.attach(part)
            
            # Send the email
            text = msg.as_string()
            server.sendmail(login_acc, email, text)
            sent_count += 1
            print(f'✓ E-Mail gesendet an: {email} ({sent_count}/{len(valid_emails)})')
            
        except Exception as e:
            logging.error(f"Failed to send email to {email}: {str(e)}")
            logging.error(traceback.format_exc())
            print(f"✗ Fehler beim Senden an: {email}")
            continue
    
    server.quit()
    print(f"\nE-Mail-Versand abgeschlossen!")
    print(f"Erfolgreich gesendet: {sent_count}/{len(valid_emails)} E-Mails")
    
except Exception as e:
    logging.error(f"Server connection error: {str(e)}")
    logging.error(traceback.format_exc())
    print(f"Server connection failed: {str(e)}")

