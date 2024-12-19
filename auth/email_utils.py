import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app, render_template
import ssl

class EmailSender:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 465
        self.sender_email = "pranjal.ai.arena@gmail.com"
        self.password = "rwsphrfezciohbgj"
        self.sender_name = "Mino Password Manager"

    def send_email(self, to_email, subject, template_name=None, body=None, **template_args):
        """Send an HTML email using Gmail SMTP service."""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.sender_name} <{self.sender_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject

            if template_name:
                # Render HTML template
                html_content = render_template(f"email/{template_name}.html", **template_args)
                msg.attach(MIMEText(html_content, 'html'))
            else:
                # Use plain text body
                msg.attach(MIMEText(body, 'plain', 'utf-8'))

            # Create SSL context
            context = ssl.create_default_context()

            # Connect to server and send email
            current_app.logger.info(f"Connecting to SMTP server {self.smtp_server}:{self.smtp_port}")
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context) as server:
                current_app.logger.info("Attempting SMTP login")
                server.login(self.sender_email, self.password)
                current_app.logger.info("SMTP login successful")
                
                current_app.logger.info(f"Sending email to {to_email}")
                server.send_message(msg)
                current_app.logger.info("Email sent successfully")

            return True

        except smtplib.SMTPAuthenticationError as e:
            current_app.logger.error(f"SMTP Authentication failed: {str(e)}")
            raise Exception(f"Failed to authenticate with email server: {str(e)}")
            
        except smtplib.SMTPException as e:
            current_app.logger.error(f"SMTP error occurred: {str(e)}")
            raise Exception(f"Failed to send email: {str(e)}")
            
        except Exception as e:
            current_app.logger.error(f"Unexpected error sending email: {str(e)}")
            raise Exception(f"An unexpected error occurred while sending email: {str(e)}")

# Initialize email sender
email_sender = EmailSender()

# Maintain backward compatibility with the old send_email function
def send_email(to_email, subject, body):
    """Backward compatible function for sending plain text emails."""
    return email_sender.send_email(to_email=to_email, subject=subject, body=body)

def send_otp_email(to_email, otp):
    """Send OTP verification email."""
    return email_sender.send_email(
        to_email=to_email,
        subject="Your Verification Code",
        template_name="otp_verification",
        otp=otp
    )

def send_password_reset_email(to_email, reset_link):
    """Send password reset email."""
    return email_sender.send_email(
        to_email=to_email,
        subject="Reset Your Password",
        template_name="password_reset",
        reset_link=reset_link
    )

def send_login_alert(to_email, login_time, ip_address, device, location, account_security_link):
    """Send login alert email."""
    return email_sender.send_email(
        to_email=to_email,
        subject="New Login Detected",
        template_name="login_alert",
        login_time=login_time,
        ip_address=ip_address,
        device=device,
        location=location,
        account_security_link=account_security_link
    )

def send_welcome_email(to_email, name, dashboard_link):
    """Send welcome email to new users."""
    return email_sender.send_email(
        to_email=to_email,
        subject="Welcome to Mino Password Manager",
        template_name="welcome",
        name=name,
        dashboard_link=dashboard_link
    )
