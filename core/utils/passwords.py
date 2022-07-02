import random
import string

def generate_random_password():
    """ Picks a random password """
    password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(12))
    return password
