import pygame
import random

# --- CONFIG ---
WIDTH, HEIGHT = 800, 400
GROUND = HEIGHT - 60
POP_SIZE = 50
GENE_LENGTH = 120   # decision steps (jump/no-op)x
MUTATION_RATE = 0.05
FPS = 60
HORIZONTAL_SPEED = 3  # constant forward speed

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# --- ENVIRONMENT ---
obstacles = [
    pygame.Rect(300, GROUND - 40, 40, 40),
    pygame.Rect(500, GROUND - 60, 40, 60),
    pygame.Rect(650, GROUND - 50, 40, 50),
]

goal = pygame.Rect(WIDTH - 50, GROUND - 50, 40, 50)

obstacle_thresholds = [obs.right for obs in obstacles]  # [340, 540, 690] for your current setup
BONUS = 300


# --- BOX CLASS ---
class Box:
    def __init__(self, genes=None):
        self.x = 5
        self.y = GROUND
        self.vel_y = 0
        self.on_ground = True
        self.dead = False
        self.gene_index = 0
        # genes: "j" = jump, "n" = no-op
        self.genes = genes or [random.choice(["j", "n"]) for _ in range(GENE_LENGTH)]
        self.fitness = 0

    def clone(self):
        return Box(self.genes.copy())

    def mutate(self):
        for i in range(len(self.genes)):
            # more mutation chance for early genes
            rate = MUTATION_RATE * (1.5 if i < GENE_LENGTH // 2 else 0.5)
            if random.random() < rate:
                self.genes[i] = random.choice(["j", "n"])

    def update(self):
        # If the box dies, give bonus for obstacles passed
        if self.dead:
            cleared_count = 0
            for th in obstacle_thresholds:
                if self.x > th:
                    cleared_count += 1
            self.fitness += cleared_count * BONUS
            return 


        # Constant forward movement
        self.x += HORIZONTAL_SPEED

        # Jump decision
        if self.gene_index < len(self.genes):
            action = self.genes[self.gene_index]
            self.gene_index += 1
        else:
            action = "n"

        if action == "j" and self.on_ground:
            self.vel_y = -10
            self.on_ground = False

        # Gravity
        self.vel_y += 0.5
        self.y += self.vel_y
        if self.y >= GROUND:
            self.y = GROUND
            self.vel_y = 0
            self.on_ground = True

        # Collision
        box_rect = pygame.Rect(self.x, self.y - 20, 20, 20)
        for obs in obstacles:
            if box_rect.colliderect(obs):
                self.dead = True
                break

        # Goal reached
        if box_rect.colliderect(goal):
            self.dead = True
            self.fitness += 10000

        # Fitness = distance traveled
        self.fitness = max(self.fitness, self.x)

    def draw(self):
        # custom colors: body + border
        color = (0,0,200) if not self.dead else (200, 200, 0)
        border = (0, 0, 0)
        pygame.draw.rect(screen, color, (self.x, self.y - 20, 20, 20))
        pygame.draw.rect(screen, border, (self.x, self.y - 20, 20, 20), 2)

# --- GENETIC ALGORITHM ---
def evolve(population):
    # Sort by fitness
    population.sort(key=lambda b: b.fitness, reverse=True)
    top_half = population[: len(population) // 2]

    # No elitism, pure GA
    next_gen = []

    # Fitness info
    all_time_best = max(population, key=lambda b: b.fitness)
    print(f"Current best: {population[0].fitness:.2f}, All-time best: {all_time_best.fitness:.2f}")

    # Roulette-wheel selection
    total_fit = sum(b.fitness for b in top_half)
    if total_fit == 0:
        probs = [1 / len(top_half)] * len(top_half)
    else:
        probs = [b.fitness / total_fit for b in top_half]

    while len(next_gen) < POP_SIZE:
        p1 = random.choices(top_half, weights=probs, k=1)[0]
        p2 = random.choices(top_half, weights=probs, k=1)[0]

        # Biased crossover: early genes more likely to mix
        cut = int(random.betavariate(2, 5) * GENE_LENGTH)
        child_genes = p1.genes[:cut] + p2.genes[cut:]
        child = Box(child_genes)
        child.mutate()
        next_gen.append(child)

    return next_gen

# --- MAIN LOOP ---
generation = 1
population = [Box() for _ in range(POP_SIZE)]

running = True
while running:
    clock.tick(FPS)
    screen.fill((40, 40, 50))  # background color

    # Draw environment
    pygame.draw.rect(screen, (0, 120, 255), goal)  # goal color
    for obs in obstacles:
        pygame.draw.rect(screen, (200, 50, 50), obs)  # obstacle color
    pygame.draw.line(screen, (220, 220, 220), (0, GROUND + 1), (WIDTH, GROUND + 1), 2)

    # Update and draw boxes
    for box in population:
        box.update()
        box.draw()

    pygame.display.flip()

    # Advance generation only when all boxes are dead
    if all(b.dead for b in population):
        generation += 1
        print(f"\n--- Generation {generation} ---")
        population = evolve(population)
        for b in population:
            b.x = 50
            b.y = GROUND
            b.vel_y = 0
            b.dead = False
            b.gene_index = 0
            b.fitness = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
