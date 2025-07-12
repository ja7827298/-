import pygame
import sys
import random
import math

pygame.init()
pygame.font.init()

# 屏幕设置
screen_width, screen_height = 1440, 720
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("数字方块合成游戏")

# 字体设置
font = pygame.font.SysFont('Arial', 24)
title_font = pygame.font.SysFont('Arial', 36)

# 网格设置
grid_size = 64  # 网格大小
grid_width = screen_width // grid_size
grid_height = screen_height // grid_size

# 方块设置
block_size = grid_size - 4  # 方块边长，留出间隙
colors = {
    2: (238, 228, 218),
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46)
}

# 创建数字方块表面
def create_block_surface(number):
    color = colors.get(number, (60, 58, 50))
    surface = pygame.Surface((block_size, block_size))
    surface.fill(color)
    
    # 调整字体大小以适应大数字
    font_size = 24
    if number >= 100:
        font_size = 18
    text_font = pygame.font.SysFont('Arial', font_size)
    
    # 绘制数字
    text = text_font.render(str(number), True, (119, 110, 101) if number <= 4 else (249, 246, 242))
    text_rect = text.get_rect(center=(block_size//2, block_size//2))
    surface.blit(text, text_rect)
    
    return surface

# 存储所有方块的列表
blocks = []
# 合并动画列表
merge_animations = []
# 分数
score = 0

# 物理参数
GRAVITY = 0.5
FRICTION = 0.98
ELASTICITY = 0.7

class MergeAnimation:
    def __init__(self, block1, block2, new_number):
        self.block1 = block1
        self.block2 = block2
        self.new_number = new_number
        self.progress = 0  # 0-1表示动画进度
        self.duration = 0.3  # 动画持续时间(秒)
        self.speed = 1.0 / self.duration
        self.active = True
        
        # 计算新方块的位置(取两个方块的中心)
        x1, y1 = block1['rect'].center
        x2, y2 = block2['rect'].center
        self.target_pos = ((x1 + x2) // 2, (y1 + y2) // 2)
        
        # 创建新方块表面
        self.new_surface = create_block_surface(new_number)
    
    def update(self, dt):
        self.progress += self.speed * dt
        if self.progress >= 1:
            self.progress = 1
            self.active = False
        return self.active
    
    def draw(self, screen):
        # 计算当前缩放比例
        scale = 1.0 + 0.2 * math.sin(self.progress * math.pi)  # 脉冲效果
        
        # 绘制第一个方块
        if self.progress < 0.5:
            pos = (
                self.block1['rect'].x + (self.target_pos[0] - self.block1['rect'].centerx) * self.progress * 2,
                self.block1['rect'].y + (self.target_pos[1] - self.block1['rect'].centery) * self.progress * 2
            )
            scaled_surface = pygame.transform.scale(
                self.block1['surface'],
                (int(block_size * scale), int(block_size * scale))
            )
            screen.blit(scaled_surface, pos)
        
        # 绘制第二个方块
        if self.progress < 0.5:
            pos = (
                self.block2['rect'].x + (self.target_pos[0] - self.block2['rect'].centerx) * self.progress * 2,
                self.block2['rect'].y + (self.target_pos[1] - self.block2['rect'].centery) * self.progress * 2
            )
            scaled_surface = pygame.transform.scale(
                self.block2['surface'],
                (int(block_size * scale), int(block_size * scale))
            )
            screen.blit(scaled_surface, pos)
        
        # 绘制合并后的新方块
        if self.progress >= 0.5:
            alpha = int(255 * (self.progress - 0.5) * 2)
            self.new_surface.set_alpha(alpha)
            scaled_surface = pygame.transform.scale(
                self.new_surface,
                (int(block_size * scale), int(block_size * scale))
            )
            screen.blit(scaled_surface, (
                self.target_pos[0] - scaled_surface.get_width() // 2,
                self.target_pos[1] - scaled_surface.get_height() // 2
            ))

def check_collisions():
    """检查所有方块的碰撞并处理合并"""
    global score
    # 创建方块的副本以便安全遍历
    blocks_copy = blocks.copy()
    
    for i, block in enumerate(blocks_copy):
        if block not in blocks:  # 如果方块已被移除则跳过
            continue
            
        # 检查与其他方块的碰撞
        for other_block in blocks_copy[i+1:]:
            if other_block not in blocks:  # 如果方块已被移除则跳过
                continue
                
            if block['rect'].colliderect(other_block['rect']) and block['number'] == other_block['number']:
                # 计算合并后的数字
                new_number = block['number'] * 2
                
                # 创建合并动画
                merge_animations.append(MergeAnimation(block, other_block, new_number))
                
                # 更新被合并的方块
                other_block['number'] = new_number
                other_block['surface'] = create_block_surface(new_number)
                
                # 增加分数
                score += new_number
                
                # 移除当前方块
                blocks.remove(block)
                break  # 跳出内层循环

def spawn_block():
    """从左下角生成一个新方块"""
    # 从左下角飞出
    x = random.randint(0, screen_width - block_size)
    y = screen_height
    
    # 随机速度
    velocity_x = random.uniform(-2, 2)
    velocity_y = random.uniform(-10, -5)
    
    # 随机数字 (80%概率是2，20%概率是4)
    number = random.choice([2, 2, 2, 2, 4])
    
    new_block = {
        'rect': pygame.Rect(x, y, block_size, block_size),
        'velocity': [velocity_x, velocity_y],
        'number': number,
        'surface': create_block_surface(number),
        'falling': True
    }
    blocks.append(new_block)

def snap_to_grid(rect):
    """将方块对齐到网格"""
    grid_x = round(rect.x / grid_size)
    grid_y = round(rect.y / grid_size)
    
    # 确保在网格范围内
    grid_x = max(0, min(grid_x, grid_width - 1))
    grid_y = max(0, min(grid_y, grid_height - 1))
    
    return pygame.Rect(grid_x * grid_size + 2, grid_y * grid_size + 2, block_size, block_size)

def draw_header():
    """绘制顶部标题和分数"""
    # 绘制标题背景
    pygame.draw.rect(screen, (187, 173, 160), (0, 0, screen_width, 50))
    
    # 绘制标题
    title_text = title_font.render("合成游戏", True, (119, 110, 101))
    screen.blit(title_text, (20, 10))
    
    # 绘制分数
    score_text = font.render(f"分数: {score}", True, (119, 110, 101))
    screen.blit(score_text, (screen_width - 150, 15))

# 游戏主循环
clock = pygame.time.Clock()
running = True
while running:
    dt = clock.tick(60) / 1000.0  # 获取帧间隔时间(秒)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键点击
                # 点击鼠标时生成10个方块
                for _ in range(10):
                    spawn_block()
    
    # 清屏
    screen.fill((187, 173, 160))  # 背景色
    
    # 绘制网格线
    for x in range(0, screen_width, grid_size):
        pygame.draw.line(screen, (205, 193, 180), (x, 50), (x, screen_height))
    for y in range(50, screen_height, grid_size):
        pygame.draw.line(screen, (205, 193, 180), (0, y), (screen_width, y))
    
    # 检查碰撞
    check_collisions()
    
    # 更新合并动画
    for animation in merge_animations[:]:
        if not animation.update(dt):
            merge_animations.remove(animation)
    
    # 更新和绘制所有方块
    for block in blocks[:]:  # 使用副本遍历以便安全删除
        if block.get('falling', False):
            # 应用重力
            block['velocity'][1] += GRAVITY
            
            # 应用摩擦力
            block['velocity'][0] *= FRICTION
            block['velocity'][1] *= FRICTION
            
            # 临时保存旧位置用于碰撞检测
            old_x, old_y = block['rect'].x, block['rect'].y
            
            # 更新位置
            block['rect'].x += block['velocity'][0]
            block['rect'].y += block['velocity'][1]
            
            # 检测是否到达底部
            if block['rect'].y >= screen_height - block_size - 2:
                block['rect'].y = screen_height - block_size - 2
                block['velocity'][1] = 0
                block['falling'] = False
            
            # 对齐到网格
            if abs(block['velocity'][0]) < 0.5 and abs(block['velocity'][1]) < 0.5:
                snapped_rect = snap_to_grid(block['rect'])
                if snapped_rect != block['rect']:
                    block['rect'] = snapped_rect
                    block['velocity'] = [0, 0]
                    block['falling'] = False
        
        # 检查是否超出屏幕
        if block['rect'].y < -block_size or block['rect'].x < -block_size or block['rect'].x > screen_width:
            blocks.remove(block)
            continue
        
        # 绘制方块
        screen.blit(block['surface'], block['rect'])
    
    # 绘制合并动画
    for animation in merge_animations:
        animation.draw(screen)
    
    # 绘制顶部标题和分数
    draw_header()
    
    # 更新显示
    pygame.display.flip()

pygame.quit()
sys.exit()