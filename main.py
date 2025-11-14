import pygame
import random

# --- CONFIG ---
WIDTH, HEIGHT = 800, 400
GROUND = HEIGHT - 60
POP_SIZE = 20
GENE_COUNT = 50  # number of decision points per individual
FPS = 60
BONUS = 20
JUMP_PENALTY = 10
MUTATION_PROB = 0.05  # probability to introduce a new jump near death

DESTROY_COLOR = (255,255,255)


HORIZONTAL_SPEED = 2
GRAVITY = 0.35
JUMP_VELOCITY = 10 


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()




# --- ENVIRONMENT ---


obstacles = [
    pygame.Rect(300, GROUND - 30, 50, 30),
    pygame.Rect(500, GROUND - 70, 30, 70),
    pygame.Rect(650, GROUND - 60, 20, 60),
]
goal = pygame.Rect(WIDTH - 5, GROUND - 200, 5, 200)
obstacle_thresholds = [obs.right for obs in obstacles]

# --- BOX CLASS ---
class Box:
    def __init__(self, genes=None):
        self.x = 5
        self.y = GROUND
        self.vel_y = 0
        self.on_ground = True
        self.dead = False
        self.gene_index = 0
        if genes:
            self.genes = genes
        else:
            # all "n" initially
            self.genes = sorted(
                [(int(WIDTH*(i+1)/GENE_COUNT), "n") for i in range(GENE_COUNT)],
                key=lambda g: g[0]
            )
        self.fitness = 0
        self.color = (random.randint(50,255), random.randint(50,255), random.randint(50,255))
        self.start_delay = random.randint(0, 100)
        
    def update(self):
        if self.dead:
            return
        
        if self.start_delay > 0:
            self.start_delay -= 1
            return

        self.x += HORIZONTAL_SPEED

        # check gene triggers
        while self.gene_index < len(self.genes) and self.x >= self.genes[self.gene_index][0]:
            action = self.genes[self.gene_index][1]
            if action == "j" and self.on_ground:
                self.vel_y = -JUMP_VELOCITY
                self.on_ground = False
            self.gene_index += 1

        # gravity
        self.vel_y += GRAVITY
        self.y += self.vel_y
        if self.y >= GROUND:
            self.y = GROUND
            self.vel_y = 0
            self.on_ground = True

        # collision
        box_rect = pygame.Rect(self.x, self.y-20, 20, 20)
        for obs in obstacles:
            if box_rect.colliderect(obs):
                self.dead = True
                break

        # goal reached
        if box_rect.colliderect(goal):
            self.dead = True

        self.calculate_fitness()

    def calculate_fitness(self):
        cleared = 0
        for th in obstacle_thresholds:
            if self.x > th:
                cleared += 1
        self.fitness = cleared * BONUS

        if not self.dead and cleared < len(obstacle_thresholds):
            next_obs = obstacle_thresholds[cleared]
            partial = (self.x / next_obs) * BONUS
            self.fitness += partial

        if self.x >= goal.x:
            self.fitness += BONUS

        # penalize jumps
        num_jumps = sum(1 for _, action in self.genes if action == "j")
        self.fitness -= num_jumps * JUMP_PENALTY

    def draw(self):
        # color = (0,0,200) if not self.dead else (200,200,0)
        color = self.color if not self.dead else DESTROY_COLOR
        pygame.draw.rect(screen,color,(self.x,self.y-20,20,20))
        pygame.draw.rect(screen,(0,0,0),(self.x,self.y-20,20,20),2)

# --- GENETIC ALGORITHM ---
def evolve(population):
    total_fitness = sum(b.fitness for b in population)
    if total_fitness == 0:
        total_fitness = 1

    def roulette_select():
        pick = random.uniform(0, total_fitness)
        current = 0
        for b in population:
            current += b.fitness
            if current >= pick:
                return b
        return population[-1]

    new_population = []
    for _ in range(POP_SIZE):
        p1 = roulette_select()
        p2 = roulette_select()

        # one-point crossover
        cut = random.randint(1, GENE_COUNT-1)
        child_genes = p1.genes[:cut] + p2.genes[cut:]
        child = Box(child_genes)

        # --- NEW LOGIC: introduce one jump near parent death ---
        for parent in [p1, p2]:
            if parent.dead and random.random() < MUTATION_PROB:
                death_x = parent.x
                # choose a random distance before death to add jump
                jump_x = max(0, death_x - random.randint(0,50))
                # pick closest gene to assign jump
                closest_idx = min(range(len(child.genes)), key=lambda i: abs(child.genes[i][0]-jump_x))
                child.genes[closest_idx] = (child.genes[closest_idx][0], "j")
                break  # only one jump per child

        new_population.append(child)
    return new_population

# --- MAIN LOOP ---
generation = 1
population = [Box() for _ in range(POP_SIZE)]

running = True
while running:
    clock.tick(FPS)
    screen.fill((40,40,50))

    # draw environment
    pygame.draw.rect(screen,(0,120,255),goal)
    for obs in obstacles:
        pygame.draw.rect(screen,(200,50,50),obs)
    pygame.draw.line(screen,(220,220,220),(0,GROUND+1),(WIDTH,GROUND+1),2)

    all_dead = True
    for box in population:
        box.update()
        box.draw()
        if not box.dead:
            all_dead = False

    pygame.display.flip()

    if all_dead:
        best_fit = max(b.fitness for b in population)
        print(f"--- Generation {generation} | Best fitness: {best_fit:.2f} ---")
        population = evolve(population)
        for b in population:
            b.x = 5
            b.y = GROUND
            b.vel_y = 0
            b.dead = False
            b.gene_index = 0
            b.fitness = 0
        generation += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
