import pygame
import sys
import numpy as np
import matplotlib.pyplot as plt
import io

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 初始化pygame
pygame.init()

# 扩大屏幕尺寸以提供更多空间
WIDTH, HEIGHT = 1200, 1020  # 高度增加到1020像素
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("小岛央行 - 宏观经济政策模拟游戏")

# 颜色定义
BACKGROUND = (25, 40, 65)
PANEL_BG = (40, 60, 95)
TEXT_COLOR = (220, 220, 240)
HIGHLIGHT = (70, 150, 230)
BUTTON_COLOR = (60, 100, 160)
BUTTON_HOVER = (80, 140, 220)
RED = (220, 90, 90)
GREEN = (90, 200, 140)
YELLOW = (230, 180, 70)
PURPLE = (170, 130, 220)

# 为Matplotlib定义颜色
MPL_YELLOW = (230 / 255, 180 / 255, 70 / 255)
MPL_RED = (220 / 255, 90 / 255, 90 / 255)
MPL_GREEN = (90 / 255, 200 / 255, 140 / 255)

# 字体
try:
    font_large = pygame.font.SysFont("SimHei", 36)
    font_medium = pygame.font.SysFont("SimHei", 30)
    font_small = pygame.font.SysFont("SimHei", 24)
    font_smaller = pygame.font.SysFont("SimHei", 20)
    font_tiny = pygame.font.SysFont("SimHei", 18)
except:
    font_large = pygame.font.SysFont(None, 36)
    font_medium = pygame.font.SysFont(None, 30)
    font_small = pygame.font.SysFont(None, 24)
    font_smaller = pygame.font.SysFont(None, 20)
    font_tiny = pygame.font.SysFont(None, 18)


# 经济模型
class Economy:
    def __init__(self):
        # 初始经济状态
        self.quarter = 0
        self.year = 2023
        self.inflation = 2.0  # 通货膨胀率 (%)
        self.unemployment = 5.0  # 失业率 (%)
        self.gdp_growth = 2.5  # GDP增长率 (%)
        self.interest_rate = 3.0  # 基准利率 (%)
        self.reserve_ratio = 10.0  # 存款准备金率 (%)

        # 经济历史记录
        self.history = {
            'inflation': [self.inflation],
            'unemployment': [self.unemployment],
            'gdp_growth': [self.gdp_growth],
            'interest_rate': [self.interest_rate],
            'reserve_ratio': [self.reserve_ratio]
        }

        # 目标范围
        self.target_inflation = (1.8, 2.2)
        self.target_unemployment = (4.5, 5.5)
        self.target_gdp = (2.0, 3.0)

        # 游戏状态
        self.score = 0
        self.game_over = False
        self.message = ""
        self.policy_changes = {"interest": 0, "reserve": 0}

    def apply_policy(self):
        """应用货币政策并计算下一季度经济指标"""
        if self.game_over:
            return

        # 更新政策工具
        self.interest_rate = max(0.0, min(10.0, self.interest_rate + self.policy_changes["interest"]))
        self.reserve_ratio = max(5.0, min(20.0, self.reserve_ratio + self.policy_changes["reserve"]))

        # 模拟经济变化
        inflation_change = -0.3 * self.policy_changes["interest"] + np.random.normal(0, 0.2)
        self.inflation = max(0.1, min(10.0, self.inflation + inflation_change))

        gdp_effect = 0.4 * (self.gdp_growth - 2.5)
        unemployment_change = -0.3 * gdp_effect + 0.2 * self.policy_changes["interest"] + np.random.normal(0, 0.15)
        self.unemployment = max(2.0, min(15.0, self.unemployment + unemployment_change))

        gdp_change = -0.4 * self.policy_changes["interest"] + np.random.normal(0, 0.25)
        self.gdp_growth = max(-3.0, min(8.0, self.gdp_growth + gdp_change))

        # 更新季度和时间
        self.quarter += 1
        if self.quarter == 4:
            self.quarter = 0
            self.year += 1

        # 保存历史数据
        self.history['inflation'].append(self.inflation)
        self.history['unemployment'].append(self.unemployment)
        self.history['gdp_growth'].append(self.gdp_growth)
        self.history['interest_rate'].append(self.interest_rate)
        self.history['reserve_ratio'].append(self.reserve_ratio)

        # 重置政策变化
        self.policy_changes = {"interest": 0, "reserve": 0}

        # 计算得分
        self.calculate_score()

        # 检查游戏结束条件
        if self.quarter == 0 and self.year == 2024:
            self.game_over = True
            self.message = "游戏结束！一年任期已满"
        elif self.inflation > 8 or self.unemployment > 12:
            self.game_over = True
            self.message = "游戏结束！经济陷入危机"

    def calculate_score(self):
        """根据经济指标计算得分"""
        score = 0
        # 通货膨胀得分
        if self.target_inflation[0] <= self.inflation <= self.target_inflation[1]:
            score += 10
        elif abs(self.inflation - 2.0) < 1.0:
            score += 5

        # 失业率得分
        if self.target_unemployment[0] <= self.unemployment <= self.target_unemployment[1]:
            score += 10
        elif abs(self.unemployment - 5.0) < 1.5:
            score += 5

        # GDP增长得分
        if self.target_gdp[0] <= self.gdp_growth <= self.target_gdp[1]:
            score += 10
        elif self.gdp_growth > 1.0:
            score += 5

        self.score += score

    def get_current_quarter(self):
        """获取当前季度描述"""
        quarters = ["第一季度", "第二季度", "第三季度", "第四季度"]
        return f"{self.year}年{quarters[self.quarter]}"

    def get_economy_status(self):
        """获取经济状态描述"""
        status = []
        if self.inflation < 1.0:
            status.append("通货紧缩风险")
        elif self.inflation > 3.0:
            status.append("通货膨胀压力")

        if self.unemployment < 4.0:
            status.append("劳动力短缺")
        elif self.unemployment > 6.0:
            status.append("失业问题严重")

        if self.gdp_growth < 1.0:
            status.append("经济衰退")
        elif self.gdp_growth > 4.0:
            status.append("经济过热")

        return "，".join(status) if status else "经济平稳"


# 创建经济实例
economy = Economy()


# 按钮类
class Button:
    def __init__(self, x, y, width, height, text, action=None, value=0):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.value = value
        self.hovered = False

    def draw(self, surface):
        color = BUTTON_HOVER if self.hovered else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, HIGHLIGHT, self.rect, 2, border_radius=8)

        text_surf = font_small.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.action:
                    return self.action(self.value)
        return None


# 创建按钮 - 位置下移并增大间距
buttons = [
    # 利率调整按钮
    Button(200, 870, 160, 45, "利率 +0.25%", action=lambda x: ("interest", 0.25)),
    Button(200, 940, 160, 45, "利率 -0.25%", action=lambda x: ("interest", -0.25)),

    # 存款准备金率调整按钮
    Button(450, 870, 160, 45, "准备金率 +0.5%", action=lambda x: ("reserve", 0.5)),
    Button(450, 940, 160, 45, "准备金率 -0.5%", action=lambda x: ("reserve", -0.5)),

    # 执行政策按钮
    Button(700, 905, 220, 55, "执行货币政策", action=lambda x: ("apply", 0)),
]


# 创建图表函数
def create_economy_chart(history):
    try:
        plt.close('all')

        # 创建图表
        dpi = 120
        fig = plt.figure(figsize=(10, 5), dpi=dpi, facecolor=(0.05, 0.08, 0.13))
        ax = fig.add_subplot(111)
        ax.set_facecolor((0.05, 0.08, 0.13))

        # 确保数据有效
        if not history['inflation']:
            history['inflation'] = [2.0]
        if not history['unemployment']:
            history['unemployment'] = [5.0]
        if not history['gdp_growth']:
            history['gdp_growth'] = [2.5]

        quarters = list(range(len(history['inflation'])))

        # 绘制数据线
        ax.plot(quarters, history['inflation'], 'o-', color=MPL_YELLOW,
                label='通货膨胀率 (%)', linewidth=2.5, markersize=7, markeredgewidth=1)
        ax.plot(quarters, history['unemployment'], 's-', color=MPL_RED,
                label='失业率 (%)', linewidth=2.5, markersize=7, markeredgewidth=1)
        ax.plot(quarters, history['gdp_growth'], 'D-', color=MPL_GREEN,
                label='GDP增长率 (%)', linewidth=2.5, markersize=7, markeredgewidth=1)

        # 设置样式
        ax.spines['bottom'].set_color('gray')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('gray')

        # 字体大小优化
        ax.tick_params(axis='x', colors='white', labelsize=12)
        ax.tick_params(axis='y', colors='white', labelsize=12)
        ax.set_xlabel('季度', color='white', fontsize=14)
        ax.set_ylabel('百分比 (%)', color='white', fontsize=14)
        ax.set_title('经济指标变化趋势', color='white', fontsize=14)

        # 设置图例
        legend = ax.legend(loc='upper right', facecolor=(0.1, 0.15, 0.25),
                           labelcolor='white', fontsize=12, framealpha=0.9)

        # 网格线优化
        ax.grid(True, color='gray', linestyle='-', alpha=0.15)

        plt.tight_layout(pad=3.0)

        # 渲染为图像缓冲区
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=dpi, bbox_inches='tight')
        plt.close(fig)

        # 从内存加载图像
        buf.seek(0)
        chart_image = pygame.image.load(buf)
        buf.close()

        return chart_image
    except Exception as e:
        print(f"图表生成错误: {str(e)}")
        return None


# 主游戏循环
clock = pygame.time.Clock()

while True:
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        for button in buttons:
            result = button.handle_event(event)
            if result:
                action, value = result
                if action == "apply":
                    economy.apply_policy()
                else:
                    economy.policy_changes[action] += value

    for button in buttons:
        button.check_hover(mouse_pos)

    # 绘制界面
    screen.fill(BACKGROUND)

    # 标题区域
    pygame.draw.rect(screen, (35, 55, 90), (0, 0, WIDTH, 100))
    title = font_large.render("小岛央行 - 宏观经济政策模拟游戏", True, TEXT_COLOR)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 30))

    # 当前季度和得分
    quarter_text = font_medium.render(f"当前: {economy.get_current_quarter()}", True, TEXT_COLOR)
    screen.blit(quarter_text, (50, 110))
    score_text = font_medium.render(f"得分: {economy.score}", True, YELLOW)
    screen.blit(score_text, (WIDTH - score_text.get_width() - 50, 110))

    # ================== 经济指标面板 ==================
    econ_panel = pygame.Rect(50, 150, WIDTH - 100, 180)
    pygame.draw.rect(screen, PANEL_BG, econ_panel, border_radius=12)
    pygame.draw.rect(screen, HIGHLIGHT, econ_panel, 2, border_radius=12)

    # 面板标题
    indicators_title = font_medium.render("经济指标", True, HIGHLIGHT)
    screen.blit(indicators_title, (70, 160))

    # 指标位置计算
    start_y = 200
    col_width = (WIDTH - 100) // 3

    # 通货膨胀指标
    inflation_text = font_small.render(f"通货膨胀率: {economy.inflation:.2f}%", True, YELLOW)
    screen.blit(inflation_text, (70, start_y))

    # 失业率指标
    unemployment_text = font_small.render(f"失业率: {economy.unemployment:.2f}%", True, RED)
    screen.blit(unemployment_text, (70 + col_width, start_y))

    # GDP增长率指标
    gdp_text = font_small.render(f"GDP增长率: {economy.gdp_growth:.2f}%", True, GREEN)
    screen.blit(gdp_text, (70 + col_width * 2, start_y))

    # 经济状态
    status = economy.get_economy_status()
    status_text = font_small.render(f"经济状态: {status}", True, TEXT_COLOR)
    screen.blit(status_text, (70, start_y + 40))

    # 目标范围
    target_y = start_y + 90
    target_text = font_smaller.render(
        f"通胀目标: {economy.target_inflation[0]}%-{economy.target_inflation[1]}% | "
        f"失业目标: {economy.target_unemployment[0]}%-{economy.target_unemployment[1]}% | "
        f"GDP增长目标: {economy.target_gdp[0]}%-{economy.target_gdp[1]}%",
        True, (180, 200, 230)
    )
    screen.blit(target_text, (WIDTH // 2 - target_text.get_width() // 2, target_y))

    # ================== 政策工具面板 ==================
    policy_panel = pygame.Rect(50, 350, WIDTH - 100, 180)
    pygame.draw.rect(screen, PANEL_BG, policy_panel, border_radius=12)
    pygame.draw.rect(screen, HIGHLIGHT, policy_panel, 2, border_radius=12)

    # 面板标题
    policy_title = font_medium.render("货币政策工具", True, HIGHLIGHT)
    screen.blit(policy_title, (70, 360))

    # 政策工具
    tool_y = 410
    # 利率
    interest_text = font_small.render(f"基准利率: {economy.interest_rate:.2f}%", True, TEXT_COLOR)
    screen.blit(interest_text, (70, tool_y))
    interest_change = font_small.render(f"调整: {economy.policy_changes['interest']:+.2f}%",
                                        True, GREEN if economy.policy_changes['interest'] >= 0 else RED)
    screen.blit(interest_change, (70, tool_y + 35))

    # 准备金率
    reserve_text = font_small.render(f"存款准备金率: {economy.reserve_ratio:.2f}%", True, TEXT_COLOR)
    screen.blit(reserve_text, (70 + col_width * 1.7, tool_y))
    reserve_change = font_small.render(f"调整: {economy.policy_changes['reserve']:+.2f}%",
                                       True, GREEN if economy.policy_changes['reserve'] >= 0 else RED)
    screen.blit(reserve_change, (70 + col_width * 1.7, tool_y + 35))

    # 政策说明
    policy_desc = font_smaller.render("↑ 利率: 抑制通胀但可能增加失业 | ↓ 准备金率: 增加银行放贷刺激经济", True,
                                      (180, 200, 230))
    screen.blit(policy_desc, (WIDTH // 2 - policy_desc.get_width() // 2, tool_y + 85))

    # ================== 图表区域 ==================
    chart_panel = pygame.Rect(50, 550, WIDTH - 100, 250)  # 大幅增加的图表区域高度
    pygame.draw.rect(screen, PANEL_BG, chart_panel, border_radius=12)
    pygame.draw.rect(screen, HIGHLIGHT, chart_panel, 2, border_radius=12)

    # 绘制图表
    if len(economy.history['inflation']) > 0:
        chart_img = create_economy_chart(economy.history)
        if chart_img:
            chart_width = min(WIDTH - 120, 1000)
            chart_height = min(220, 1000)
            chart_img = pygame.transform.scale(chart_img, (chart_width, chart_height))
            screen.blit(chart_img, (WIDTH // 2 - chart_width // 2, 565))

    # ================== 控制区域 ==================
    # 操作标题（下移到830像素）
    control_title = font_medium.render("货币政策调整", True, HIGHLIGHT)
    screen.blit(control_title, (WIDTH // 2 - control_title.get_width() // 2, 830))

    # 水平分隔线（下移到825像素）
    pygame.draw.line(screen, HIGHLIGHT, (100, 825), (WIDTH - 100, 825), 2)

    # 绘制按钮（整体下移100像素）
    for button in buttons:
        button.draw(screen)

    # ================== 游戏结束处理 ==================
    if economy.game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        end_text = font_large.render(economy.message, True, YELLOW)
        screen.blit(end_text, (WIDTH // 2 - end_text.get_width() // 2, HEIGHT // 2 - 50))

        score_text = font_medium.render(f"最终得分: {economy.score}", True, TEXT_COLOR)
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 + 20))

        restart_text = font_small.render("按R键重新开始游戏", True, GREEN)
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 80))

        if pygame.key.get_pressed()[pygame.K_r]:
            economy = Economy()

    pygame.display.flip()
    clock.tick(60)