import numpy as np
import sys

np.random.seed(2)  # Select random seed for experiment reproducibility


def get_inputs():
    """
    Gets, checks and returns the inputs from user: algorithm, number of
    cycles, maximum thinked number.
    No arguments required.
    """
    while True:
        mode = input('Выберите алгоритм угадывания:\n'
                     '0 - Прозивольное угадывание\n'
                     '1 - Линейный поиск\n'
                     '2 - Бинарный поиск\n'
                     '3 - Все\n'
                     '4 - Выход\n')
        cycles = input('Введите количество запусков: ')
        num_max = input('Введите максимальное возможное загаданное число: ')
        if mode not in ['0', '1', '2', '3', '4'] or not cycles.isdigit()\
                or int(cycles) < 1 or not num_max.isdigit()\
                or int(num_max) < 1:
            next_action = input('Некорректный ввод!\n'
                                '1 - Повторить\n'
                                '2 или любой другой ввод - Выйти\n')
            if next_action == '1':
                continue
            else:
                sys.exit()
        else:
            return int(mode), int(cycles), int(num_max)


def runner(mode, cycles, num_max):
    """
    Initializes sequence of random thinked numbers with length of (cycles) and
    maximum of (num_max). Runs selected algorithm (mode) for (cycles) times
    with maximum thinked number of (num_max).
    Ar
    """
    thinked_numbers = np.random.randint(1, num_max, size=cycles)
    if mode == 0:
        results_rand = []
        print(f"Алгоритм произвольного угадывания, {cycles} "
              f"циклов.\nЗагадано число от 1 до {num_max}.")
        for number in thinked_numbers:
            results_rand.append(random_search(number, num_max))
        print(f"Число угадано в среднем за {int(np.mean(results_rand))} "
              f"попыток при помощи произвольного поиска.")
    elif mode == 1:
        print(f"Алгоритм линейного поиска, {cycles} циклов.\nЗагадано "
              f"число от 1 до {num_max}.")
        results_linear = []
        for number in thinked_numbers:
            results_linear.append(linear_search(number, num_max))
        print(f"Число угадано в среднем за {int(np.mean(results_linear))} "
              f"попыток при помощи произвольного поиска.")
    elif mode == 2:
        print(f"Алгоритм бинарного поиска, {cycles} циклов.\nЗагадано "
              f"число от 1 до {num_max}.")
        results_binary = []
        for number in thinked_numbers:
            results_binary.append(binary_search(number, num_max))
        print(f"Число угадано в среднем за {int(np.mean(results_binary))} "
              f"попыток при помощи произвольного поиска.")
        print(max(results_binary))
    elif mode == 3:
        results_rand, results_linear, results_binary = [], [], []
        print(f"\nЗагадано число от 1 до {num_max}, число циклов - {cycles}")
        for number in thinked_numbers:
            results_rand.append(random_search(number, num_max))
            results_linear.append(linear_search(number, num_max))
            results_binary.append(binary_search(number, num_max))
        print(f"Результаты:\nАлгоритм произвольного поиска - "
              f"{int(np.mean(results_rand))} попыток\n"
              f"Алгоритм линейного поиска - "
              f"{int(np.mean(results_linear))} попыток\n"
              f"Алгоритм бинарного поиска - "
              f"{int(np.mean(results_binary))} попыток\n")

    cont_mode = input('Попробовать ещё?\n1 - Да\n2 - Нет\n')
    if cont_mode == '1':
        return False
    else:
        return True


def random_search(number, num_max):
    """Random search, one cycle"""
    count = 0
    while True:  # Limit number of tries to avoid infinite cycle
        count += 1
        guess = np.random.randint(1, num_max+1)
        if guess == number:
            return count


def linear_search(number, num_max):
    """Simple linear search algorithm"""
    count = 0
    for guess in range(1, num_max+1):
        count += 1
        if guess == number:
            return count


def binary_search(number, num_max):
    """Binary search, one cycle"""
    guess_ls = range(1, num_max + 1)
    count = 0
    while len(guess_ls) > 0:
        count += 1
        guess = guess_ls[len(guess_ls)//2]
        if guess < number:
            guess_ls = guess_ls[len(guess_ls)//2:]
        elif guess > number:
            guess_ls = guess_ls[:len(guess_ls) // 2]
        else:
            return count


if __name__ == '__main__':
    stopped = False
    while not stopped:
        stopped = runner(*get_inputs())
