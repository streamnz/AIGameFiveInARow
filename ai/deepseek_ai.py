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
你是一个五子棋AI。规则：15x15棋盘，连成5子获胜。你执{'黑' if current_player == 'black' else '白'}。

棋盘状态（0空，1黑，2白）：
{arr_str}

空位坐标：{empty}

请返回JSON格式：{{"x": 坐标x, "y": 坐标y, "analysis": "简短分析"}}
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

    def _create_few_shot_examples(self):
        """创建 Few-shot 示例，用于提高缓存命中率"""
        return [
            # 示例1：开局第一手
            {
                "role": "user", 
                "content": """你是一个五子棋AI。规则：15x15棋盘，连成5子获胜。你执黑。

棋盘状态（0空，1黑，2白）：
0: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
1: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
2: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
3: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
4: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
5: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
6: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
7: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
8: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
9: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
10: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
11: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
12: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
13: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
14: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

空位坐标：[(0, 0), (0, 1), ..., (14, 14)]

请返回JSON格式：{"x": 坐标x, "y": 坐标y}"""
            },
            {
                "role": "assistant",
                "content": '{"x": 7, "y": 7, "analysis": "开局选择天元"}'
            },
            # 示例2：第二手应对
            {
                "role": "user",
                "content": """你是一个五子棋AI。规则：15x15棋盘，连成5子获胜。你执白。

棋盘状态（0空，1黑，2白）：
0: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
1: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
2: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
3: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
4: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
5: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
6: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
7: [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0]
8: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
9: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
10: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
11: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
12: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
13: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
14: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

空位坐标：[(0, 0), (0, 1), ..., (7, 6), (7, 8), ..., (14, 14)]

请返回JSON格式：{"x": 坐标x, "y": 坐标y}"""
            },
            {
                "role": "assistant",
                "content": '{"x": 6, "y": 7, "analysis": "靠近对手形成威胁"}'
            },
            # 示例3：防守示例
            {
                "role": "user",
                "content": """你是一个五子棋AI。规则：15x15棋盘，连成5子获胜。你执白。

棋盘状态（0空，1黑，2白）：
0: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
1: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
2: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
3: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
4: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
5: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
6: [0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0]
7: [0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0]
8: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
9: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
10: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
11: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
12: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
13: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
14: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

空位坐标：[(0, 0), (0, 1), ..., (7, 5), (7, 9), ..., (14, 14)]

请返回JSON格式：{"x": 坐标x, "y": 坐标y}"""
            },
            {
                "role": "assistant",
                "content": '{"x": 9, "y": 7, "analysis": "封堵对手三连"}'
            }
        ]

    def get_move(self, board, current_player):
        """获取 DeepSeek AI 的下一步移动"""
        try:
            prompt = self._create_prompt(board, current_player)
            print(f"\n当前棋盘状态：\n{self._board_to_string(board)}")
            print(f"当前玩家：{current_player}")
            
            # 构建包含 Few-shot 示例的消息列表
            messages = [
                {"role": "system", "content": """你是一个五子棋AI专家。你必须严格按照以下JSON格式返回你的决策：

{"x": 数字, "y": 数字, "analysis": "简短分析"}

注意：
1. 必须返回具体的数字，不要使用变量
2. 坐标必须是空位
3. 只返回JSON，不要有其他内容
4. 分析内容不超过10个字"""}
            ]
            
            # 添加 Few-shot 示例
            messages.extend(self._create_few_shot_examples())
            
            # 添加当前请求
            messages.append({"role": "user", "content": prompt})
            
            data = {
                "model": "deepseek-reasoner",
                "messages": messages,
                "temperature": 0.1,
                "max_tokens": 5000,  # 使用 deepseek-reasoner 模型支持的最大值
                "top_p": 0.1,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0,
                "response_format": {"type": "json_object"},
                "return_reasoning": False  # 禁用推理过程返回
            }

            # 设置连接超时和读取超时
            response = requests.post(
                self.api_url, 
                headers=self.headers, 
                json=data, 
                timeout=(10, 60)  # (连接超时, 读取超时)
            )
            response.raise_for_status()
            
            # 获取原始响应文本
            response_text = response.text
            print(f"API 原始响应: {response_text}")
            
            # 检查缓存命中情况
            try:
                result = response.json()
                if 'usage' in result:
                    usage = result['usage']
                    cache_hit = usage.get('prompt_cache_hit_tokens', 0)
                    cache_miss = usage.get('prompt_cache_miss_tokens', 0)
                    total_prompt = usage.get('prompt_tokens', 0)
                    
                    if cache_hit > 0:
                        cache_rate = (cache_hit / total_prompt) * 100 if total_prompt > 0 else 0
                        print(f"缓存命中: {cache_hit} tokens, 未命中: {cache_miss} tokens, 命中率: {cache_rate:.1f}%")
                    else:
                        print(f"无缓存命中, 总输入: {total_prompt} tokens")
            except:
                pass
            
            # 尝试解析JSON响应
            try:
                result = response.json()
                if 'choices' in result and result['choices']:
                    message = result['choices'][0].get('message', {})
                    content = message.get('content', '').strip()
                    
                    print(f"DeepSeek AI 响应内容: {content}")
                    
                    # 尝试解析JSON内容
                    if content:
                        try:
                            move_data = json.loads(content)
                            if 'x' in move_data and 'y' in move_data:
                                x, y = int(move_data['x']), int(move_data['y'])
                                analysis = move_data.get('analysis', '无分析')
                                
                                print(f"解析出的坐标: ({x}, {y})")
                                print(f"AI 分析: {analysis}")
                                
                                # 验证坐标
                                if not (0 <= x <= 14 and 0 <= y <= 14):
                                    print(f"坐标超出范围：x={x}, y={y}")
                                    new_x, new_y = self._find_valid_position(board)
                                    print(f"找到替代位置: ({new_x}, {new_y})")
                                    return new_x, new_y
                                
                                if board[x][y] != '':
                                    print(f"位置已被占用：board[{x}][{y}]={board[x][y]}")
                                    new_x, new_y = self._find_valid_position(board)
                                    print(f"找到替代位置: ({new_x}, {new_y})")
                                    return new_x, new_y
                                
                                return x, y
                            else:
                                print("JSON中缺少必要的x和y字段")
                        except json.JSONDecodeError as e:
                            print(f"JSON解析失败: {e}")
                            print(f"清理后的内容: {content}")
                    else:
                        print("没有找到有效的响应内容")
            except Exception as e:
                print(f"响应解析失败: {e}")
                print(f"错误类型: {type(e).__name__}")
                import traceback
                print(f"错误堆栈: {traceback.format_exc()}")
            
            # 如果没有找到有效坐标，使用智能寻找替代位置
            print("未找到有效坐标，使用智能寻找替代位置...")
            new_x, new_y = self._find_valid_position(board)
            print(f"找到替代位置: ({new_x}, {new_y})")
            return new_x, new_y
            
        except Exception as e:
            print(f"Error in get_move: {str(e)}")
            print(f"错误类型: {type(e).__name__}")
            import traceback
            print(f"错误堆栈: {traceback.format_exc()}")
            # 发生错误时也使用智能寻找替代位置
            new_x, new_y = self._find_valid_position(board)
            print(f"发生错误，使用替代位置: ({new_x}, {new_y})")
            return new_x, new_y 