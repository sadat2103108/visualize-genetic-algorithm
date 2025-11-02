import pygame
import random

# --- CONFIG ---
WIDTH, HEIGHT = 800, 400
GROUND = HEIGHT - 60
POP_SIZE = 100
GENE_LENGTH = 120   # decision steps (jump/no-op)
MUTATION_PROB = 0.1
FPS = 60
HORIZONTAL_SPEED = 3 # constant forward speed
JUMP = 10
MUTATION_WINDOW = 100  # mutation window around death
RESET_UPTO = 30
MUTATION_WINDOW_PROB = 0  # 60% chance to do focused mutation




pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# --- ENVIRONMENT ---
obstacles = [
    pygame.Rect(250, GROUND - 40, 40, 40),
    pygame.Rect(600, GROUND - 60, 40, 60),
    # pygame.Rect(600, GROUND - 50, 40, 50),
]
goal = pygame.Rect(WIDTH - 50, GROUND - 50, 40, 50)
obstacle_thresholds = [obs.right for obs in obstacles]
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
        self.genes = genes or ['n' for _ in range(GENE_LENGTH)]
        self.fitness = 0

    def update(self):
        if self.dead:
            # Give bonus for obstacles cleared
            cleared_count = sum(1 for th in obstacle_thresholds if self.x > th)
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
            self.vel_y = - JUMP
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
        color = (0, 150, 200) if not self.dead else (200, 200, 0)
        border = (0, 0, 0)
        pygame.draw.rect(screen, color, (self.x, self.y - 20, 20, 20))
        pygame.draw.rect(screen, border, (self.x, self.y - 20, 20, 20), 2)

# --- GENETIC ALGORITHM ---
def evolve(population):
    # Sort by fitness
    population.sort(key=lambda b: b.fitness, reverse=True)
    top_half = population[: len(population) // 2]

    next_gen = []

    all_time_best = max(population, key=lambda b: b.fitness)
    print(f"Current best: {population[0].fitness:.2f}, All-time best: {all_time_best.fitness:.2f}")

    # Roulette-wheel selection
    total_fit = sum(b.fitness for b in top_half)
    probs = [b.fitness / total_fit if total_fit > 0 else 1/len(top_half) for b in top_half]

    while len(next_gen) < POP_SIZE:
        p1 = random.choices(top_half, weights=probs, k=1)[0]
        p2 = random.choices(top_half, weights=probs, k=1)[0]

        # Biased crossover
        cut = int(random.betavariate(2,5) * GENE_LENGTH)
        child_genes = p1.genes[:cut] + p2.genes[cut:]
        child = Box(child_genes)
        # cut = random.randint(0, GENE_LENGTH)
        # child_genes = p1.genes[:cut] + p2.genes[cut:]
        # child = Box(child_genes)

        
        maxfitness = min(max(p1.fitness, p2.fitness)+100, GENE_LENGTH-1)
        
        if random.random() < MUTATION_WINDOW_PROB:
            center_gene = int(min(maxfitness , GENE_LENGTH - 1))
            
            
            start_gene = max(0, center_gene - MUTATION_WINDOW)
            
            # end_gene = min(GENE_LENGTH, center_gene + MUTATION_WINDOW)
            # mid_gene = max(0, center_gene - MUTATION_WINDOW)
            end_gene = min(GENE_LENGTH, center_gene + 0)
            for i in range(start_gene, end_gene):
                # child.genes[i] = 'n'
                if  random.random() < MUTATION_PROB:
                    child.genes[i] = 'j' if child.genes[i] == 'n' else 'n'
        else:
            # global mutation anywhere
            for i in range(GENE_LENGTH):
                # child.genes[i] = 'n'
                if random.random() < MUTATION_PROB:
                    child.genes[i] = 'j' if child.genes[i] == 'n' else 'n'

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
    pygame.draw.rect(screen, (0, 120, 255), goal)
    for obs in obstacles:
        pygame.draw.rect(screen, (200, 50, 50), obs)
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
            b.x = 5
            b.y = GROUND
            b.vel_y = 0
            b.dead = False
            b.gene_index = 0
            b.fitness = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
