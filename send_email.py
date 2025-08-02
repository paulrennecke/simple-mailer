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

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Read email addresses and attachment filenames from CSV
email_data = pd.read_csv('list.csv')
df = pd.DataFrame(email_data)

# Email account configuration
login_acc = 'bestellung@ticketree.de'
login_pass = ''

# Read email body
with open('email_body.txt', 'r', encoding='utf8') as f:
    email_body = f.read()

# Attachments folder path
attachments_folder = 'attachments'

try:
    # Use SMTP_SSL for port 465 instead of SMTP with starttls
    server = smtplib.SMTP_SSL('mail.ticketree.de', 465)
    server.login(login_acc, login_pass)
    
    # Process each row in the CSV
    for index, row in df.iterrows():
        email = row['emails']
        attachment_filename = row['attachments']+ '.pdf'
        attachment_path = os.path.join(attachments_folder, attachment_filename)
        
        try:
            # Check if attachment file exists
            if not os.path.exists(attachment_path):
                print(f"Warning: Attachment file not found: {attachment_path} for email: {email}")
                continue
                
            # Create a new message for each email
            msg = MIMEMultipart()
            msg['From'] = login_acc
            msg['To'] = email
            msg['Subject'] = 'Ticket 9:16 AWARDS 2025'
            
            # Add the logo image as inline attachment
            try:
                with open('image001.png', 'rb') as img:
                    image = MIMEImage(img.read())
                    image.add_header('Content-ID', '<Grafik_x0020_1>')
                    image.add_header('Content-Disposition', 'inline', filename='image001.png')
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
            print(f'Email sent to: {email} with attachment: {attachment_filename}')
            
        except Exception as e:
            logging.error(f"Failed to send email to {email}: {str(e)}")
            logging.error(traceback.format_exc())
            print(f"Failed to send to: {email}")
            continue
    
    server.quit()
    print("All emails processed")
    
except Exception as e:
    logging.error(f"Server connection error: {str(e)}")
    logging.error(traceback.format_exc())
    print(f"Server connection failed: {str(e)}")

