import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(to_email, subject, html_body):
    """Send an email via Gmail SMTP."""
    smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_user = os.getenv('SMTP_USER', '')
    smtp_pass = os.getenv('SMTP_PASSWORD', '')
    from_name = os.getenv('EMAIL_FROM_NAME', 'Ray Solar Solutions')
    from_email = os.getenv('EMAIL_FROM_ADDRESS', smtp_user)

    if not smtp_user or not smtp_pass:
        print(f'[EMAIL SKIPPED] No SMTP credentials. Would send "{subject}" to {to_email}')
        return False

    msg = MIMEMultipart('alternative')
    msg['From'] = f'{from_name} <{from_email}>'
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(html_body, 'html'))

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(from_email, to_email, msg.as_string())
        print(f'[EMAIL SENT] "{subject}" to {to_email}')
        return True
    except Exception as e:
        print(f'[EMAIL ERROR] {e}')
        return False


def send_verification_email(to_email, token, frontend_url):
    """Send email verification link."""
    verify_url = f'{frontend_url}/verify-email?token={token}'
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 500px; margin: 0 auto; padding: 30px;">
      <div style="text-align: center; margin-bottom: 30px;">
        <span style="font-size: 32px;">&#9728;</span>
        <h2 style="color: #10162b; margin-top: 10px;">Ray Solar Solutions</h2>
      </div>
      <div style="background: #faf6ee; border-radius: 16px; padding: 30px;">
        <h2 style="color: #10162b; margin-top: 0;">Verify your email</h2>
        <p style="color: #4a5565; line-height: 1.6;">
          Thanks for signing up! Click the button below to verify your email address and activate your account.
        </p>
        <a href="{verify_url}"
           style="display: inline-block; background: #f5a623; color: white; padding: 14px 32px; border-radius: 12px; text-decoration: none; font-weight: bold; margin: 20px 0;">
          Verify Email
        </a>
        <p style="color: #4a5565; font-size: 13px;">
          If you didn't create an account, you can ignore this email.
        </p>
      </div>
      <p style="text-align: center; color: #999; font-size: 12px; margin-top: 20px;">
        &copy; 2026 Ray Solar Solutions. Powered by clean energy.
      </p>
    </div>
    """
    return send_email(to_email, 'Verify your email - Ray Solar Solutions', html)


def send_password_reset_email(to_email, token, frontend_url):
    """Send password reset link."""
    reset_url = f'{frontend_url}/reset-password?token={token}'
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 500px; margin: 0 auto; padding: 30px;">
      <div style="text-align: center; margin-bottom: 30px;">
        <span style="font-size: 32px;">&#9728;</span>
        <h2 style="color: #10162b; margin-top: 10px;">Ray Solar Solutions</h2>
      </div>
      <div style="background: #faf6ee; border-radius: 16px; padding: 30px;">
        <h2 style="color: #10162b; margin-top: 0;">Reset your password</h2>
        <p style="color: #4a5565; line-height: 1.6;">
          We received a request to reset your password. Click the button below to set a new one.
        </p>
        <a href="{reset_url}"
           style="display: inline-block; background: #f5a623; color: white; padding: 14px 32px; border-radius: 12px; text-decoration: none; font-weight: bold; margin: 20px 0;">
          Reset Password
        </a>
        <p style="color: #4a5565; font-size: 13px;">
          This link expires in 1 hour. If you didn't request this, you can safely ignore this email.
        </p>
      </div>
      <p style="text-align: center; color: #999; font-size: 12px; margin-top: 20px;">
        &copy; 2026 Ray Solar Solutions. Powered by clean energy.
      </p>
    </div>
    """
    return send_email(to_email, 'Reset your password - Ray Solar Solutions', html)


def send_order_confirmation_email(to_email, order):
    """Send order confirmation email."""
    items_html = ''
    for item in order.get('items', []):
        items_html += f"""
        <tr>
          <td style="padding: 8px 0; color: #4a5565; border-bottom: 1px solid #eee;">{item.get('name', 'Product')}</td>
          <td style="padding: 8px 0; color: #4a5565; border-bottom: 1px solid #eee; text-align: center;">{item.get('quantity', 1)}</td>
          <td style="padding: 8px 0; color: #4a5565; border-bottom: 1px solid #eee; text-align: right;">KSh {item.get('total', 0):,}</td>
        </tr>
        """

    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 500px; margin: 0 auto; padding: 30px;">
      <div style="text-align: center; margin-bottom: 30px;">
        <span style="font-size: 32px;">&#9728;</span>
        <h2 style="color: #10162b; margin-top: 10px;">Ray Solar Solutions</h2>
      </div>
      <div style="background: #faf6ee; border-radius: 16px; padding: 30px;">
        <h2 style="color: #10162b; margin-top: 0;">Order Confirmed!</h2>
        <p style="color: #4a5565;">Order <strong>#{order.get('order_number', '')}</strong></p>
        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
          <thead>
            <tr style="border-bottom: 2px solid #10162b;">
              <th style="padding: 8px 0; text-align: left; color: #10162b;">Item</th>
              <th style="padding: 8px 0; text-align: center; color: #10162b;">Qty</th>
              <th style="padding: 8px 0; text-align: right; color: #10162b;">Total</th>
            </tr>
          </thead>
          <tbody>{items_html}</tbody>
        </table>
        <div style="border-top: 2px solid #10162b; padding-top: 12px; text-align: right;">
          <strong style="color: #10162b; font-size: 18px;">KSh {order.get('total_amount', 0):,}</strong>
        </div>
        <p style="color: #4a5565; margin-top: 20px; line-height: 1.6;">
          We'll send you an update when your order ships. You can track your order in the app.
        </p>
      </div>
      <p style="text-align: center; color: #999; font-size: 12px; margin-top: 20px;">
        &copy; 2026 Ray Solar Solutions. Powered by clean energy.
      </p>
    </div>
    """
    return send_email(to_email, f'Order Confirmed - #{order.get("order_number", "")}', html)


def send_order_status_email(to_email, order_number, status):
    """Send order status update email."""
    status_messages = {
        'confirmed': 'Your order has been confirmed and is being prepared.',
        'shipped': 'Your order has been shipped and is on its way!',
        'delivered': 'Your order has been delivered. Enjoy your solar products!',
        'cancelled': 'Your order has been cancelled.',
    }
    message = status_messages.get(status, f'Your order status has been updated to {status}.')
    status_title = status.replace('_', ' ').title()

    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 500px; margin: 0 auto; padding: 30px;">
      <div style="text-align: center; margin-bottom: 30px;">
        <span style="font-size: 32px;">&#9728;</span>
        <h2 style="color: #10162b; margin-top: 10px;">Ray Solar Solutions</h2>
      </div>
      <div style="background: #faf6ee; border-radius: 16px; padding: 30px;">
        <h2 style="color: #10162b; margin-top: 0;">Order Update</h2>
        <p style="color: #4a5565;">Order <strong>#{order_number}</strong></p>
        <div style="background: white; border-radius: 12px; padding: 16px; margin: 20px 0; text-align: center;">
          <span style="font-size: 14px; font-weight: bold; color: #f5a623; text-transform: uppercase;">{status_title}</span>
        </div>
        <p style="color: #4a5565; line-height: 1.6;">{message}</p>
      </div>
      <p style="text-align: center; color: #999; font-size: 12px; margin-top: 20px;">
        &copy; 2026 Ray Solar Solutions. Powered by clean energy.
      </p>
    </div>
    """
    return send_email(to_email, f'Order {status_title} - #{order_number}', html)
