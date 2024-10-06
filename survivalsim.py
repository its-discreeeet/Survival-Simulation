import random
import pygame
import math


pygame.init()

WIDTH, HEIGHT = 800, 600
NUM_BOTS = 20
INITIAL_ENERGY = 50
FOOD_RADIUS = 5 
BOT_RADIUS = 5
REPRODUCTION_THRESHOLD = 100
MOVEMENT_COST = 0.01
FOOD_SPAWN_RATE = 0.1


WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)

class Bot:
    def __init__(self, x, y, food_specialization):
        self.x = x
        self.y = y
        self.food_specialization = food_specialization  # 0: herbivore, 1: carnivore, 0.5: omnivore
        self.energy = INITIAL_ENERGY
        self.alive = True
        self.direction = random.uniform(0, 2 * math.pi)
        self.speed = random.uniform(1, 3)
        
    def move(self):
        if self.alive:
            # Random direction changes
            self.direction += random.uniform(-0.5, 0.5)
            
            # Move in current direction
            self.x += math.cos(self.direction) * self.speed
            self.y += math.sin(self.direction) * self.speed
            
            # Wrap around screen edges
            self.x = self.x % WIDTH
            self.y = self.y % HEIGHT
            
            # Energy cost based on speed
            self.energy -= MOVEMENT_COST * self.speed
            
            if self.energy <= 0:
                self.die()

    def eat(self, food_amount, food_type):
        if not self.alive:
            return False
            
        # Dietary preferences affect energy gained
        efficiency = 1.0
        if self.food_specialization == 0:  # Herbivore
            efficiency = 1.0 if food_type == "plant" else 0.2
        elif self.food_specialization == 1:  # Carnivore
            efficiency = 1.0 if food_type == "meat" else 0.2
        else:  # Omnivore
            efficiency = 0.7  # Balanced diet
            
        self.energy += food_amount * efficiency
        return True

    def reproduce(self):
        if self.energy > REPRODUCTION_THRESHOLD:
            # Create offspring with possible mutations
            child = Bot(self.x, self.y, self.food_specialization)
            
            # Mutations
            if random.random() < 0.1:  # 10% mutation chance
                child.food_specialization = random.choice([0, 0.5, 1])
            if random.random() < 0.1:
                child.speed = max(0.5, min(5, self.speed + random.uniform(-0.5, 0.5)))
                
            self.energy /= 2  # Parent loses half energy
            child.energy = self.energy  # Child gets half energy
            
            return child
        return None

    def die(self):
        self.alive = False

class Food:
    def __init__(self, x, y, food_type="plant"):
        self.x = x
        self.y = y
        self.food_type = food_type
        self.amount = random.randint(10, 20)
        self.color = GREEN if food_type == "plant" else RED

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Evolution Simulation")
    clock = pygame.time.Clock()
    
    # Initialize populations
    bots = [Bot(random.randint(0, WIDTH), random.randint(0, HEIGHT), 
                random.choice([0, 0.5, 1])) for _ in range(NUM_BOTS)]
    foods = [Food(random.randint(0, WIDTH), random.randint(0, HEIGHT)) 
             for _ in range(NUM_BOTS * 2)]
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(WHITE)
        
        # Spawn new food
        if random.random() < FOOD_SPAWN_RATE:
            foods.append(Food(random.randint(0, WIDTH), random.randint(0, HEIGHT)))
        
        # Update and draw food
        for food in foods[:]:
            pygame.draw.circle(screen, food.color, (int(food.x), int(food.y)), FOOD_RADIUS)

        # Update and draw bots
        new_bots = []
        for bot in bots[:]:
            if bot.alive:
                # Movement
                bot.move()
                
                # Feeding
                for food in foods[:]:
                    distance = math.hypot(bot.x - food.x, bot.y - food.y)
                    if distance < BOT_RADIUS + FOOD_RADIUS:
                        if bot.eat(food.amount, food.food_type):
                            foods.remove(food)
                            break
                
                # Reproduction
                child = bot.reproduce()
                if child:
                    new_bots.append(child)
                
                # Draw bot
                color = RED if bot.food_specialization == 1 else (
                    BLUE if bot.food_specialization == 0 else PURPLE)
                pygame.draw.circle(screen, color, (int(bot.x), int(bot.y)), BOT_RADIUS)
        
        # Add new bots and remove dead ones
        bots.extend(new_bots)
        bots = [bot for bot in bots if bot.alive and bot.energy > 0]
        
        # Display stats
        font = pygame.font.Font(None, 36)
        stats = f"Bots: {len(bots)} Food: {len(foods)}"
        text = font.render(stats, True, (0, 0, 0))
        screen.blit(text, (10, 10))
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()