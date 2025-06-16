#!/usr/bin/env python3
"""
测试本地 Llama3 AI 模型的脚本
"""

from ai.llama3_ai import Llama3AI

def test_llama3_ai():
    """测试 Llama3 AI 的基本功能"""
    print("=== 测试本地 Llama3 AI 模型 ===")
    
    # 初始化 AI
    ai = Llama3AI()
    
    # 创建一个空棋盘进行测试
    empty_board = [['' for _ in range(15)] for _ in range(15)]
    
    print("\n测试1: 空棋盘开局")
    try:
        x, y = ai.get_move(empty_board, 'black')
        print(f"✅ 开局落子成功: ({x}, {y})")
    except Exception as e:
        print(f"❌ 开局落子失败: {e}")
    
    # 创建一个有几个棋子的棋盘
    test_board = [['' for _ in range(15)] for _ in range(15)]
    test_board[7][7] = 'black'  # 中心有一个黑子
    test_board[7][8] = 'white'  # 旁边有一个白子
    
    print("\n测试2: 有棋子的棋盘")
    try:
        x, y = ai.get_move(test_board, 'black')
        print(f"✅ 应对落子成功: ({x}, {y})")
        if test_board[x][y] == '':
            print("✅ 落子位置有效")
        else:
            print("❌ 落子位置无效")
    except Exception as e:
        print(f"❌ 应对落子失败: {e}")

def test_api_connection():
    """测试与本地 Llama3 API 的连接"""
    print("\n=== 测试 API 连接 ===")
    
    import requests
    
    try:
        # 测试简单的请求
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": "你好，请回答：1+1=?",
                "stream": False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API 连接成功")
            print(f"响应: {result.get('response', '无响应')[:100]}...")
        else:
            print(f"❌ API 响应错误: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到本地 Llama3 服务")
        print("请确保:")
        print("1. Ollama 服务正在运行")
        print("2. Llama3 模型已下载")
        print("3. 服务运行在 localhost:11434")
    except Exception as e:
        print(f"❌ API 测试失败: {e}")

if __name__ == "__main__":
    # 首先测试 API 连接
    test_api_connection()
    
    # 然后测试 AI 功能
    test_llama3_ai()
    
    print("\n=== 使用说明 ===")
    print("要使用本地 Llama3 AI，请:")
    print("1. 确保 Ollama 服务正在运行")
    print("2. 设置环境变量: export AI_MODEL=llama3")
    print("3. 或者在代码中修改 AI_MODEL 变量")
    print("4. 重启应用程序") 