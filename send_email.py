import smtplib
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import traceback
import logging

email_data = pd.read_csv('test.csv') #provide path of sample.csv
df = pd.DataFrame(email_data)
emails = list(df['emails'])
#print(emails)
login_acc = ''  #email id
login_pass = '' #password
server = smtplib.SMTP('smtp.gmail.com',587)
server.starttls()
server.login(login_acc,login_pass)
with open('bodyh1.txt','r',encoding = 'utf8') as f: #provide email body path
    data = f.read()
filename = 'vesAIthon.pdf' #provide file path
attachment = open(filename,'rb')
part = MIMEBase('application','octet-stream')
part.set_payload(attachment.read())
encoders.encode_base64(part)
part.add_header('Content-Disposition',"attachment;filename = "+filename)

for email in emails:
    try:
        msg = MIMEMultipart()
        msg['From'] = login_acc
        body = data
        msg['Subject'] = 'vesaithon11'
        sendto = email
        msg['To'] = sendto
        msg.attach(part)
        msg.attach(MIMEText(body,'html'))
        text= msg.as_string()
        server.sendmail(login_acc,sendto,text)
        print('sent')
    except Exception as e:
        logging.error(traceback.format_exc())
        print(email)
        continue




server.quit()

