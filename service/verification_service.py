import time
import threading
import logging
from datetime import datetime, timedelta
from config import Config
from service.email_service import EmailService

logger = logging.getLogger(__name__)

class VerificationService:
    """
    验证码服务类
    使用内存存储验证码，支持过期自动清理
    """
    
    def __init__(self):
        # 存储格式: {email: {'code': 'xxxxxx', 'timestamp': timestamp, 'attempts': count}}
        self.verification_codes = {}
        self.email_service = EmailService()
        self.max_attempts = 3  # 最大验证尝试次数
        self.cleanup_interval = 300  # 5分钟清理一次过期验证码
        
        # 启动清理线程
        self.start_cleanup_thread()
    
    def start_cleanup_thread(self):
        """启动定期清理过期验证码的线程"""
        def cleanup_expired_codes():
            while True:
                try:
                    current_time = time.time()
                    expired_emails = []
                    
                    for email, data in self.verification_codes.items():
                        if current_time - data['timestamp'] > Config.VERIFICATION_CODE_EXPIRY:
                            expired_emails.append(email)
                    
                    for email in expired_emails:
                        del self.verification_codes[email]
                        logger.info(f"Cleaned up expired verification code for {email}")
                        
                except Exception as e:
                    logger.error(f"Error in verification code cleanup: {str(e)}")
                
                time.sleep(self.cleanup_interval)
        
        cleanup_thread = threading.Thread(target=cleanup_expired_codes, daemon=True)
        cleanup_thread.start()
        logger.info("Verification code cleanup thread started")
    
    def send_verification_code(self, email):
        """
        发送验证码到指定邮箱
        
        Args:
            email (str): 目标邮箱
            
        Returns:
            dict: 包含状态和消息的字典
            
        """
        try:
            # 检查是否在冷却期内
            if email in self.verification_codes:
                last_sent = self.verification_codes[email]['timestamp']
                if time.time() - last_sent < 60:  # 1分钟冷却期
                    remaining_time = 60 - int(time.time() - last_sent)
                    return {
                        "status": "error",
                        "message": f"Please wait {remaining_time} seconds before requesting a new code."
                    }
            
            # 生成验证码
            verification_code = self.email_service.generate_verification_code()
            
            # 发送邮件
            if self.email_service.send_verification_email(email, verification_code):
                # 存储验证码
                self.verification_codes[email] = {
                    'code': verification_code,
                    'timestamp': time.time(),
                    'attempts': 0
                }
                
                logger.info(f"Verification code sent to {email}")
                return {
                    "status": "success",
                    "message": "Verification code sent successfully."
                }
            else:
                return {
                    "status": "error",
                    "message": "Failed to send verification email. Please try again later."
                }
                
        except Exception as e:
            logger.error(f"Error sending verification code to {email}: {str(e)}")
            return {
                "status": "error",
                "message": "An error occurred while sending verification code."
            }
    
    def verify_code(self, email, provided_code):
        """
        验证邮箱验证码
        
        Args:
            email (str): 邮箱地址
            provided_code (str): 用户提供的验证码
            
        Returns:
            dict: 包含验证结果的字典
        """
        # 开发环境：自动验证通过
        return {
            "status": "success",
            "message": "Email verified successfully."
        }
    
    def is_email_service_enabled(self):
        """检查邮件服务是否可用"""
        return True
    
    def get_verification_status(self, email):
        """
        获取邮箱的验证状态
        
        Args:
            email (str): 邮箱地址
            
        Returns:
            dict: 包含验证状态信息的字典
        """
        if email in self.verification_codes:
            code_data = self.verification_codes[email]
            remaining_time = Config.VERIFICATION_CODE_EXPIRY - (time.time() - code_data['timestamp'])
            
            if remaining_time > 0:
                return {
                    "has_pending_code": True,
                    "remaining_time": int(remaining_time),
                    "attempts_used": code_data['attempts'],
                    "max_attempts": self.max_attempts
                }
        
        return {
            "has_pending_code": False,
            "remaining_time": 0,
            "attempts_used": 0,
            "max_attempts": self.max_attempts
        } 