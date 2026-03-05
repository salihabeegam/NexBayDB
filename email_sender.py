# email_sender.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from config import EMAIL_CONFIG


class EmailSender:
    def __init__(self):
        """Initialize email sender with config from config.py"""
        self.smtp_server = EMAIL_CONFIG['smtp_server']
        self.smtp_port = EMAIL_CONFIG['smtp_port']
        self.smtp_user = EMAIL_CONFIG['sender_email']  # Using 'sender_email' key
        self.smtp_password = EMAIL_CONFIG['sender_password']  # Using 'sender_password' key

    def send_email(self, recipient_email, subject, body, attachment_path=None):
        """Send plain text email with optional attachment"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_user
            msg['To'] = recipient_email
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            if attachment_path and os.path.exists(attachment_path):
                with open(attachment_path, 'rb') as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {os.path.basename(attachment_path)}'
                    )
                    msg.attach(part)

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.smtp_user, recipient_email, msg.as_string())

            return True, "Email sent successfully"
        except Exception as e:
            return False, str(e)

    def send_email_html(self, recipient_email, subject, html_body, plain_text_body=None, attachment_paths=None,
                        bcc_email=None):
        """Send HTML email with optional attachments and BCC"""
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.smtp_user
            msg['To'] = recipient_email
            msg['Subject'] = subject

            # Add plain text version
            if plain_text_body:
                part1 = MIMEText(plain_text_body, 'plain')
                msg.attach(part1)

            # Add HTML version
            part2 = MIMEText(html_body, 'html')
            msg.attach(part2)

            # Add attachments
            if attachment_paths:
                for file_path in attachment_paths:
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as f:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(f.read())
                            encoders.encode_base64(part)
                            part.add_header('Content-Disposition',
                                            f'attachment; filename= {os.path.basename(file_path)}')
                            msg.attach(part)

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)

                # Include BCC in recipients list (but not in headers)
                recipients = [recipient_email]
                if bcc_email:
                    recipients.append(bcc_email)

                server.sendmail(self.smtp_user, recipients, msg.as_string())

            return True, "Email sent successfully"
        except Exception as e:
            return False, str(e)

    def send_email_to_multiple(self, recipient_emails, subject, body, attachment_path=None):
        """Send plain text email to multiple recipients"""
        email_list = [e.strip() for e in recipient_emails.replace(';', ',').replace('\n', ',').split(',') if e.strip()]

        success_count = 0
        failed_emails = []
        results = []

        for email in email_list:
            success, message = self.send_email(email, subject, body, attachment_path)
            if success:
                success_count += 1
                results.append({'email': email, 'status': 'Success'})
            else:
                failed_emails.append(email)
                results.append({'email': email, 'status': f'Failed: {message}'})

        return success_count, failed_emails, results

    def send_email_to_multiple_html(self, recipient_emails, subject, port_name=None, country=None,
                                    attachment_paths=None, bcc_email=None, html_body=None, plain_text_body=None):
        """Send HTML emails to multiple recipients with BCC support"""
        # Parse emails
        email_list = [e.strip() for e in recipient_emails.replace(';', ',').replace('\n', ',').split(',') if e.strip()]

        success_count = 0
        failed_emails = []
        results = []

        for email in email_list:
            try:
                # Use provided HTML/plain text or generate from templates
                if html_body is None and port_name and country:
                    from email_templates import get_html_template, get_plain_text_template
                    html_content = get_html_template(port_name, country)
                    plain_content = get_plain_text_template(port_name, country)
                else:
                    html_content = html_body
                    plain_content = plain_text_body

                success, msg = self.send_email_html(
                    recipient_email=email,
                    subject=subject,
                    html_body=html_content,
                    plain_text_body=plain_content,
                    attachment_paths=attachment_paths,
                    bcc_email=bcc_email
                )

                if success:
                    success_count += 1
                    results.append({'email': email, 'status': 'Success'})
                else:
                    failed_emails.append(email)
                    results.append({'email': email, 'status': f'Failed: {msg}'})
            except Exception as e:
                failed_emails.append(email)
                results.append({'email': email, 'status': f'Failed: {str(e)}'})

        return success_count, failed_emails, results

    def send_bulk_emails(self, recipients_list, subject, body, attachment_path=None):
        """Send emails in bulk to a list of recipients"""
        success_count = 0
        failed_count = 0

        for recipient in recipients_list:
            success, _ = self.send_email(recipient, subject, body, attachment_path)
            if success:
                success_count += 1
            else:
                failed_count += 1

        return success_count, failed_count