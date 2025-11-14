
# Box Evolution Simulation

A Pygame-based simulation where boxes evolve using a genetic algorithm to navigate obstacles and reach a goal.

## Description

- Each box has a set of "genes" representing decision points (jump or no action) at specific horizontal positions.
- Boxes move automatically from left to right, jumping when instructed by their genes.
- The goal is to reach the end while avoiding obstacles.
- Fitness is calculated based on obstacles cleared, reaching the goal, and penalizing unnecessary jumps.
- A genetic algorithm evolves the population over generations, using crossover and mutation to improve performance.

## Features

- Real-time simulation using Pygame.
- Genetic algorithm with:
  - Roulette wheel selection
  - One-point crossover
  - Mutation introducing jumps near parent death
- Visual representation of boxes, obstacles, and goal.
- Console output showing the best fitness per generation.

## Configuration

- `WIDTH`, `HEIGHT`      : Window dimensions (default 800x400)  
- `GROUND`               : Ground level  
- `POP_SIZE`             : Number of boxes per generation  
- `GENE_COUNT`           : Number of decision points per box  
- `FPS`                  : Frames per second  
- `BONUS`                : Fitness bonus per cleared obstacle  
- `JUMP_PENALTY`         : Fitness penalty per jump  
- `MUTATION_PROB`        : Probability to introduce new jump near parent death  
- `HORIZONTAL_SPEED`     : Box horizontal movement speed  
- `GRAVITY`              : Vertical acceleration due to gravity  
- `JUMP_VELOCITY`        : Initial vertical velocity for jumps  

## Requirements

- Python 3.x  
- Pygame (`pip install pygame`)

## Running the Simulation

1. Install dependencies:

```bash
pip install pygame
````

2. Run the script:

```bash
python your_script_name.py
```

3. Watch boxes attempt to navigate obstacles in real-time.
   Console output shows the best fitness per generation.

## Controls

* Close the window to stop the simulation.

## Notes

* Boxes start with random gene sequences.
* Over generations, the population adapts to clear obstacles more effectively.
* Mutation occasionally introduces jumps near the position where parent boxes died, helping the evolution process.


