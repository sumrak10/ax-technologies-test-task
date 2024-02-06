import random
import string


def generate_random_string(length: int, only_digits: bool = False, only_letters: bool = False) -> str:
    array = []
    if only_digits and only_letters:
        array = string.ascii_letters + string.digits
    elif only_digits:
        array = string.digits
    elif only_letters:
        array = string.ascii_letters
    crypt_rand_string = ''.join(random.choice(array)
                                for i in range(length))
    return crypt_rand_string
