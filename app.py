import os
import smtplib
from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import urllib.parse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables
load_dotenv()
EMAIL_ADDRESS = os.getenv("EMAILID")
EMAIL_PASSWORD = os.getenv("PASS")

@app.route('/')
def upload_csv():
    return render_template('upload.html')

@app.route('/kanban', methods=['POST'])
def kanban():
    file = request.files['file']
    df = pd.read_csv(file)
    
    # Split the dataframe into two halves
    fazz = df.shape
    foo = (fazz[0] - 1) // 2  
    ram_board = df.iloc[:foo+1, :]  
    shyam_board = df.iloc[foo+1:, :]  
    
    return render_template('kanban.html', ram_board=ram_board, shyam_board=shyam_board)

@app.route('/send_mail', methods=['POST'])
def send_mail():
    candidate_email = request.form['email']
    candidate_name = request.form['name']
    company_name = request.form['company']
    interviewer_email = request.form['interviewer_email']
    scheduling_method = request.form['scheduling_method']

    subject = f"Follow-up for {candidate_name} at {company_name}"
    body = (f"Dear {candidate_name},\n\n"
            f"We are following up with you regarding your interview with {company_name}.\n"
            f"Please schedule your interview using the following method: {scheduling_method}\n\n"
            f"Best regards,\n{interviewer_email}")
    
    try:
        send_email(candidate_email, subject, body)
    except Exception as e:
        print(f"Error sending email: {e}")
        return "Failed to send email", 500

    return redirect(url_for('upload_csv'))


def send_email(to_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Attach the body to the email
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

            smtp.send_message(msg)
            print(f"Email sent to {to_email} with subject '{subject}' and body:\n{body}")
    except smtplib.SMTPException as e:
        print(f"SMTP error: {e}")
        raise


@app.route('/send_whatsapp', methods=['POST'])
def send_whatsapp():
    candidate_phone = request.form['phone']
    message = request.form['message']
    whatsapp_url = f"https://api.whatsapp.com/send?phone={candidate_phone}&text={urllib.parse.quote(message)}"
    return redirect(whatsapp_url)

@app.route('/reveal_phone', methods=['POST'])
def reveal_phone():
    candidate_phone = request.form['phone']
    return f"Phone Number: {candidate_phone}"

if __name__ == "__main__":
    app.run(debug=True)
