
        maxfitness = max(p1.fitness, p2.fitness) 
        if random.random() < MUTATION_WINDOW_PROB:
            center_gene = int(min(maxfitness