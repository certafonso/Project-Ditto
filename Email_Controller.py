import smtplib
import imaplib
import email
import os
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

def Setup_SMTP(username, password):
    """Creates SMTP server (to send emails)"""

    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.ehlo()
    server.login(username, password)

    return server

def Setup_IMAP(username, password):
    """Creates IMAP server (to see emails)"""
    
    server = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    server.login(username, password)

    return server

def SendEmail(username, password, receiver, subject, message):
    """Sends a plain text email"""

    try:
        message = f"Subject: {subject} \n\n{message}"

        server = Setup_SMTP(username, password)

        server.sendmail(username, receiver, message)

        print(f"{subject} was sent to {receiver}")

        return True
    except:
        print("ERROR")
        return False

def SendWithAttachment(username, password, receiver, subject, message, ImgFileName):
    """Sends email with image attached"""

    img_data = open(ImgFileName, 'rb').read()
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = username
    msg['To'] = receiver

    text = MIMEText(message)
    msg.attach(text)
    image = MIMEImage(img_data, name=os.path.basename(ImgFileName))
    msg.attach(image)

    s = Setup_SMTP(username, password)

    s.sendmail(username, receiver, msg.as_string())

def GetLastMail(username, password):
    server = Setup_IMAP(username, password)

    server.select("Inbox")

    a, data = server.search(None, 'ALL')

    mail_ids = data[0]
    id_list = mail_ids.split()

    num = data[0].split()[-1] #select last mail
    
    typ, data = server.fetch(num, '(RFC822)' )
    msg = email.message_from_string(data[0][1].decode("utf-8"))

    mail = {
        "id": id_list[-1],
        "to": msg["to"],
        "from": msg["from"],
        "subject": msg["subject"],
        "body": msg.get_payload()[0].get_payload()
    }

    return mail