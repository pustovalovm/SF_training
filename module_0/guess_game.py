# Written by Mikhail Pustovalov, pustovalovm@gmail.com

# Imports
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
    with maximum thinked number of (num_max). Asks user if another try is
    needed.
    Arguments:
        mode - algorithm to be run.
            mode = 0 - random guess
            mode = 1 - linear guess
            mode = 2 - binary guess
            mode = 3 - all above
        cycles - a list of np.random.randint integer numbers is generetad and
        algorithm is run along this list for each number as thinked.
        num_max - highest possible thinked number.
    Returns:
         False if the user has selected to run the script again
         True if the user has selected to stop execution
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
    """
    Random search, one cycle. The function chooses random number from 1 to
    num_max and compares it to the thinked number (number) in an infinite loop
    until it finds one equal to thinked number.
    Arguments:
        number - thinked number
        num_max - highest possible value of thinked number
    Returns:
        Int number of attempts to guess required to find thinked number
    """
    count = 0
    while True:  # Limit number of tries to avoid infinite cycle
        count += 1
        guess = np.random.randint(1, num_max+1)
        if guess == number:
            return count


def linear_search(number, num_max):
    """
    Linear search, one cycle. The function goes through the list of numbers
    from 1 to num_max and compares each number to the thinked number (number)
    until it finds one equal to thinked number.
    Arguments:
        number - thinked number
        num_max - highest possible value of thinked number
    Returns:
        Int number of attempts to guess required to find thinked number
    """
    count = 0
    for guess in range(1, num_max+1):
        count += 1
        if guess == number:
            return count


def binary_search(number, num_max):
    """
    Binary search, one cycle. The function creates the list of numbers
    from 1 to num_max. On each step it takes the median value in this list
    compares number to the thinked number (number). If the number was not
    guessed the function takes a half of the list ("left" thus lesser if our
    median is higher than thinked number and "right" otherwise) as a new
    guess list and repeats this process for this new list until it finds one
    median equal to thinked number.
    Arguments:
        number - thinked number
        num_max - highest possible value of thinked number
    Returns:
        Int number of attempts to guess required to find thinked number
    """
    guess_ls = range(1, num_max + 1)
    count = 0
    while len(guess_ls) > 0:
        count += 1
        guess = guess_ls[len(guess_ls)//2]
        if guess < number:
            guess_ls = guess_ls[len(guess_ls)//2:]
        elif guess > number:
            guess_ls = guess_ls[:len(guess_ls)//2]
        else:
            return count


if __name__ == '__main__':
    stopped = False
    while not stopped:
        stopped = runner(*get_inputs())
