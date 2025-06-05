import os
from dotenv import load_dotenv
from openai import OpenAI
import re

# 加载环境变量
load_dotenv()

class OpenAIAI:
    def __init__(self):
        print("DEBUG: OPENAI_API_KEY =", os.getenv('OPENAI_API_KEY'))
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = "gpt-4"  # 使用 gpt-4 模型，因为 gpt-4.1 目前不可用

    def _create_prompt(self, board, current_player):
        """创建发送给 OpenAI 的提示"""
        board_str = self._board_to_string(board)
        prompt = f"""
你是一个五子棋AI。
规则：
- 棋盘为15x15，双方轮流落子。
- 任意一方在横、纵或斜方向连成5子即获胜。
- 你执{'黑' if current_player == 'black' else '白'}。

请只返回你要落子的坐标，格式为(x,y)，不要输出任何解释或多余内容。

当前棋盘（行号在左侧，列号在顶部）：
{board_str}
"""
        return prompt

    def _board_to_string(self, board):
        """将棋盘转换为字符串表示，并标注关键位置"""
        # 定义关键位置（天元和星位）
        key_positions = {
            (7, 7): '*',  # 天元
            (3, 3): '*', (3, 7): '*', (3, 11): '*',  # 左上、中上、右上星位
            (7, 3): '*', (7, 11): '*',  # 左中、右中星位
            (11, 3): '*', (11, 7): '*', (11, 11): '*'  # 左下、中下、右下星位
        }
        
        board_str = "   " + " ".join([f"{i:2d}" for i in range(15)]) + "\n"
        for i, row in enumerate(board):
            row_str = f"{i:2d} "
            for j, cell in enumerate(row):
                if (i, j) in key_positions:
                    if cell == 'black':
                        row_str += ' B'
                    elif cell == 'white':
                        row_str += ' W'
                    else:
                        row_str += ' *'
                else:
                    if cell == 'black':
                        row_str += ' B'
                    elif cell == 'white':
                        row_str += ' W'
                    else:
                        row_str += ' .'
            board_str += row_str + "\n"
        return board_str

    def _find_valid_position(self, board):
        """智能寻找一个有效的落子位置"""
        # 定义优先级区域（从中心向外扩展）
        priority_areas = [
            (7, 7),  # 天元
            (3, 3), (3, 7), (3, 11),  # 星位
            (7, 3), (7, 11),
            (11, 3), (11, 7), (11, 11)
        ]
        
        # 首先检查优先级位置
        for x, y in priority_areas:
            if board[x][y] == '':
                return x, y
        
        # 检查对手的威胁
        opponent = 'white' if any('black' in row for row in board) else 'black'
        for i in range(15):
            for j in range(15):
                if board[i][j] == '':
                    # 检查这个位置是否能形成威胁
                    if self._is_threatening_position(board, i, j, opponent):
                        return i, j
        
        # 如果找不到威胁位置，从中心向外寻找空位
        center = 7
        for distance in range(8):
            for i in range(max(0, center - distance), min(15, center + distance + 1)):
                for j in range(max(0, center - distance), min(15, center + distance + 1)):
                    if board[i][j] == '':
                        return i, j
        
        return 7, 7  # 默认返回中心位置

    def _is_threatening_position(self, board, x, y, player):
        """检查位置是否具有威胁性"""
        # 临时放置棋子
        board[x][y] = player
        
        # 检查是否能形成活四、冲四或活三
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dx, dy in directions:
            count = 1
            # 向一个方向检查
            i, j = x + dx, y + dy
            while 0 <= i < 15 and 0 <= j < 15 and board[i][j] == player:
                count += 1
                i += dx
                j += dy
            
            # 向相反方向检查
            i, j = x - dx, y - dy
            while 0 <= i < 15 and 0 <= j < 15 and board[i][j] == player:
                count += 1
                i -= dx
                j -= dy
            
            if count >= 3:  # 如果能形成活三或更多
                board[x][y] = ''  # 恢复棋盘状态
                return True
        
        board[x][y] = ''  # 恢复棋盘状态
        return False

    def get_move(self, board, current_player):
        """获取 OpenAI AI 的下一步移动"""
        try:
            prompt = self._create_prompt(board, current_player)
            print(f"\n当前棋盘状态：\n{self._board_to_string(board)}")
            print(f"当前玩家：{current_player}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的五子棋AI，请仔细分析棋局并返回最佳落子坐标。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=100
            )
            
            # 从响应中提取坐标
            move_text = response.choices[0].message.content.strip()
            print(f"AI返回的原始文本: {move_text}")
            
            # 使用正则表达式提取坐标
            match = re.search(r'\((\d+),\s*(\d+)\)', move_text)
            if match:
                x, y = map(int, match.groups())
                print(f"解析出的坐标: ({x}, {y})")
                
                # 验证坐标是否有效
                if 0 <= x < 15 and 0 <= y < 15 and board[x][y] == '':
                    return x, y
                else:
                    print(f"坐标 ({x}, {y}) 无效或已被占用，寻找替代位置")
                    return self._find_valid_position(board)
            else:
                print("无法从AI响应中解析出有效坐标，使用替代位置")
                return self._find_valid_position(board)
                
        except Exception as e:
            print(f"Error in get_move: {str(e)}")
            print("发生错误，使用替代位置")
            return self._find_valid_position(board) 