"""A fun number guessing game!"""

import random

def main():
    number = random.randint(1, 100)
    guesses = 0

    print("I'm thinking of a number, between 1 and 100. Can you guess what it is?")
    while True:
        guesses += 1
        guess = input('= ')
        try:
            guess = int(guess)
        except ValueError:
            print("Base 10 integers only, please.")
            continue

        if guess > number:
            print("Too high!")
        elif guess <  number:
            print("Too low!")
        else:
            print("That's right, {}. You got it in {} guesses.".format(number, guesses))
            break

    print()
    input("Press enter to quit.")
