import pygame

from settings import FPS, SCREEN_HEIGHT, SCREEN_WIDTH, TITLE
from src.core.event_bus import EventBus
from src.core.game_state import GameState
from src.resources.resource_manager import ResourceManager
from src.scenes.intro_scene import IntroScene
from src.scenes.menu_scene import MenuScene
from src.scenes.playing_scene import PlayingScene
from src.scenes.scene_manager import SceneManager
from src.ui.scene_transition import SceneTransitionManager


class Game:
    """游戏主类，负责窗口、状态、主循环和顶层场景切换。"""

    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = GameState.MENU
        self.resources = ResourceManager()
        self.events = EventBus()
        self.scene_manager = SceneManager()
        self.scene_transition = SceneTransitionManager()

        self.title_font = self.resources.load_font(48)
        self.menu_font = self.resources.load_font(28)
        self.small_font = self.resources.load_font(24)
        self._show_menu()

    def run(self) -> None:
        """主循环入口。"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()

        pygame.quit()

    def handle_events(self) -> None:
        """处理全局输入，再把场景内输入交给当前场景。"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
                continue

            if event.type == pygame.KEYDOWN:
                key_name = pygame.key.name(event.key)
                if event.key == pygame.K_e:
                    print("[EVENT] E keydown received")
                print(f"[STATE] current_state = {self.state.value}, key = {key_name}")

            if self.scene_transition.is_blocking_input():
                continue

            if self.scene_manager.handle_event(event):
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.quit()
                elif self.state == GameState.MENU and event.key == pygame.K_RETURN:
                    self.start_game()

    def update(self) -> None:
        """更新当前场景。"""
        dt = self.clock.tick(FPS) / 1000
        self.scene_manager.update(dt)
        self.scene_transition.update(dt)

    def draw(self) -> None:
        """绘制当前场景。"""
        self.scene_manager.draw(self.screen)
        self.scene_transition.draw(self.screen)
        pygame.display.flip()

    def start_game(self) -> None:
        """从菜单进入主游戏场景。"""
        if self.scene_transition.is_active():
            return
        self.scene_transition.start(self._start_intro_scene, target_scene="intro")

    def _start_intro_scene(self) -> None:
        video_path = IntroScene.VIDEO_PATH
        video_found = video_path.exists()
        print(f"[INTRO] video path={video_path.as_posix()}")
        print(f"[INTRO] video found={video_found}")
        if video_found:
            print("[INTRO][WARN] video playback unsupported, skip intro")
        print("[INTRO] skip -> village_hub")
        self._start_game_now()

    def _start_game_now(self) -> None:
        self.state = GameState.PLAYING
        self.scene_manager.set_scene("playing", PlayingScene(self.small_font))

    def quit(self) -> None:
        """标记退出，交由主循环统一关闭 pygame。"""
        self.running = False

    def _show_menu(self) -> None:
        self.state = GameState.MENU
        self.scene_manager.set_scene(
            "menu",
            MenuScene(
                self.title_font,
                self.menu_font,
                self.small_font,
                start_callback=self.start_game,
                quit_callback=self.quit,
            ),
        )
