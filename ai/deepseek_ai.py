import requests
import json
import os
import re
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class DeepSeekAI:
    def __init__(self):
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def _create_prompt(self, board, current_player):
        """创建发送给 DeepSeek 的提示"""
        # 生成二维数组
        arr = [[0 if cell == '' else 1 if cell == 'black' else 2 for cell in row] for row in board]
        arr_str = "\n".join([f"{i}: {row}" for i, row in enumerate(arr)])
        # 生成空位坐标列表
        empty = [(i, j) for i in range(15) for j in range(15) if board[i][j] == '']
        prompt = f"""
你是一个五子棋AI。
规则：
- 棋盘为15x15，双方轮流落子。
- 任意一方在横向、纵向或斜向连成5个相同颜色的棋子即获胜。
- 如果棋盘下满且无人连成5子，则为平局。
- 你执{'黑' if current_player == 'black' else '白'}。

你的目标是：想尽一切办法取得胜利！你需要主动进攻，积极寻找获胜机会，同时防止对手形成五连。

五子棋常用攻防策略：
- 主动创造"活四"（四连且两端都为空）或"冲四"（四连一端被堵，另一端为空），优先选择能形成活四的位置。
- 如果对方有"活四"或"冲四"，必须优先封堵。
- 主动创造"活三"（三连且两端都为空），为后续形成活四做准备。
- 不要让对方形成连续四子且两端都没有我方棋子（避免被对方活四或冲四）。
- 如果有机会形成"双三"或"双四"威胁（同时出现两个活三或活四），优先选择。
- 进攻时优先考虑中心和关键点，防守时优先封堵对方潜在连子。

棋盘如下（二维数组，0为空，1为黑，2为白）：
行号/列号:  0  1  2 ... 14
{arr_str}
数组的第i行第j列对应棋盘的(i,j)坐标。

空位坐标列表（只能从中选择）: {empty}

请只从空位坐标中选择一个，返回你要落子的坐标，格式为(x,y)，不要输出任何解释或多余内容。
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
        """获取 DeepSeek AI 的下一步移动"""
        try:
            prompt = self._create_prompt(board, current_player)
            print(f"\n当前棋盘状态：\n{self._board_to_string(board)}")
            print(f"当前玩家：{current_player}")
            print(f"发送给 DeepSeek 的提示：\n{prompt}")
            
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "你是一个五子棋AI，只返回你要落子的坐标，格式为(x,y)，不要输出任何解释。"},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 100
            }

            response = requests.post(self.api_url, headers=self.headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            move_text = result['choices'][0]['message']['content'].strip()
            print(f"DeepSeek AI 响应: {move_text}")
            
            # 提取坐标
            match = re.search(r'\((\d+),\s*(\d+)\)', move_text)
            if match:
                x, y = int(match.group(1)), int(match.group(2))
                print(f"解析出的坐标: ({x}, {y})")
                
                # 详细的坐标验证
                if not (0 <= x <= 14 and 0 <= y <= 14):
                    print(f"坐标超出范围：x={x}, y={y}，坐标必须在0-14之间")
                    new_x, new_y = self._find_valid_position(board)
                    print(f"找到替代位置: ({new_x}, {new_y})")
                    return new_x, new_y
                
                if board[x][y] != '':
                    print(f"位置已被占用：board[{x}][{y}]={board[x][y]}")
                    print("当前棋盘状态：")
                    for i in range(15):
                        for j in range(15):
                            if board[i][j] != '':
                                print(f"位置({i},{j})已被{board[i][j]}占用")
                    new_x, new_y = self._find_valid_position(board)
                    print(f"找到替代位置: ({new_x}, {new_y})")
                    return new_x, new_y
                
                print(f"坐标有效，返回 ({x}, {y})")
                return x, y
            
            # 如果没有找到有效坐标，使用智能寻找替代位置
            print("未找到有效坐标，使用智能寻找替代位置...")
            new_x, new_y = self._find_valid_position(board)
            print(f"找到替代位置: ({new_x}, {new_y})")
            return new_x, new_y
            
        except Exception as e:
            print(f"Error in get_move: {str(e)}")
            # 发生错误时也使用智能寻找替代位置
            new_x, new_y = self._find_valid_position(board)
            print(f"发生错误，使用替代位置: ({new_x}, {new_y})")
            return new_x, new_y 