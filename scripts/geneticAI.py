import random
import pickle
# Параметры генетического алгоритма
TARGET = "небо имеет цвет синий"
GENOME_LENGTH = len(TARGET)
POPULATION_SIZE = 100
MUTATION_RATE = 0.01
TOURNAMENT_SIZE = 5

# Генерация случайной строки
def generate_random_genome(length):
    return ''.join(random.choice('небо синего цвета') for _ in range(length))

# Инициализация популяции
def generate_population(size, genome_length):
    return [generate_random_genome(genome_length) for _ in range(size)]

# Оценка приспособленности
def fitness(genome):
    return sum(genome[i] == TARGET[i] for i in range(GENOME_LENGTH))

# Отбор для размножения
def selection(population):
    winners = []
    for _ in range(len(population)):
        tournament = random.sample(population, TOURNAMENT_SIZE)
        winners.append(max(tournament, key=fitness))
    return winners

# Кроссовер
def crossover(a, b):
    pivot = random.randint(0, GENOME_LENGTH)
    return a[:pivot] + b[pivot:], b[:pivot] + a[pivot:]

# Мутация
def mutate(genome):
    genome_list = list(genome)
    for i in range(len(genome_list)):
        if random.random() < MUTATION_RATE:
            genome_list[i] = random.choice('абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ, !')
    return ''.join(genome_list)

def save_population(population, filename='population.pkl'):
    with open(filename, 'wb') as file:
        pickle.dump(population, file)

# Главный цикл генетического алгоритма
population = generate_population(POPULATION_SIZE, GENOME_LENGTH)

for generation in range(1, 101111):
    # Оценка приспособленности каждой особи
    population = sorted(population, key=fitness, reverse=True)
    
    # Проверка на соответствие целевой строке
    if fitness(population[0]) == GENOME_LENGTH:
        print(f"Найдено совпадение на поколении {generation}!")
        print(population[0])
        save_population(population, filename=f'/scripts/genetic/best_population_gen_{generation}.pkl')
        break

    # Отбор и размножение
    next_generation = selection(population)
    population = []

    # Скрещивание и мутация для создания новой популяции
    for i in range(0, POPULATION_SIZE, 2):
        parent1, parent2 = next_generation[i], next_generation[i+1]
        child1, child2 = crossover(parent1, parent2)
        population.append(mutate(child1))
        population.append(mutate(child2))

