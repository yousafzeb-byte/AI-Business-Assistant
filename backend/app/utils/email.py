import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)

_RESET_HTML = """\
<!DOCTYPE html>
<html>
<body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:32px;background:#f9fafb">
  <div style="background:#fff;border-radius:10px;padding:32px;border:1px solid #e5e7eb">
    <h2 style="color:#6366f1;margin-top:0">AI Business Ops — Password Reset</h2>
    <p style="color:#374151">We received a request to reset the password for your account.</p>
    <p>
      <a href="{reset_link}"
         style="background:#6366f1;color:#fff;padding:12px 28px;border-radius:6px;
                text-decoration:none;display:inline-block;font-weight:600">
        Reset Password
      </a>
    </p>
    <p style="color:#9ca3af;font-size:13px;margin-bottom:0">
      This link expires in <strong>1 hour</strong>. If you did not request a
      password reset, you can safely ignore this email.
    </p>
  </div>
</body>
</html>"""

_RESET_TEXT = """\
AI Business Ops — Password Reset

We received a request to reset the password for your account.

Reset your password here:
{reset_link}

This link expires in 1 hour.
If you did not request a password reset, you can safely ignore this email.
"""


def send_password_reset_email(
    *,
    to_email: str,
    reset_link: str,
    smtp_host: str,
    smtp_port: int,
    smtp_user: str,
    smtp_password: str,
    smtp_from: str,
) -> bool:
    """
    Send a password-reset email over SMTP/STARTTLS.
    Returns True on success, False on any delivery failure.
    """
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Reset your AI Business Ops password"
        msg["From"] = smtp_from
        msg["To"] = to_email

        msg.attach(MIMEText(_RESET_TEXT.format(reset_link=reset_link), "plain"))
        msg.attach(MIMEText(_RESET_HTML.format(reset_link=reset_link), "html"))

        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_from, [to_email], msg.as_string())

        logger.info("Password reset email sent to %s", to_email)
        return True

    except smtplib.SMTPAuthenticationError:
        logger.error(
            "SMTP authentication failed — check SMTP_USER / SMTP_PASSWORD"
        )
    except smtplib.SMTPConnectError:
        logger.error(
            "Could not connect to SMTP server %s:%s", smtp_host, smtp_port
        )
    except Exception as exc:
        logger.error("Failed to send reset email to %s: %s", to_email, exc)

    return False
