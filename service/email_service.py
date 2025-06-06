import boto3
import random
import string
import logging
from botocore.exceptions import ClientError
from config import Config

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        """Initialize AWS SES client"""
        try:
            if Config.AWS_ACCESS_KEY_ID and Config.AWS_SECRET_ACCESS_KEY:
                self.ses_client = boto3.client(
                    'ses',
                    aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
                    region_name=Config.AWS_REGION
                )
                self.from_email = Config.SES_FROM_EMAIL
                self.enabled = True
            else:
                logger.warning("AWS SES credentials not configured. Email verification disabled.")
                self.enabled = False
        except Exception as e:
            logger.error(f"Failed to initialize AWS SES client: {str(e)}")
            self.enabled = False
    
    def generate_verification_code(self, length=6):
        """Generate a random verification code"""
        return ''.join(random.choices(string.digits, k=length))
    
    def send_verification_email(self, to_email, verification_code):
        """Send verification code email using AWS SES"""
        if not self.enabled:
            logger.error("Email service is not enabled. Cannot send verification email.")
            return False
        
        if not self.from_email:
            logger.error("SES_FROM_EMAIL not configured. Cannot send verification email.")
            return False
        
        subject = "StreamNZ - Email Verification Code"
        
        # HTML email body with modern design
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Email Verification</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f8f9fa;
                }}
                .email-container {{
                    background: #ffffff;
                    border-radius: 16px;
                    padding: 40px;
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .logo {{
                    font-size: 24px;
                    font-weight: 700;
                    background: linear-gradient(135deg, #8B5CF6 0%, #06B6D4 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                    margin-bottom: 10px;
                }}
                .verification-code {{
                    background: linear-gradient(135deg, #8B5CF6 0%, #06B6D4 100%);
                    color: white;
                    font-size: 32px;
                    font-weight: 700;
                    text-align: center;
                    padding: 20px;
                    border-radius: 12px;
                    letter-spacing: 4px;
                    margin: 30px 0;
                    box-shadow: 0 8px 25px rgba(139, 92, 246, 0.3);
                }}
                .content {{
                    text-align: center;
                    font-size: 16px;
                    line-height: 1.6;
                }}
                .footer {{
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #e5e7eb;
                    text-align: center;
                    font-size: 14px;
                    color: #6b7280;
                }}
                .warning {{
                    background: rgba(239, 68, 68, 0.1);
                    border: 1px solid rgba(239, 68, 68, 0.2);
                    border-radius: 8px;
                    padding: 16px;
                    margin: 20px 0;
                    color: #dc2626;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <div class="logo">StreamNZ</div>
                    <h2>Email Verification</h2>
                </div>
                
                <div class="content">
                    <p>Welcome to StreamNZ! Please use the verification code below to complete your registration:</p>
                    
                    <div class="verification-code">
                        {verification_code}
                    </div>
                    
                    <p>This code will expire in 10 minutes for security reasons.</p>
                    
                    <div class="warning">
                        <strong>Security Notice:</strong> If you didn't request this verification code, please ignore this email. Never share your verification code with anyone.
                    </div>
                </div>
                
                <div class="footer">
                    <p>This is an automated message from StreamNZ. Please do not reply to this email.</p>
                    <p>&copy; 2024 StreamNZ. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text version
        text_body = f"""
        StreamNZ - Email Verification
        
        Welcome to StreamNZ!
        
        Your verification code is: {verification_code}
        
        This code will expire in 10 minutes.
        
        If you didn't request this verification code, please ignore this email.
        
        StreamNZ Team
        """
        
        try:
            response = self.ses_client.send_email(
                Destination={
                    'ToAddresses': [to_email],
                },
                Message={
                    'Body': {
                        'Html': {
                            'Charset': 'UTF-8',
                            'Data': html_body,
                        },
                        'Text': {
                            'Charset': 'UTF-8',
                            'Data': text_body,
                        },
                    },
                    'Subject': {
                        'Charset': 'UTF-8',
                        'Data': subject,
                    },
                },
                Source=self.from_email,
            )
            
            logger.info(f"Verification email sent successfully to {to_email}. Message ID: {response['MessageId']}")
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"AWS SES error sending email to {to_email}: {error_code} - {error_message}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending email to {to_email}: {str(e)}")
            return False
    
    def is_email_verified_in_ses(self, email):
        """Check if email is verified in AWS SES (for development/testing)"""
        if not self.enabled:
            return True  # Skip verification if SES is not enabled
        
        try:
            response = self.ses_client.get_identity_verification_attributes(
                Identities=[email]
            )
            
            verification_attrs = response.get('VerificationAttributes', {})
            email_attrs = verification_attrs.get(email, {})
            
            return email_attrs.get('VerificationStatus') == 'Success'
        except Exception as e:
            logger.warning(f"Could not check email verification status: {str(e)}")
            return True  # Assume verified if we can't check 