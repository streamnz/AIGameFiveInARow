#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ai.llama3_ai import Llama3AI

def create_test_board():
    """创建测试棋盘，模拟图片中的情况"""
    # 创建15x15的空棋盘
    board = [['' for _ in range(15)] for _ in range(15)]
    
    # 根据图片设置棋子位置
    # 白子连成4个（第7行，从第4列到第7列）
    board[7][4] = 'white'
    board[7][5] = 'white' 
    board[7][6] = 'white'
    board[7][7] = 'white'
    
    # 黑子位置
    board[6][0] = 'black'  # 左上角的黑子
    board[7][0] = 'black'  # 左边的黑子
    board[7][1] = 'black'
    board[7][2] = 'black'
    board[7][3] = 'black'
    board[7][9] = 'black'  # 右边的黑子
    
    return board

def print_board(board):
    """打印棋盘"""
    print("   " + " ".join([f"{i:2d}" for i in range(15)]))
    for i, row in enumerate(board):
        row_str = f"{i:2d} "
        for j, cell in enumerate(row):
            if cell == 'black':
                row_str += ' B'
            elif cell == 'white':
                row_str += ' W'
            else:
                row_str += ' .'
        print(row_str)

def test_threat_detection():
    """测试威胁检测"""
    print("=== 威胁检测测试 ===")
    
    # 创建测试棋盘
    board = create_test_board()
    print("测试棋盘:")
    print_board(board)
    
    # 创建AI实例
    ai = Llama3AI()
    
    # 测试黑子（AI）的威胁检测
    print("\n=== 黑子（AI）视角分析 ===")
    threats, opportunities = ai._analyze_threats(board, 'black')
    
    print(f"检测到威胁: {len(threats)} 个")
    for i, (x, y, count, desc) in enumerate(threats):
        print(f"  威胁{i+1}: ({x},{y}) - {desc}")
        
    print(f"检测到机会: {len(opportunities)} 个")
    for i, (x, y, count, desc) in enumerate(opportunities):
        print(f"  机会{i+1}: ({x},{y}) - {desc}")
    
    # 测试策略决策
    print("\n=== 策略决策测试 ===")
    strategic_move = ai._get_best_move_by_strategy(board, 'black')
    if strategic_move:
        x, y = strategic_move
        print(f"策略建议: ({x}, {y})")
        
        # 验证这个位置是否能有效封堵
        if (x, y) == (7, 8):  # 白子右边
            print("✅ 正确！建议在白子右边封堵")
        elif (x, y) == (7, 3):  # 白子左边（但已被黑子占据）
            print("❌ 错误！建议位置已被占据")
        else:
            print(f"🤔 建议位置: ({x}, {y})，需要验证是否合理")
    else:
        print("❌ 没有找到策略建议")

if __name__ == "__main__":
    test_threat_detection() 