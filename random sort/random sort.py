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

# 한 세대의 개체 수를 나타냅니다.
CHILD_CNT = 64

# DNA의 크기를 나타냅니다. (여기선 정렬할 원소의 갯수)
DNA_SIZE = 16;
# DNA의 원하는 결과를 나타냅니다. (여기선 정렬된 DNA_SIZE크기의 리스트)
DNA_FINAL = [x for x in range(DNA_SIZE)]

## RATE는 0~1의 값을 가져야 합니다.
# 다음 세대에 이전 세대에서 가장 적합도가 높은 개체를 얼마나 전달할지 결정합니다.
SELECT_BEST_RATE = 0.5
# 돌연변이가 일어날 확률입니다.
MUTATION_RATE = 0.6
# 교차가 일어날 호가률입니다.
CROSS_RATE = 0.3

# 적합도는 0~1사이의 값으로 나타내기 때문에 1이 되면 진화가 끝난것으로 간주합니다.
MAX_FITNESS = 1

# 그래프의 크기를 결정합니다.
MAX_X = 100
MAX_Y = 1.1

def rand(x, y):
	return randrange(x, y)

# 어떤 확률이 발생했는지 안했는지를 판단합니다.
def event(rate):
	return True if uniform(0.0, 1.0) < rate else False

# 리스트를 셔플합니다. (원소가 중복되지 않도록)
def sufflize(func = lambda x : rand(0, DNA_SIZE)):
	ret = [-1] * (DNA_SIZE)
	for i in range(DNA_SIZE):
		p = func(i)
		while ret[p] != -1:
			p = func(i)
		ret[p] = i
	return ret

# 휠에서 선택을 합니다. 각 휠의 크기는 람다를 이용한 func인자로 결정할 수 있습니다.
def wheel_choice(items, func = lambda x : x.fitness):
	p = uniform(0.0, sum([func(x) for x in items]))
	c = 0
	for i in items:
		c += func(i)
		if c>p:
			return i

# 한 세대를 나타내는 클래스 입니다.
class Generation:
    cnt = 0
    def __init__(self, dna_list):
        Generation.cnt += 1
        self.level = Generation.cnt
        self.DNA_list = dna_list

    def __repr__(self):
        return "<Gen %d>" % self.level

    # 이번 세대에서 다음 세대의 자식들을 반환해 줍니다.
    # 현재 세대에서 휠 선택으로 부모를 선택해 교배합니다.
    def next_child(self):
    	return DNA(wheel_choice(self.DNA_list).child(wheel_choice(self.DNA_list)))

    # 다음 세대를 반환합니다.
    # SELECT_BEST_RATE만큼의 BEST 개체들과 next_child를 이용한 자식들로 이루어진 세대를 반환합니다. 
    def evolution(self):
        childs = [self.best if event(SELECT_BEST_RATE) else self.next_child() for _ in range(CHILD_CNT)]
        return Generation(childs)

    # 현재 세대의 적합도를 나타냅니다. numpy의 mean이 사용됩니다.
    def fitness(self):
    	return mean([dna.fitness for dna in self.DNA_list])

   	# 이번 세대에서 가장 적합도가 높은 개체입니다.
    @property
    def best(self):
        return sorted(self.DNA_list, key=lambda x: x.fitness)[-1]

# 어떤 한 개체를 나타냅니다. 각 개체는 특정한 DNA를 가지고 있습니다.
class DNA:
    def __init__(self, gene = sufflize()):
        self.gene = gene

    def __repr__(self):
        return "[DNA %s |FIT %.2f]\n" % (", ".join(str(x) for x in self.gene), self.fitness)

    def __str__(self):
    	return "[ %s ]" % ", ".join(str(x) for x in self.gene)

   	# 다른 개체와 교배한 자식을 반환합니다.
   	# CROSS_RATE를 이용한 교차가 일어나고
   	# MUTATION_RATE를 이용한 돌연변이가 일어납니다.
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

	# 이 개체의 적합도입니다. 이 적합도는 실제 값과 목적 값의 차이를 나타냅니다.
    @property
    def fitness(self) -> int:
    	cnt = 0
    	for tar, obj in zip(DNA_FINAL, self.gene):
    		cnt += DNA_SIZE - abs(tar - obj)
    	#생각보다 람다 구문이 너무 느림
    	#cnt = reduce(lambda x, y: x + y, list(map(lambda x, y: DNA_SIZE - abs(x-y), DNA_FINAL, self.gene)))
    	return cnt / (DNA_SIZE * DNA_SIZE * 1.0)

    #diff 체크를 사용한 fitness 계산, (매우느림)
    #@property
    #def fitness(self) -> int:
    #	cnt = 0
    #	for i in range(DNA_SIZE):
    #		cnt += DNA_SIZE - abs(self.gene[i] - i)
    #	return cnt / (DNA_SIZE * DNA_SIZE * 1.0)

# 시작 세대에서 가장 좋은 개체를 저장합니다.
# 이는 시작 세대에서 얼마나 빠르게 발전했는지를 나타내는데 사용될 수 있습니다.
best_start = []
# 각 세대들을 담고있는 리스트입니다.
generations = list()
line_mean = deque([0], maxlen = MAX_X)
line_best = deque([0], maxlen = MAX_X)

# 세대를 진행시킵니다.
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

	# 테스트결과 출력
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
	# 첫 세대는 램덤하게 발생됩니다.
	generations.append(Generation([DNA(sufflize()) for _ in range(CHILD_CNT)]))
	best_start = generations[-1].best

	fig = figure()
	l1, = axes(xlim=(0, MAX_X), ylim=(0, MAX_Y)).plot([], [])
	ani = FuncAnimation(fig, evolution, fargs=(l1,), interval=5)

	show()