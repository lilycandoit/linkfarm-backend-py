"""
Email Service using Resend
Handles sending transactional emails to farmers
"""
import os
import resend
from flask import current_app

# Configure Resend with API key from environment
resend.api_key = os.getenv('RESEND_API_KEY')

def send_inquiry_notification(farmer_email: str, farmer_name: str, inquiry_data: dict) -> bool:
    """
    Send email notification to farmer when they receive a new inquiry.

    Args:
        farmer_email: Farmer's email address
        farmer_name: Farmer's name for personalization
        inquiry_data: Dictionary containing inquiry details
            - customer_name: Name of the customer
            - customer_phone: Customer's phone number
            - product_name: Name of the product
            - message: Customer's message

    Returns:
        bool: True if email sent successfully, False otherwise
    """

    # Check if Resend is configured
    if not resend.api_key:
        current_app.logger.warning('RESEND_API_KEY not configured. Email notification skipped.')
        return False

    try:
        # Extract inquiry details
        customer_name = inquiry_data.get('customer_name', 'A customer')
        customer_phone = inquiry_data.get('customer_phone', 'Not provided')
        product_name = inquiry_data.get('product_name', 'your product')
        message = inquiry_data.get('message', 'No message provided')

        # Compose email
        params = {
            "from": "LinkFarm <onboarding@resend.dev>",  # Resend's development email (no verification needed)
            "to": [farmer_email],
            "subject": f"🌾 New Inquiry: {customer_name} is interested in {product_name}",
            "html": f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #10b981; color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
        .content {{ background-color: #f9fafb; padding: 20px; border: 1px solid #e5e7eb; }}
        .detail {{ margin: 10px 0; padding: 10px; background-color: white; border-left: 4px solid #10b981; }}
        .detail strong {{ color: #10b981; }}
        .footer {{ margin-top: 20px; padding: 15px; background-color: #f3f4f6; border-radius: 0 0 8px 8px; text-align: center; font-size: 12px; color: #6b7280; }}
        .cta {{ display: inline-block; margin-top: 15px; padding: 12px 24px; background-color: #10b981; color: white; text-decoration: none; border-radius: 6px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>🌾 New Customer Inquiry!</h2>
        </div>
        <div class="content">
            <p>Hi {farmer_name},</p>
            <p>Great news! You've received a new inquiry from a customer interested in your product.</p>

            <div class="detail">
                <strong>👤 Customer:</strong> {customer_name}
            </div>
            <div class="detail">
                <strong>📞 Phone:</strong> {customer_phone}
            </div>
            <div class="detail">
                <strong>🛒 Product:</strong> {product_name}
            </div>
            <div class="detail">
                <strong>💬 Message:</strong><br>
                {message}
            </div>

            <p style="margin-top: 20px;">
                <strong>Next Steps:</strong><br>
                Contact the customer at <strong>{customer_phone}</strong> to discuss their inquiry and arrange purchase details.
            </p>

            <center>
                <a href="http://localhost:5173/dashboard" class="cta">View in Dashboard</a>
            </center>
        </div>
        <div class="footer">
            <p>This email was sent by <strong>LinkFarm</strong> - Connecting local farmers with customers</p>
            <p>You received this email because you're a registered farmer on LinkFarm.</p>
        </div>
    </div>
</body>
</html>
            """,
        }

        # Send email via Resend
        email = resend.Emails.send(params)
        current_app.logger.info(f'Inquiry notification sent to {farmer_email}. Email ID: {email["id"]}')
        return True

    except Exception as e:
        current_app.logger.error(f'Failed to send inquiry notification: {str(e)}')
        return False


def send_welcome_email(farmer_email: str, farmer_name: str) -> bool:
    """
    Send welcome email to new farmers when they create their profile.

    Args:
        farmer_email: Farmer's email address
        farmer_name: Farmer's name

    Returns:
        bool: True if email sent successfully, False otherwise
    """

    if not resend.api_key:
        current_app.logger.warning('RESEND_API_KEY not configured. Welcome email skipped.')
        return False

    try:
        params = {
            "from": "LinkFarm <onboarding@resend.dev>",
            "to": [farmer_email],
            "subject": "🌾 Welcome to LinkFarm!",
            "html": f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #10b981; color: white; padding: 30px; border-radius: 8px 8px 0 0; text-align: center; }}
        .content {{ background-color: #f9fafb; padding: 30px; border: 1px solid #e5e7eb; }}
        .cta {{ display: inline-block; margin-top: 20px; padding: 12px 24px; background-color: #10b981; color: white; text-decoration: none; border-radius: 6px; }}
        .footer {{ margin-top: 20px; padding: 15px; background-color: #f3f4f6; border-radius: 0 0 8px 8px; text-align: center; font-size: 12px; color: #6b7280; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Welcome to LinkFarm! 🌾</h1>
        </div>
        <div class="content">
            <p>Hi {farmer_name},</p>
            <p>We're excited to have you join the LinkFarm community! 🎉</p>
            <p>LinkFarm connects local farmers directly with customers who value fresh, quality produce. You can now start listing your products and reaching customers in your area.</p>

            <p><strong>Get Started:</strong></p>
            <ul>
                <li>Add your products to the marketplace</li>
                <li>Receive inquiries from interested customers</li>
                <li>Connect directly via phone or messenger</li>
                <li>Build lasting relationships with your customers</li>
            </ul>

            <center>
                <a href="http://localhost:5173/dashboard" class="cta">Go to Dashboard</a>
            </center>
        </div>
        <div class="footer">
            <p>Thank you for choosing <strong>LinkFarm</strong></p>
            <p>Empowering local farmers through direct digital connections</p>
        </div>
    </div>
</body>
</html>
            """,
        }

        email = resend.Emails.send(params)
        current_app.logger.info(f'Welcome email sent to {farmer_email}. Email ID: {email["id"]}')
        return True

    except Exception as e:
        current_app.logger.error(f'Failed to send welcome email: {str(e)}')
        return False
