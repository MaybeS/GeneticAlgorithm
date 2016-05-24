"""
@Time 2016-05-16 -- 22
@Author MaybeS
@lang Python
"""

from functools import reduce
from random import randrange, uniform
from matplotlib.pyplot import plot, show, xlim, ylim, xlabel, ylabel, figure, axes
from matplotlib.animation import FuncAnimation
from collections import deque
from numpy import mean

CHILD_CNT = 64

DNA_SIZE = 16;
DNA_FINAL = [x for x in range(DNA_SIZE)]

SELECT_BEST_RATE = 0.5
MUTATION_RATE = 0.6
CROSS_RATE = 0.3

MAX_FITNESS = 1

MAX_X = 100
MAX_Y = 1.1

def rand(x, y):
	return randrange(x, y)

def event(rate):
	return True if uniform(0.0, 1.0) < rate else False

def sufflize(func = lambda x : rand(0, DNA_SIZE)):
	ret = [-1] * (DNA_SIZE)
	for i in range(DNA_SIZE):
		p = func(i)
		while ret[p] != -1:
			p = func(i)
		ret[p] = i
	return ret

def wheel_choice(items, func = lambda x : x.fitness):
	p = uniform(0.0, sum([func(x) for x in items]))
	c = 0
	for i in items:
		c += func(i)
		if c>p:
			return i

class Generation:
    cnt = 0
    def __init__(self, dna_list):
        Generation.cnt += 1
        self.level = Generation.cnt
        self.DNA_list = dna_list

    def __repr__(self):
        return "<Gen %d>" % self.level

    def next_child(self):
    	return DNA(wheel_choice(self.DNA_list).child(wheel_choice(self.DNA_list)))

    def evolution(self):
        childs = [self.best if event(SELECT_BEST_RATE) else self.next_child() for _ in range(CHILD_CNT)]
        return Generation(childs)

    def fitness(self):
    	return mean([dna.fitness for dna in self.DNA_list])

    @property
    def best(self):
        return sorted(self.DNA_list, key=lambda x: x.fitness)[-1]

class DNA:
    def __init__(self, gene = sufflize()):
        self.gene = gene

    def __repr__(self):
        return "[DNA %s |FIT %.2f]\n" % (", ".join(str(x) for x in self.gene), self.fitness)

    def __str__(self):
    	return "[ %s ]" % ", ".join(str(x) for x in self.gene)

    def child(self, mother):
    	sperm = self.gene
    	# CROSSOVER
    	while True:
	        sp = rand(0, DNA_SIZE-1)
	        ep = rand(sp+1, DNA_SIZE)

	        sperm = sperm[sp:ep]
	        fetus = [x for x in mother.gene if x not in sperm]

	        offspring = fetus[:sp-1] + sperm + fetus[sp-1:len(fetus)]

	        # MUTATION
	        while event(MUTATION_RATE):
	        	mp = rand(0, DNA_SIZE)
	        	np = rand(0, DNA_SIZE)

	        	offspring[mp], offspring[np] = offspring[np], offspring[mp]

	        if(not event(CROSS_RATE)):
	        	return offspring

    @property
    def fitness(self) -> int:
    	cnt = 0
    	for tar, obj in zip(DNA_FINAL, self.gene):
    		cnt += DNA_SIZE - abs(tar - obj)
    	#cnt = reduce(lambda x, y: x + y, list(map(lambda x, y: DNA_SIZE - abs(x-y), DNA_FINAL, self.gene)))
    	return cnt / (DNA_SIZE * DNA_SIZE * 1.0)

    #@property
    #def fitness(self) -> int:
    #	cnt = 0
    #	for i in range(DNA_SIZE):
    #		cnt += DNA_SIZE - abs(self.gene[i] - i)
    #	return cnt / (DNA_SIZE * DNA_SIZE * 1.0)

best_start = []
generations = list()
line_mean = deque([0], maxlen = MAX_X)
line_best = deque([0], maxlen = MAX_X)

def evolution(fn, ld):
	generation = generations[-1].evolution()
	generations.append(generation)
	fitness = generation.fitness()

	print("%s %s %s" % (repr(generation), repr(generation.best), fitness))

	#line_mean.append(fitness)
	line_best.append(generation.best.fitness)
	plot([MAX_FITNESS] * MAX_X, color='red')
	#ld.set_data(range(0, len(line_mean)), line_mean)
	ld.set_data(range(0, len(line_best)), line_best)

	if generation.best.fitness >= MAX_FITNESS:
		print("""
	Genetic Algorithm Test: 

	DNA_START = %s
	DNA_FINAL = %s
	take %d gen
	DNA size: %d
	Child in a Gen: %d

	Select best rate: %f
	Mutation rate: %f
	Cross rate: %f
	

	input any key to exit: 
""" % (best_start, generation.best, generation.level, DNA_SIZE, CHILD_CNT, SELECT_BEST_RATE, MUTATION_RATE, CROSS_RATE))
		input() # end of program

		raise SystemExit()

if __name__ == '__main__':
	generations.append(Generation([DNA(sufflize()) for _ in range(CHILD_CNT)]))
	best_start = generations[-1].best

	fig = figure()
	l1, = axes(xlim=(0, MAX_X), ylim=(0, MAX_Y)).plot([], [])
	ani = FuncAnimation(fig, evolution, fargs=(l1,), interval=5)

	show()