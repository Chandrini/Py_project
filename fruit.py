
import pygame
import random
import sys
import os

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCALE_FACTOR = 0.3
GAME_TIME = 60  # seconds

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Fruit Catcher - Fixed Version")
        self.clock = pygame.time.Clock()

        # Game states
        self.state = "MENU"  # MENU, PLAYING, PAUSED, GAME_OVER

        # Load fonts
        self.font_title = pygame.font.Font(None, 74)
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)

        # Load images with fallback
        self.load_images()
        self.load_sounds()

        # Game variables
        self.reset_game()

    def load_images(self):
        """Load images with fallback to colored shapes"""
        self.fruit_images = []
        self.bomb_image = None
        self.basket_image = None

        # Try to load fruit images, fallback to colored circles
        fruit_files = ["strawberry.png", "kiwi.png", "banana.png", "orange.png"]
        fruit_colors = [RED, GREEN, YELLOW, ORANGE]

        for i, (filename, color) in enumerate(zip(fruit_files, fruit_colors)):
            try:
                if os.path.exists(filename):
                    img = pygame.image.load(filename)
                    img = pygame.transform.scale(img, (int(50 * SCALE_FACTOR * 3), int(50 * SCALE_FACTOR * 3)))
                    self.fruit_images.append(img)
                else:
                    raise FileNotFoundError
            except (pygame.error, FileNotFoundError):
                # Create fallback fruit shape
                surface = pygame.Surface((45, 45), pygame.SRCALPHA)
                pygame.draw.circle(surface, color, (22, 22), 20)
                pygame.draw.circle(surface, BLACK, (22, 22), 20, 2)
                self.fruit_images.append(surface)

        # Try to load bomb image, fallback to black circle with X
        try:
            if os.path.exists("bomb.png"):
                self.bomb_image = pygame.image.load("bomb.png")
                self.bomb_image = pygame.transform.scale(self.bomb_image, (int(50 * SCALE_FACTOR * 3), int(50 * SCALE_FACTOR * 3)))
            else:
                raise FileNotFoundError
        except (pygame.error, FileNotFoundError):
            surface = pygame.Surface((45, 45), pygame.SRCALPHA)
            pygame.draw.circle(surface, BLACK, (22, 22), 20)
            pygame.draw.line(surface, RED, (10, 10), (34, 34), 3)
            pygame.draw.line(surface, RED, (34, 10), (10, 34), 3)
            self.bomb_image = surface

        # Try to load basket image, fallback to brown rectangle
        try:
            if os.path.exists("basket.png"):
                self.basket_image = pygame.image.load("basket.png")
                self.basket_image = pygame.transform.scale(self.basket_image, (int(80 * SCALE_FACTOR * 3), int(60 * SCALE_FACTOR * 3)))
            else:
                raise FileNotFoundError
        except (pygame.error, FileNotFoundError):
            surface = pygame.Surface((72, 54), pygame.SRCALPHA)
            pygame.draw.rect(surface, (139, 69, 19), (0, 10, 72, 44))
            pygame.draw.rect(surface, BLACK, (0, 10, 72, 44), 2)
            # Add handle
            pygame.draw.arc(surface, BLACK, (20, 0, 32, 20), 0, 3.14, 3)
            self.basket_image = surface

    def load_sounds(self):
        """Load sound effects with error handling"""
        try:
            if os.path.exists("catch.wav"):
                self.catch_sound = pygame.mixer.Sound("catch.wav")
            else:
                self.catch_sound = None
        except pygame.error:
            self.catch_sound = None

        try:
            if os.path.exists("explosion.wav"):
                self.explosion_sound = pygame.mixer.Sound("explosion.wav")
            else:
                self.explosion_sound = None
        except pygame.error:
            self.explosion_sound = None

    def reset_game(self):
        """Reset game variables for new game"""
        self.player = Player(self.basket_image)
        self.falling_objects = []
        self.score = 0
        self.start_ticks = pygame.time.get_ticks()
        self.base_fall_speed = 3

    def get_remaining_time(self):
        """Get remaining game time"""
        elapsed = (pygame.time.get_ticks() - self.start_ticks) // 1000
        return max(0, GAME_TIME - elapsed)

    def get_current_speed(self):
        """Get current falling speed (increases over time)"""
        elapsed = (pygame.time.get_ticks() - self.start_ticks) // 1000
        return self.base_fall_speed + (elapsed // 10)

    def spawn_object(self):
        """Spawn new falling object"""
        if random.random() < 0.02:  # 2% chance per frame
            x_pos = random.randint(0, SCREEN_WIDTH - 50)
            obj_type = 'fruit' if random.random() < 0.8 else 'bomb'

            if obj_type == 'fruit':
                image = random.choice(self.fruit_images)
            else:
                image = self.bomb_image

            speed = self.get_current_speed()
            self.falling_objects.append(FallingObject(x_pos, 0, obj_type, image, speed))

    def update_game(self):
        """Update game logic"""
        if self.get_remaining_time() <= 0:
            self.state = "GAME_OVER"
            return

        # Update player
        self.player.update()

        # Update falling objects
        for obj in self.falling_objects[:]:
            obj.update()

            # Remove off-screen objects
            if obj.off_screen():
                self.falling_objects.remove(obj)
                continue

            # Check collision with player
            if obj.check_collision(self.player):
                if obj.type == 'fruit':
                    self.score += 10
                    if self.catch_sound:
                        self.catch_sound.play()
                else:  # bomb
                    self.score = max(0, self.score - 5)  # Prevent negative score
                    if self.explosion_sound:
                        self.explosion_sound.play()

                self.falling_objects.remove(obj)

        # Spawn new objects
        self.spawn_object()

    def draw_menu(self):
        """Draw main menu"""
        self.screen.fill(WHITE)

        title_text = self.font_title.render("Fruit Catcher", True, BLACK)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//4))
        self.screen.blit(title_text, title_rect)

        instructions = [
            "Catch fruits (+10 points)",
            "Avoid bombs (-5 points)",
            "Use LEFT/RIGHT arrow keys to move",
            "Press ESC to pause during game",
            "",
            "Press ENTER to start",
            "Press Q to quit"
        ]

        for i, instruction in enumerate(instructions):
            text = self.font_medium.render(instruction, True, BLACK)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + i*30))
            self.screen.blit(text, text_rect)

    def draw_game(self):
        """Draw main game"""
        self.screen.fill(WHITE)

        # Draw falling objects
        for obj in self.falling_objects:
            obj.draw(self.screen)

        # Draw player
        self.player.draw(self.screen)

        # Draw UI
        score_text = self.font_large.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_text, (10, 10))

        time_text = self.font_large.render(f"Time: {self.get_remaining_time()}", True, BLACK)
        time_rect = time_text.get_rect(topright=(SCREEN_WIDTH-10, 10))
        self.screen.blit(time_text, time_rect)

        speed_text = self.font_small.render(f"Speed: {self.get_current_speed()}", True, BLACK)
        self.screen.blit(speed_text, (10, 60))

        # Draw pause instruction
        pause_text = self.font_small.render("Press ESC to pause", True, BLACK)
        pause_rect = pause_text.get_rect(topright=(SCREEN_WIDTH-10, 60))
        self.screen.blit(pause_text, pause_rect)

    def draw_pause(self):
        """Draw pause menu"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        pause_text = self.font_title.render("PAUSED", True, WHITE)
        pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.screen.blit(pause_text, pause_rect)

        instruction_text = self.font_medium.render("Press ESC to resume", True, WHITE)
        instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60))
        self.screen.blit(instruction_text, instruction_rect)

    def draw_game_over(self):
        """Draw game over screen"""
        self.screen.fill(WHITE)

        game_over_text = self.font_title.render("GAME OVER", True, BLACK)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3))
        self.screen.blit(game_over_text, game_over_rect)

        final_score_text = self.font_large.render(f"Final Score: {self.score}", True, BLACK)
        score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.screen.blit(final_score_text, score_rect)

        instructions = [
            "Press ENTER to play again",
            "Press Q to quit"
        ]

        for i, instruction in enumerate(instructions):
            text = self.font_medium.render(instruction, True, BLACK)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 80 + i*40))
            self.screen.blit(text, text_rect)

    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return False

                if self.state == "MENU":
                    if event.key == pygame.K_RETURN:
                        self.state = "PLAYING"
                        self.reset_game()

                elif self.state == "PLAYING":
                    if event.key == pygame.K_ESCAPE:
                        self.state = "PAUSED"

                elif self.state == "PAUSED":
                    if event.key == pygame.K_ESCAPE:
                        self.state = "PLAYING"

                elif self.state == "GAME_OVER":
                    if event.key == pygame.K_RETURN:
                        self.state = "MENU"

        return True

    def run(self):
        """Main game loop"""
        running = True

        while running:
            running = self.handle_events()

            if self.state == "PLAYING":
                self.update_game()
                self.draw_game()
            elif self.state == "MENU":
                self.draw_menu()
            elif self.state == "PAUSED":
                self.draw_game()  # Draw game in background
                self.draw_pause()  # Draw pause overlay
            elif self.state == "GAME_OVER":
                self.draw_game_over()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

class Player:
    def __init__(self, image):
        self.image = image
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - self.height - 10
        self.speed = 7

    def update(self):
        """Update player position based on input"""
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed

    def draw(self, screen):
        """Draw player on screen"""
        screen.blit(self.image, (self.x, self.y))

    def get_rect(self):
        """Get player rectangle for collision detection"""
        return pygame.Rect(self.x, self.y, self.width, self.height)

class FallingObject:
    def __init__(self, x, y, obj_type, image, speed):
        self.x = x
        self.y = y
        self.type = obj_type
        self.image = image
        self.speed = speed
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def update(self):
        """Update object position"""
        self.y += self.speed
        self.rect.y = self.y

    def draw(self, screen):
        """Draw object on screen"""
        screen.blit(self.image, self.rect)

    def off_screen(self):
        """Check if object is off screen"""
        return self.y > SCREEN_HEIGHT

    def check_collision(self, player):
        """Check collision with player"""
        return self.rect.colliderect(player.get_rect())

# Run the game
if __name__ == "__main__":
    game = Game()
    game.run()
