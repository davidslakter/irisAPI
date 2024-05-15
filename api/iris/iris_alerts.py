import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from twilio.rest import Client

#twilio setup
account_sid = '------'
auth_token = '----'
twilio_client = Client(account_sid, auth_token)

def sendEmail(recipient, crime_type):
    # email setup
    iris_email = 'alerts@xiris.ai' 
    iris_password = '-------'
    
    msgRoot = MIMEMultipart('related')
    msgRoot['Subject'] = 'Security Update'
    msgRoot['From'] = iris_email
    msgRoot['To'] = recipient
    msgRoot.preamble = ''

    msgAlternative = MIMEMultipart('alternative')
    msgRoot.attach(msgAlternative)

    email_body = f"""\
            <html>
                <head></head>
                <body>
                    <p>
                    Iris detected (a) {crime_type}! the footage is available on your dashboard at http://dashboard.xiris.ai 
                    </p>
                </body>
            </html>
            """
    msgText = MIMEText(email_body, 'html')
    msgAlternative.attach(msgText)

    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.starttls()
    smtp.login(iris_email, iris_password)
    smtp.sendmail(iris_email, recipient, msgRoot.as_string())
    smtp.quit()


def sendText(recipient, crime_type):
    msg = twilio_client.messages.create(
            body=f"Iris detected (a) {crime_type}! To see the footage, login to your dashboard at http://dashboard.xiris.ai",
            from_='+12068256609',
            to=recipient
        )

