from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr

from app.core.config import Settings, get_settings


# ==========================================
#  SMTP Client Config
# ==========================================
def _smtp_config(settings: Settings) -> ConnectionConfig:
    """Builds the SMTP connection settings from the application settings.

    Account, password, sender, port and server come from Settings (ADR-0013); the sender is
    mail_from when set and the SMTP account otherwise. Transport options stay fixed here.

    Args:
        settings: The validated application settings.

    Returns:
        ConnectionConfig: The configuration the FastMail client is built with.
    """
    return ConnectionConfig(
        MAIL_USERNAME=settings.mail_username,
        MAIL_PASSWORD=settings.mail_password,
        MAIL_FROM=settings.mail_sender,
        MAIL_PORT=settings.mail_port,
        MAIL_SERVER=settings.mail_server,
        MAIL_FROM_NAME="Ecotur Asoprado",
        MAIL_STARTTLS=False,
        MAIL_SSL_TLS=True,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True,
    )


fast_mail = FastMail(_smtp_config(get_settings()))


async def send_verification_email(email_to: EmailStr, first_name: str, token: str, base_url: str):
    """Construye y envía el correo electrónico con un diseño HTML corporativo responsivo."""
    verification_link = f"{base_url}/usuarios/verificar-email?token={token}"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                background-color: #F7F9FB;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 40px auto;
                background-color: #ffffff;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 4px 15px rgba(0,0,0,0.05);
                border: 1px solid #E2E8F0;
            }}
            .header {{ background-color: #006875; padding: 32px; text-align: center; }}
            .header h1 {{ color: #ffffff; margin: 0; font-size: 24px; letter-spacing: 1px; }}
            .content {{ padding: 40px 32px; color: #3B494C; line-height: 1.6; }}
            .content h2 {{ color: #191C1E; font-size: 20px; margin-top: 0; }}
            .btn-container {{ text-align: center; margin: 40px 0; }}
            .btn {{
                background-color: #006C49;
                color: #ffffff;
                padding: 14px 32px;
                text-decoration: none;
                border-radius: 6px;
                font-weight: bold;
                display: inline-block;
            }}
            .footer {{
                background-color: #F2F4F6;
                padding: 24px;
                text-align: center;
                font-size: 12px;
                color: #6B7A7D;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>ECOTUR ASOPRADO</h1>
            </div>
            <div class="content">
                <h2>¡Hola, {first_name}!</h2>
                <p>Gracias por unirte a Ecotur Asoprado. Estás a un solo paso de descubrir las
                mejores experiencias bioculturales que tenemos para ti desde Prado, Tolima.</p>
                <p>Para garantizar la seguridad de tu cuenta y activar tu acceso, por favor
                verifica tu dirección de correo electrónico haciendo clic en el siguiente botón:</p>

                <div class="btn-container">
                    <a href="{verification_link}" class="btn"
                        style="color: #ffffff !important;
                        text-decoration: none;">Verificar mi Cuenta</a>
                </div>

                <p>Si el botón no funciona, copia y pega este enlace en tu navegador:</p>
                <p style="font-size: 12px; color: #006875;
                    word-break: break-all;">{verification_link}</p>
                <p><i>Este enlace expirará en 15 minutos.</i></p>
            </div>
            <div class="footer">
                <p>© 2026 Ecotur Asoprado. Todos los derechos reservados.</p>
                <p>Si no solicitaste este registro, puedes ignorar este correo.</p>
            </div>
        </div>
    </body>
    </html>
    """

    message = MessageSchema(
        subject="Verifica tu cuenta de Ecotur Asoprado",
        recipients=[email_to],
        body=html_content,
        subtype=MessageType.html,
    )

    await fast_mail.send_message(message)
