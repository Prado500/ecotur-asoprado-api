import os
from pathlib import Path
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr
from dotenv import load_dotenv

load_dotenv()

# ==========================================
#  SMTP Client Config
# ==========================================
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM", "tu_correo@gmail.com"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", 465)),
    MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.gmail.com"),
    MAIL_FROM_NAME="Ecotur Asoprado",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

fast_mail = FastMail(conf)

async def send_verification_email(email_to: EmailStr, first_name: str, token: str, base_url: str):
    """
    Construye y envía el correo electrónico con un diseño HTML corporativo responsivo.
    """
    verification_link = f"{base_url}/usuarios/verificar-email?token={token}"

    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 40px 16px; background-color: #f7f9fa; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #2d3748; -webkit-font-smoothing: antialiased;">
        <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 580px; margin: 0 auto; background-color: #ffffff; border: 1px solid #e1e4e8; border-radius: 8px; padding: 40px 32px;">
            <tr>
                <td align="center" style="padding-bottom: 28px;">
                    <h1 style="margin: 0; font-size: 22px; font-weight: 700; color: #006875; letter-spacing: 0.5px;">
                        ECOTUR ASOPRADO
                    </h1>
                </td>
            </tr>
            
            <tr>
                <td style="font-size: 15px; line-height: 1.6; color: #2d3748;">
                    <p style="margin-top: 0; margin-bottom: 16px; font-weight: 600; font-size: 17px; color: #1a202c;">
                        ¡Hola, {first_name}!
                    </p>
                    <p style="margin-bottom: 16px;">
                        Gracias por unirte a Ecotur Asoprado. Estás a un solo paso de descubrir las mejores experiencias bioculturales que tenemos para ti desde Prado, Tolima.
                    </p>
                    <p style="margin-bottom: 24px;">
                        Para garantizar la seguridad de tu cuenta y activar tu acceso, por favor verifica tu dirección de correo electrónico:
                    </p>
                    
                    <div style="margin: 28px 0;">
                        <a href="{verification_link}" style="background-color: #006875; color: #ffffff !important; padding: 12px 28px; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 14px; display: inline-block;" target="_blank">
                            Verificar mi Cuenta
                        </a>
                    </div>
                    
                    <p style="margin-bottom: 8px; font-size: 14px; color: #4a5568;">
                        Si el botón de arriba no funciona, copia y pega el siguiente enlace en tu navegador:
                    </p>
                    
                    <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 4px; padding: 12px; margin-bottom: 24px; word-break: break-all; font-size: 13px;">
                        <a href="{verification_link}" style="color: #0284c7; text-decoration: none;" target="_blank">{verification_link}</a>
                    </div>
                    
                    <p style="margin-bottom: 24px; font-size: 13px; color: #718096; font-style: italic;">
                        Este enlace expirará en 15 minutos.
                    </p>
                    
                    <p style="margin-bottom: 4px;">Gracias.</p>
                    <p style="margin-top: 0; font-weight: 600; color: #1e293b;">
                        Soporte Técnico de Ecotur Asoprado
                    </p>
                </td>
            </tr>
        </table>

        <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 580px; margin: 20px auto 0 auto;">
            <tr>
                <td align="center" style="font-size: 12px; line-height: 1.5; color: #718096; text-align: center;">
                    <p style="margin: 0 0 6px 0;">
                        © 2026 Ecotur Asoprado. Todos los derechos reservados.
                    </p>
                    <p style="margin: 0;">
                        Si no solicitaste este registro, puedes ignorar este correo de forma segura.
                    </p>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

    message = MessageSchema(
        subject="Verifica tu cuenta de Ecotur Asoprado",
        recipients=[email_to],
        body=html_content,
        subtype=MessageType.html
    )

    await fast_mail.send_message(message)

async def send_password_reset_email(email_to: EmailStr, first_name: str, token: str, base_url: str):
    """
    Construye y envía el correo electrónico para el restablecimiento de contraseña.
    """
    reset_link = f"{base_url.rstrip('/')}/restablecer-contrasena?token={token}"

    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 40px 16px; background-color: #f7f9fa; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #2d3748; -webkit-font-smoothing: antialiased;">
        <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 580px; margin: 0 auto; background-color: #ffffff; border: 1px solid #e1e4e8; border-radius: 8px; padding: 40px 32px;">
            
            <tr>
                <td align="center" style="padding-bottom: 28px;">
                    <h1 style="margin: 0; font-size: 22px; font-weight: 700; color: #006875; letter-spacing: 0.5px;">
                        ECOTUR ASOPRADO
                    </h1>
                </td>
            </tr>
         
            <tr>
                <td style="font-size: 15px; line-height: 1.6; color: #2d3748;">
                    <p style="margin-top: 0; margin-bottom: 16px; font-weight: 600; font-size: 17px; color: #1a202c;">
                        ¡Hola, {first_name}!
                    </p>
                    <p style="margin-bottom: 16px;">
                        Hemos recibido una solicitud para restablecer la contraseña de tu cuenta en Ecotur Asoprado.
                    </p>
                    <p style="margin-bottom: 24px;">
                        Haz clic en el siguiente botón para ingresar una nueva contraseña segura:
                    </p>
                    
                    <div style="margin: 28px 0;">
                        <a href="{reset_link}" style="background-color: #006875; color: #ffffff !important; padding: 12px 28px; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 14px; display: inline-block;" target="_blank">
                            Restablecer Contraseña
                        </a>
                    </div>
                    
                    <p style="margin-bottom: 8px; font-size: 14px; color: #4a5568;">
                        Si el botón de arriba no funciona, copia y pega el siguiente enlace en tu navegador:
                    </p>
                    
                    <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 4px; padding: 12px; margin-bottom: 24px; word-break: break-all; font-size: 13px;">
                        <a href="{reset_link}" style="color: #0284c7; text-decoration: none;" target="_blank">{reset_link}</a>
                    </div>
                    
                    <p style="margin-bottom: 24px; font-size: 13px; color: #718096; font-style: italic;">
                        Este enlace es de único uso y expirará en 15 minutos por razones de seguridad.
                    </p>
                    
                    <p style="margin-bottom: 4px;">Gracias.</p>
                    <p style="margin-top: 0; font-weight: 600; color: #1e293b;">
                        Soporte Técnico de Ecotur Asoprado
                    </p>
                </td>
            </tr>
        </table>

        <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 580px; margin: 20px auto 0 auto;">
            <tr>
                <td align="center" style="font-size: 12px; line-height: 1.5; color: #718096; text-align: center;">
                    <p style="margin: 0 0 6px 0;">
                        © 2026 Ecotur Asoprado. Todos los derechos reservados.
                    </p>
                    <p style="margin: 0;">
                        Si no solicitaste este cambio, puedes ignorar este mensaje de forma segura. Tu contraseña actual permanecerá sin cambios.
                    </p>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

    message = MessageSchema(
        subject="Restablecimiento de Contraseña - Ecotur Asoprado",
        recipients=[email_to],
        body=html_content,
        subtype=MessageType.html
    )

    await fast_mail.send_message(message)