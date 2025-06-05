#!/usr/bin/env python3
"""
配置检查脚本：验证所有必需的环境变量是否正确配置
"""

import os
from dotenv import load_dotenv

def check_config():
    """检查配置是否完整"""
    print("🔍 开始检查项目配置...")
    
    # 加载 .env 文件
    load_dotenv()
    
    # 必需的环境变量
    required_vars = {
        'MYSQL_HOST': '数据库主机地址',
        'MYSQL_PORT': '数据库端口',
        'MYSQL_DATABASE': '数据库名称',
        'MYSQL_USER': '数据库用户名',
        'MYSQL_ENCRYPTED_PASSWORD': '加密的数据库密码',
        'MYSQL_DB_KEY': '数据库密码加密密钥',
        'DEEPSEEK_API_KEY': 'DeepSeek API 密钥',
        'FLASK_SECRET_KEY': 'Flask 密钥',
        'FLASK_DEBUG': 'Flask 调试模式'
    }
    
    print("\n📋 检查环境变量:")
    missing_vars = []
    configured_vars = []
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            if var == 'DEEPSEEK_API_KEY':
                # 隐藏API密钥，只显示前几位
                display_value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
            elif 'PASSWORD' in var or 'KEY' in var:
                display_value = "***已配置***"
            else:
                display_value = value
            print(f"✅ {var}: {display_value} ({description})")
            configured_vars.append(var)
        else:
            print(f"❌ {var}: 未配置 ({description})")
            missing_vars.append(var)
    
    print(f"\n📊 配置统计:")
    print(f"✅ 已配置: {len(configured_vars)}/{len(required_vars)}")
    print(f"❌ 缺失: {len(missing_vars)}")
    
    if missing_vars:
        print(f"\n⚠️ 缺失的配置项:")
        for var in missing_vars:
            print(f"   - {var}: {required_vars[var]}")
        
        print(f"\n📝 解决方案:")
        if 'DEEPSEEK_API_KEY' in missing_vars:
            print("1. 访问 https://platform.deepseek.com 获取 API 密钥")
        print("2. 在项目根目录的 .env 文件中添加缺失的配置")
        print("3. 重新运行此检查脚本")
        
        return False
    else:
        print("\n🎉 所有配置都已正确设置！")
        
        # 测试数据库密码解密
        try:
            from cryptography.fernet import Fernet
            db_key = os.getenv('MYSQL_DB_KEY')
            encrypted_password = os.getenv('MYSQL_ENCRYPTED_PASSWORD')
            
            cipher_suite = Fernet(db_key.encode())
            decrypted_password = cipher_suite.decrypt(encrypted_password.encode()).decode()
            print("✅ 数据库密码解密测试成功")
        except Exception as e:
            print(f"❌ 数据库密码解密测试失败: {e}")
            return False
            
        print("\n🚀 项目配置验证完成，可以启动应用！")
        return True

def main():
    """主函数"""
    success = check_config()
    
    if success:
        print("\n💡 下一步：")
        print("   python app.py  # 启动应用")
    else:
        print("\n💡 请先完成配置后再启动应用")

if __name__ == "__main__":
    main() 