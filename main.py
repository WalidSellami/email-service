from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from jinja2 import Environment, FileSystemLoader
from email.message import EmailMessage
import aiosmtplib
import os

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load SMTP credentials from environment
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# Setup Jinja2 templates
env = Environment(loader=FileSystemLoader("templates"))

# Request body
class EmailData(BaseModel):
    theme: str  # 'confirm_user', 'confirm_therapist', or 'reject_user'
    user_email: str
    therapist_email: str
    subject: str
    therapist_name: str
    user_name: str
    user_condition: str
    session_type: str
    date: str
    time: str
    duration: str
    reason_rejection: str = ""


@app.post("/send-email")
async def send_email(email_data: EmailData):
    try:
        theme = email_data.theme.lower()

        if theme == "reject_user":
            template = env.get_template("email_template_reject_user.html")
            html = template.render(
                subject=email_data.subject,
                therapist_name=email_data.therapist_name,
                therapist_email=email_data.therapist_email,
                session_type=email_data.session_type,
                date=email_data.date,
                time=email_data.time,
                duration = email_data.duration,
                reason_rejection=email_data.reason_rejection,
            )
            msg = EmailMessage()
            msg["From"] = f"Admin Support <{SMTP_EMAIL}>"
            msg["To"] = email_data.user_email
            msg["Subject"] = email_data.subject
            msg.set_content("Your session has been rejected.")
            msg.add_alternative(html, subtype="html")

        elif theme == "confirm_user":
            template = env.get_template("email_template_user.html")
            html = template.render(
                subject=email_data.subject,
                date=email_data.date,
                time=email_data.time,
                duration = email_data.duration,
                link ='https://serenity-platform.web.app',
                therapist_name=email_data.therapist_name,
                therapist_email=email_data.therapist_email,
                session_type=email_data.session_type,
            )
            msg = EmailMessage()
            msg["From"] = f"Admin Support <{SMTP_EMAIL}>"
            msg["To"] = email_data.user_email
            msg["Subject"] = email_data.subject
            msg.set_content("Your session is confirmed.")
            msg.add_alternative(html, subtype="html")

        elif theme == "confirm_therapist":
            template = env.get_template("email_template_therapist.html")
            html = template.render(
                subject=email_data.subject,
                date=email_data.date,
                time=email_data.time,
                duration = email_data.duration,
                therapist_name=email_data.therapist_name,
                session_type=email_data.session_type,
                link ='https://serenity-platform.web.app',
                user_name=email_data.user_name,
                user_email=email_data.user_email,
                user_condition=email_data.user_condition,
            )
            msg = EmailMessage()
            msg["From"] = f"Admin Support <{SMTP_EMAIL}>"
            msg["To"] = email_data.therapist_email
            msg["Subject"] = email_data.subject
            msg.set_content("Session with a user is confirmed.")
            msg.add_alternative(html, subtype="html")

        else:
            raise HTTPException(status_code=400, detail="Invalid theme value.")

        await aiosmtplib.send(
            msg,
            hostname="smtp.gmail.com",
            port=587,
            start_tls=True,
            username=SMTP_EMAIL,
            password=SMTP_PASSWORD
        )

        return {"message": f"{theme.replace('_', ' ').capitalize()} email sent."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))