import requests
import json
import re
import random

class Llama3AI:
    def __init__(self):
        self.api_url = "http://100.96.21.95:11435/api/generate"
        self.model = "llama3"
        self.headers = {
            "Content-Type": "application/json"
        }

    def _validate_move(self, board, x, y):
        """验证移动是否有效"""
        print(f"验证坐标 ({x}, {y})...")
        
        # 检查坐标范围
        if not (0 <= x <= 14 and 0 <= y <= 14):
            print(f"❌ 坐标超出范围：x={x}, y={y}，有效范围是0-14")
            return False
        
        # 检查位置是否为空
        current_cell = board[x][y]
        if current_cell != '':
            print(f"❌ 位置已被占用：board[{x}][{y}]='{current_cell}'")
            print(f"当前棋盘第{x}行: {[board[x][j] if board[x][j] != '' else '.' for j in range(15)]}")
            
            # 显示可用的空位
            empty_positions = [(i, j) for i in range(15) for j in range(15) if board[i][j] == '']
            print(f"可用空位数量: {len(empty_positions)}")
            if len(empty_positions) > 0:
                print(f"前5个可用空位: {empty_positions[:5]}")
            return False
        
        print(f"✅ 坐标验证通过: ({x}, {y})")
        return True

    def _analyze_threats(self, board, player_color):
        """分析威胁和机会"""
        threats = []
        opportunities = []
        
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]  # 水平、垂直、两个对角线
        opponent_color = 'white' if player_color == 'black' else 'black'
        
        # 检查每个空位
        for i in range(15):
            for j in range(15):
                if board[i][j] == '':  # 只检查空位
                    # 检查在这个位置下棋后能形成的连子数
                    for dx, dy in directions:
                        # 检查我方机会
                        my_count = self._count_line(board, i, j, dx, dy, player_color)
                        if my_count >= 2:  # 降低阈值，检测更多机会
                            # 检查是否为活连（两端都没有被堵）
                            is_alive = self._is_alive_line(board, i, j, dx, dy, player_color)
                            line_type = "活" if is_alive else "死"
                            opportunities.append((i, j, my_count, f"我方{line_type}{my_count}连", is_alive))
                        
                        # 检查对手威胁
                        opponent_count = self._count_line(board, i, j, dx, dy, opponent_color)
                        if opponent_count >= 2:  # 降低阈值，检测更多威胁
                            # 检查是否为活连
                            is_alive = self._is_alive_line(board, i, j, dx, dy, opponent_color)
                            line_type = "活" if is_alive else "死"
                            threats.append((i, j, opponent_count, f"对手{line_type}{opponent_count}连", is_alive))
        
        # 按威胁程度排序（连子数越多越危险，活连优先于死连）
        threats.sort(key=lambda x: (x[2], x[4]), reverse=True)
        opportunities.sort(key=lambda x: (x[2], x[4]), reverse=True)
        
        return threats, opportunities
    
    def _count_line(self, board, x, y, dx, dy, color):
        """计算在(x,y)位置下棋后，沿(dx,dy)方向能形成的连子数"""
        count = 1  # 包括当前位置
        
        # 向正方向计数
        nx, ny = x + dx, y + dy
        while 0 <= nx < 15 and 0 <= ny < 15 and board[nx][ny] == color:
            count += 1
            nx += dx
            ny += dy
        
        # 向负方向计数
        nx, ny = x - dx, y - dy
        while 0 <= nx < 15 and 0 <= ny < 15 and board[nx][ny] == color:
            count += 1
            nx -= dx
            ny -= dy
        
        return count

    def _is_alive_line(self, board, x, y, dx, dy, color):
        """检查连线是否为活连（两端都没有被对手棋子堵住）"""
        # 向正方向找到连线的末端
        end_x, end_y = x, y
        while 0 <= end_x + dx < 15 and 0 <= end_y + dy < 15 and board[end_x + dx][end_y + dy] == color:
            end_x += dx
            end_y += dy
        
        # 向负方向找到连线的起始端
        start_x, start_y = x, y
        while 0 <= start_x - dx < 15 and 0 <= start_y - dy < 15 and board[start_x - dx][start_y - dy] == color:
            start_x -= dx
            start_y -= dy
        
        # 检查两端是否都是空位或边界
        opponent_color = 'white' if color == 'black' else 'black'
        
        # 检查正方向端点
        pos_end_x, pos_end_y = end_x + dx, end_y + dy
        pos_blocked = (0 <= pos_end_x < 15 and 0 <= pos_end_y < 15 and 
                      board[pos_end_x][pos_end_y] == opponent_color)
        
        # 检查负方向端点
        neg_end_x, neg_end_y = start_x - dx, start_y - dy
        neg_blocked = (0 <= neg_end_x < 15 and 0 <= neg_end_y < 15 and 
                      board[neg_end_x][neg_end_y] == opponent_color)
        
        # 如果两端都没有被对手堵住，则为活连
        return not (pos_blocked and neg_blocked)

    def _create_prompt(self, board, current_player):
        """创建发送给 Llama3 的提示"""
        # 生成二维数组
        arr = [[0 if cell == '' else 1 if cell == 'black' else 2 for cell in row] for row in board]
        
        # 生成空位坐标列表
        empty = [(i, j) for i in range(15) for j in range(15) if board[i][j] == '']
        
        # 分析当前局势
        my_color = 1 if current_player == 'black' else 2
        opponent_color = 2 if current_player == 'black' else 1
        
        # 分析威胁和机会
        threats, opportunities = self._analyze_threats(board, current_player)
        
        # 构建局势分析
        situation_analysis = ""
        if threats:
            situation_analysis += f"⚠️ 紧急威胁：{threats[:3]}\n"
        if opportunities:
            situation_analysis += f"🎯 进攻机会：{opportunities[:3]}\n"
        if not threats and not opportunities:
            situation_analysis = "📊 局势平稳，寻找最佳发展位置\n"
        
        # 构建优先级指导
        priority_guide = ""
        if threats:
            top_threat = threats[0]
            priority_guide += f"🚨 最高优先级：封堵对手威胁 ({top_threat[0]},{top_threat[1]}) - {top_threat[3]}\n"
        if opportunities:
            top_opportunity = opportunities[0]
            priority_guide += f"⚡ 进攻优先级：利用机会 ({top_opportunity[0]},{top_opportunity[1]}) - {top_opportunity[3]}\n"
        
        prompt = f"""Gomoku AI Move Selection

Your color: {current_player} ({my_color})
Opponent: {'white' if current_player == 'black' else 'black'} ({opponent_color})

Board (0=empty, 1=black, 2=white):
{chr(10).join([f"{i:2d}: {arr[i]}" for i in range(15)])}

Available: {empty[:20]}{'...' if len(empty) > 20 else ''}

{situation_analysis.strip()}
{priority_guide.strip()}

CRITICAL: If there are threats, you MUST block them immediately!

Choose best move. Return JSON only:
{{"x": row, "y": col, "analysis": "reason"}}

Response:"""
        
        return prompt

    def _board_to_string(self, board):
        """将棋盘转换为字符串表示"""
        board_str = "   " + " ".join([f"{i:2d}" for i in range(15)]) + "\n"
        for i, row in enumerate(board):
            row_str = f"{i:2d} "
            for j, cell in enumerate(row):
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
        # 首先寻找能形成连子的位置
        for i in range(15):
            for j in range(15):
                if board[i][j] == '':
                    # 检查周围是否有棋子
                    has_neighbor = False
                    for di in [-1, 0, 1]:
                        for dj in [-1, 0, 1]:
                            if di == 0 and dj == 0:
                                continue
                            ni, nj = i + di, j + dj
                            if 0 <= ni < 15 and 0 <= nj < 15 and board[ni][nj] != '':
                                has_neighbor = True
                                break
                        if has_neighbor:
                            break
                    
                    if has_neighbor:
                        return i, j
        
        # 如果没有相邻的位置，选择优先级区域
        priority_areas = [
            (7, 7),  # 天元
            (3, 3), (3, 7), (3, 11),  # 星位
            (7, 3), (7, 11),
            (11, 3), (11, 7), (11, 11),
            (6, 6), (6, 7), (6, 8),  # 中心区域
            (7, 6), (7, 8),
            (8, 6), (8, 7), (8, 8)
        ]
        
        for x, y in priority_areas:
            if board[x][y] == '':
                return x, y
        
        # 最后从中心向外寻找空位
        center = 7
        for distance in range(8):
            for i in range(max(0, center - distance), min(15, center + distance + 1)):
                for j in range(max(0, center - distance), min(15, center + distance + 1)):
                    if board[i][j] == '':
                        return i, j
        
        return 7, 7  # 默认返回中心位置

    def _get_best_move_by_strategy(self, board, current_player):
        """基于策略获取最佳移动"""
        threats, opportunities = self._analyze_threats(board, current_player)
        opponent_color = 'white' if current_player == 'black' else 'black'
        
        print(f"=== 策略分析 ===")
        print(f"发现威胁: {len(threats)} 个")
        for i, (x, y, count, desc, is_alive) in enumerate(threats[:5]):
            alive_str = "活" if is_alive else "死"
            print(f"  威胁{i+1}: ({x},{y}) - {desc} ({alive_str})")
        
        print(f"发现机会: {len(opportunities)} 个")
        for i, (x, y, count, desc, is_alive) in enumerate(opportunities[:5]):
            alive_str = "活" if is_alive else "死"
            print(f"  机会{i+1}: ({x},{y}) - {desc} ({alive_str})")
        
        # 寻找叉攻机会
        fork_opportunities = self._find_fork_opportunities(board, current_player)
        if fork_opportunities:
            print(f"发现叉攻机会: {len(fork_opportunities)} 个")
            for i, (x, y, count, desc) in enumerate(fork_opportunities[:3]):
                print(f"  叉攻{i+1}: ({x},{y}) - {desc}")
        
        # 寻找封堵位置
        blocking_positions = self._find_blocking_positions(board, opponent_color)
        if blocking_positions:
            print(f"需要封堵: {len(blocking_positions)} 个位置")
            for i, (x, y, count, desc) in enumerate(blocking_positions[:3]):
                print(f"  封堵{i+1}: ({x},{y}) - {desc}")

        # 计算当前局面的空位数量，用于判断游戏阶段
        empty_count = sum(1 for i in range(15) for j in range(15) if board[i][j] == '')
        is_early_game = empty_count > 180  # 开局阶段
        is_mid_game = 100 < empty_count <= 180  # 中局阶段
        is_late_game = empty_count <= 100  # 残局阶段
        
        # 策略优先级
        # 1. 如果我方能立即获胜（5连），立即下
        winning_moves = [(x, y) for x, y, count, desc, is_alive in opportunities if count >= 5]
        if winning_moves:
            x, y = random.choice(winning_moves)  # 如果有多个制胜点，随机选择
            print(f"🎉 立即获胜: ({x},{y})")
            return x, y
        
        # 2. 如果对手能立即获胜（5连），必须封堵
        critical_threats = [(x, y) for x, y, count, desc, is_alive in threats if count >= 5]
        if critical_threats:
            x, y = random.choice(critical_threats)  # 如果有多个威胁点，随机选择
            print(f"🚨 紧急封堵: ({x},{y})")
            return x, y
        
        # 3. 如果我方能形成活四，优先考虑
        alive_four_moves = [(x, y) for x, y, count, desc, is_alive in opportunities if count == 4 and is_alive]
        if alive_four_moves:
            x, y = random.choice(alive_four_moves)
            print(f"⚡ 活四必胜: ({x},{y})")
            return x, y
        
        # 4. 如果对手能形成活四，必须封堵
        alive_four_threats = [(x, y) for x, y, count, desc, is_alive in threats if count == 4 and is_alive]
        if alive_four_threats:
            x, y = random.choice(alive_four_threats)
            print(f"🛡️ 封堵活四: ({x},{y})")
            return x, y
        
        # 5. 双活三叉攻（非常强的进攻手段）
        if fork_opportunities:
            # 在开局和中局更倾向于选择叉攻
            if is_early_game or is_mid_game:
                x, y = random.choice(fork_opportunities[:3])[:2]  # 从前三个叉攻中随机选择
                print(f"🗡️ 双活三叉攻: ({x},{y})")
                return x, y
        
        # 6. 如果对手有活三，必须封堵
        alive_three_threats = [(x, y) for x, y, count, desc, is_alive in threats if count == 3 and is_alive]
        if alive_three_threats:
            # 如果有多个活三威胁，优先选择能同时防守和进攻的点
            best_blocking_moves = []
            for bx, by in alive_three_threats:
                # 评估这个防守点的进攻价值
                attack_value = self._evaluate_attack_value(board, bx, by, current_player)
                best_blocking_moves.append((bx, by, attack_value))
            
            if best_blocking_moves:
                # 按进攻价值排序，从最高的开始选择
                best_blocking_moves.sort(key=lambda x: x[2], reverse=True)
                top_moves = [move for move in best_blocking_moves if move[2] >= best_blocking_moves[0][2] * 0.8]
                x, y, _ = random.choice(top_moves)  # 从最好的几个中随机选择
                print(f"🛡️ 封堵活三: ({x},{y})")
                return x, y
        
        # 7. 我方活三进攻
        alive_three_moves = [(x, y) for x, y, count, desc, is_alive in opportunities if count == 3 and is_alive]
        if alive_three_moves and (is_early_game or is_mid_game):
            # 评估每个活三的进攻价值
            attack_moves = []
            for ax, ay in alive_three_moves:
                attack_value = self._evaluate_attack_value(board, ax, ay, current_player)
                attack_moves.append((ax, ay, attack_value))
            
            if attack_moves:
                # 按进攻价值排序，选择最好的几个
                attack_moves.sort(key=lambda x: x[2], reverse=True)
                top_moves = [move for move in attack_moves if move[2] >= attack_moves[0][2] * 0.8]
                x, y, _ = random.choice(top_moves)
                print(f"⚔️ 活三进攻: ({x},{y})")
                return x, y
        
        # 8. 在没有明显战术机会时，进行位置评估
        if is_early_game:
            # 开局更注重布局和控制中心
            center_moves = self._get_center_control_moves(board)
            if center_moves:
                x, y = random.choice(center_moves[:3])  # 从最好的三个位置中随机选择
                print(f"🎯 布局控制中心: ({x},{y})")
                return x, y
        elif is_mid_game:
            # 中局注重发展和防守平衡
            balanced_moves = self._get_balanced_moves(board, current_player)
            if balanced_moves:
                x, y = random.choice(balanced_moves[:3])
                print(f"⚖️ 均衡发展: ({x},{y})")
                return x, y
        else:
            # 残局更注重具体战术
            tactical_moves = self._get_tactical_moves(board, current_player)
            if tactical_moves:
                x, y = random.choice(tactical_moves[:3])
                print(f"📊 战术选择: ({x},{y})")
                return x, y
        
        # 如果上述策略都没有找到合适的位置，使用综合评估
        best_positions = []
        for i in range(15):
            for j in range(15):
                if board[i][j] == '':
                    value = self._evaluate_position_value(board, i, j)
                    # 添加随机扰动
                    value += random.uniform(-5, 5)
                    best_positions.append((i, j, value))
        
        if best_positions:
            best_positions.sort(key=lambda x: x[2], reverse=True)
            # 从最高分值的前几个位置中随机选择
            top_positions = [pos for pos in best_positions if pos[2] >= best_positions[0][2] * 0.9]
            x, y, value = random.choice(top_positions[:5])  # 从前5个最佳位置中随机选择
            print(f"🎯 综合评估位置: ({x},{y}) - 价值{value:.2f}")
            return x, y
        
        print("📊 无明显策略，使用AI分析")
        return None  # 没有明显策略，让AI自己分析

    def _evaluate_attack_value(self, board, x, y, player_color):
        """评估某个位置的进攻价值"""
        value = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        # 模拟在此位置下棋
        board_copy = [row[:] for row in board]
        board_copy[x][y] = player_color
        
        # 计算在各个方向上的发展潜力
        for dx, dy in directions:
            # 检查连子数量
            count = self._count_line(board_copy, x, y, dx, dy, player_color)
            # 检查是否为活子
            is_alive = self._is_alive_line(board_copy, x, y, dx, dy, player_color)
            
            # 根据连子数量和活度给分
            if is_alive:
                value += count * 10  # 活子价值更高
            else:
                value += count * 5   # 死子也有一定价值
            
            # 检查周围是否有己方棋子（有助于形成更复杂的局面）
            for d in range(-2, 3):
                nx, ny = x + dx * d, y + dy * d
                if 0 <= nx < 15 and 0 <= ny < 15 and board[nx][ny] == player_color:
                    value += 2
        
        return value

    def _get_center_control_moves(self, board):
        """获取控制中心的最佳位置"""
        moves = []
        center_positions = [
            (7, 7),  # 天元
            (6, 6), (6, 7), (6, 8),  # 中心区域
            (7, 6), (7, 8),
            (8, 6), (8, 7), (8, 8),
            (5, 5), (5, 7), (5, 9),  # 次中心区域
            (7, 5), (7, 9),
            (9, 5), (9, 7), (9, 9)
        ]
        
        for x, y in center_positions:
            if board[x][y] == '':
                value = 20 - (abs(x - 7) + abs(y - 7))  # 离中心越近价值越高
                moves.append((x, y, value))
        
        moves.sort(key=lambda x: x[2], reverse=True)
        return [(x, y) for x, y, _ in moves]

    def _get_balanced_moves(self, board, player_color):
        """获取平衡发展的位置"""
        moves = []
        for i in range(15):
            for j in range(15):
                if board[i][j] == '':
                    attack_value = self._evaluate_attack_value(board, i, j, player_color)
                    defense_value = self._evaluate_defense_value(board, i, j, player_color)
                    # 在中局，我们希望找到攻防都不错的位置
                    balance_value = min(attack_value, defense_value) * 2 + max(attack_value, defense_value)
                    moves.append((i, j, balance_value))
        
        moves.sort(key=lambda x: x[2], reverse=True)
        return [(x, y) for x, y, _ in moves]

    def _get_tactical_moves(self, board, player_color):
        """获取战术位置（主要用于残局）"""
        moves = []
        for i in range(15):
            for j in range(15):
                if board[i][j] == '':
                    # 在残局，我们更关注直接的战术价值
                    tactical_value = self._evaluate_tactical_value(board, i, j, player_color)
                    moves.append((i, j, tactical_value))
        
        moves.sort(key=lambda x: x[2], reverse=True)
        return [(x, y) for x, y, _ in moves]

    def _evaluate_defense_value(self, board, x, y, player_color):
        """评估某个位置的防守价值"""
        value = 0
        opponent_color = 'white' if player_color == 'black' else 'black'
        
        # 模拟在此位置下棋
        board_copy = [row[:] for row in board]
        board_copy[x][y] = player_color
        
        # 检查是否能阻止对手的连线
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dx, dy in directions:
            # 检查对手在这个位置的潜在威胁
            opponent_count = self._count_line(board, x, y, dx, dy, opponent_color)
            is_alive = self._is_alive_line(board, x, y, dx, dy, opponent_color)
            
            # 根据威胁程度给分
            if is_alive:
                value += opponent_count * 15  # 阻止活子威胁
            else:
                value += opponent_count * 8   # 阻止死子威胁
        
        return value

    def _evaluate_tactical_value(self, board, x, y, player_color):
        """评估某个位置的战术价值（主要用于残局）"""
        value = 0
        opponent_color = 'white' if player_color == 'black' else 'black'
        
        # 攻击价值
        attack_value = self._evaluate_attack_value(board, x, y, player_color)
        # 防守价值
        defense_value = self._evaluate_defense_value(board, x, y, player_color)
        
        # 在残局，我们更重视能形成直接威胁的位置
        value = max(attack_value, defense_value) * 1.5
        
        # 检查是否能形成多重威胁
        board_copy = [row[:] for row in board]
        board_copy[x][y] = player_color
        
        # 计算此位置能形成的威胁数量
        threats_count = 0
        for dx, dy in [(0, 1), (1, 0), (1, 1), (1, -1)]:
            count = self._count_line(board_copy, x, y, dx, dy, player_color)
            is_alive = self._is_alive_line(board_copy, x, y, dx, dy, player_color)
            if count >= 3 and is_alive:
                threats_count += 1
        
        # 多重威胁的价值很高
        value += threats_count * 20
        
        return value

    def get_move(self, board, current_player):
        """获取 Llama3 AI 的下一步移动"""
        try:
            print(f"\n当前棋盘状态：\n{self._board_to_string(board)}")
            print(f"当前玩家：{current_player}")
            
            # 首先进行策略分析，处理紧急情况
            strategic_move = self._get_best_move_by_strategy(board, current_player)
            if strategic_move:
                x, y = strategic_move
                if self._validate_move(board, x, y):
                    print(f"✅ 使用策略决策: ({x}, {y})")
                    return x, y
                else:
                    print(f"❌ 策略决策位置无效: ({x}, {y})，继续AI分析")
            
            # 如果没有紧急情况，使用AI分析
            prompt = self._create_prompt(board, current_player)
            
            data = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,  # 稍微提高一点创造性
                    "top_p": 0.9,        # 增加候选词范围
                    "top_k": 20,         # 增加候选词数量
                    "num_predict": 8192,  # 设置最大生成token数为8192
                    "repeat_penalty": 1.2,  # 增加重复惩罚
                    "stop": ["\n\n\n"]  # 简化停止词，只在多个换行时停止
                }
            }

            print(f"发送请求到 Llama3...")
            print(f"请求参数: {json.dumps(data['options'], indent=2, ensure_ascii=False)}")
            
            response = requests.post(
                self.api_url, 
                headers=self.headers, 
                json=data, 
                timeout=60
            )
            response.raise_for_status()
            
            # 解析响应
            result = response.json()
            response_text = result.get('response', '').strip()
            
            # 打印详细的响应信息
            print(f"=== Llama3 响应详情 ===")
            print(f"原始响应长度: {len(response_text)} 字符")
            print(f"原始响应: {response_text}")
            
            # 检查是否有其他响应字段
            if 'done' in result:
                print(f"生成完成状态: {result['done']}")
            if 'total_duration' in result:
                print(f"总耗时: {result['total_duration']} 纳秒")
            if 'load_duration' in result:
                print(f"加载耗时: {result['load_duration']} 纳秒")
            if 'prompt_eval_count' in result:
                print(f"输入 token 数: {result['prompt_eval_count']}")
            if 'prompt_eval_duration' in result:
                print(f"输入处理耗时: {result['prompt_eval_duration']} 纳秒")
            if 'eval_count' in result:
                print(f"生成 token 数: {result['eval_count']}")
            if 'eval_duration' in result:
                print(f"生成耗时: {result['eval_duration']} 纳秒")
            
            # 计算速度
            if 'eval_count' in result and 'eval_duration' in result and result['eval_duration'] > 0:
                tokens_per_second = result['eval_count'] / (result['eval_duration'] / 1e9)
                print(f"生成速度: {tokens_per_second:.2f} tokens/秒")
            
            print(f"========================")
            
            # 如果响应太短或不包含数字，直接使用备用策略
            if len(response_text.strip()) < 10 or not re.search(r'\d', response_text):
                print("=== 响应过短分析 ===")
                print(f"响应长度: {len(response_text.strip())} 字符 (阈值: 10)")
                print(f"响应内容: '{response_text}'")
                
                # 检查是否因为停止词而提前结束
                if 'eval_count' in result:
                    print(f"实际生成了 {result['eval_count']} 个 token")
                    if result['eval_count'] < 50:
                        print("⚠️ 生成的 token 数量很少，可能是停止词过早触发")
                    elif result['eval_count'] >= 8000:
                        print("⚠️ 生成的 token 数量接近上限，可能被截断")
                
                print("使用智能备用策略")
                print("===================")
                new_x, new_y = self._find_valid_position(board)
                print(f"找到替代位置: ({new_x}, {new_y})")
                return new_x, new_y
            
            # 尝试从响应中提取JSON或坐标
            json_patterns = [
                r'\{\s*"x"\s*:\s*\d+\s*,\s*"y"\s*:\s*\d+[^}]*\}',  # 完整JSON
                r'"x"\s*:\s*(\d+)[^}]*"y"\s*:\s*(\d+)',  # 提取坐标对
                r'(\d+)\s*,\s*(\d+)',  # 简单的数字对
                r'x[:\s]*(\d+)[^0-9]*y[:\s]*(\d+)',  # x: 数字 y: 数字格式
            ]
            
            json_str = None
            extracted_coords = None
            
            for i, pattern in enumerate(json_patterns):
                if i == 0:  # 完整JSON模式
                    json_match = re.search(pattern, response_text)
                    if json_match:
                        json_str = json_match.group()
                        print(f"提取的JSON: {json_str}")
                        break
                else:  # 坐标提取模式
                    coords = re.findall(pattern, response_text)
                    if coords:
                        try:
                            if len(coords[0]) == 2:  # 确保有两个数字
                                x, y = int(coords[0][0]), int(coords[0][1])
                                extracted_coords = (x, y)
                                print(f"提取坐标 (模式{i+1}): ({x}, {y})")
                                break
                        except (ValueError, IndexError):
                            continue
            
            # 处理提取到的JSON或坐标
            if json_str:
                try:
                    move_data = json.loads(json_str)
                    if 'x' in move_data and 'y' in move_data:
                        x, y = int(move_data['x']), int(move_data['y'])
                        analysis = move_data.get('analysis', '无分析')
                        
                        print(f"解析出的坐标: ({x}, {y})")
                        print(f"AI 分析: {analysis}")
                        
                        # 详细验证坐标
                        if self._validate_move(board, x, y):
                            return x, y
                    else:
                        print("JSON中缺少必要的x和y字段")
                except json.JSONDecodeError as e:
                    print(f"JSON解析失败: {e}")
            elif extracted_coords:
                x, y = extracted_coords
                print(f"使用直接提取的坐标: ({x}, {y})")
                if self._validate_move(board, x, y):
                    return x, y
            
            # 如果没有找到有效坐标，使用智能寻找替代位置
            print("未找到有效坐标，使用智能寻找替代位置...")
            new_x, new_y = self._find_valid_position(board)
            print(f"找到替代位置: ({new_x}, {new_y})")
            return new_x, new_y
            
        except requests.exceptions.RequestException as e:
            print(f"网络请求错误: {str(e)}")
            print("使用智能寻找替代位置...")
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

    def _evaluate_position_value(self, board, x, y):
        """评估位置价值"""
        value = 0
        
        # 中心控制价值（越靠近中心价值越高）
        center_distance = abs(x - 7) + abs(y - 7)
        center_value = max(0, 14 - center_distance)
        value += center_value * 2
        
        # 星位价值（传统的重要位置）
        star_positions = [(3, 3), (3, 7), (3, 11), (7, 3), (7, 7), (7, 11), (11, 3), (11, 7), (11, 11)]
        if (x, y) in star_positions:
            value += 15
        
        # 邻近棋子价值（有利于形成连子）
        neighbor_count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < 15 and 0 <= ny < 15 and board[nx][ny] != '':
                    neighbor_count += 1
        value += neighbor_count * 5
        
        return value
    
    def _find_fork_opportunities(self, board, player_color):
        """寻找双活三（叉攻）机会"""
        fork_opportunities = []
        
        for i in range(15):
            for j in range(15):
                if board[i][j] == '':
                    # 检查在这个位置下棋后能形成多少个活三
                    alive_threes = 0
                    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
                    
                    for dx, dy in directions:
                        count = self._count_line(board, i, j, dx, dy, player_color)
                        if count == 3 and self._is_alive_line(board, i, j, dx, dy, player_color):
                            alive_threes += 1
                    
                    if alive_threes >= 2:  # 双活三或更多
                        fork_opportunities.append((i, j, alive_threes, f"双活三叉攻"))
        
        return fork_opportunities
    
    def _find_blocking_positions(self, board, opponent_color):
        """寻找需要封堵的关键位置"""
        blocking_positions = []
        
        # 寻找对手的活三
        for i in range(15):
            for j in range(15):
                if board[i][j] == '':
                    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
                    for dx, dy in directions:
                        count = self._count_line(board, i, j, dx, dy, opponent_color)
                        if count == 3 and self._is_alive_line(board, i, j, dx, dy, opponent_color):
                            blocking_positions.append((i, j, count, f"封堵对手活三"))
        
        return blocking_positions 