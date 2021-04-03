# __author__ = "Monowar Hasan"
# __email__ = "mhasan11@illinois.edu"


import random
import dill  # pickle will fail if we remove this line
import gzip


def UUniFast(n, U):
    """ Classic UUniFast algorithm """
    sumU = U  # sum of n uniform random variables
    vectU = []
    for i in range(1, n):  # iterate over i to n-1
        nextSumU = sumU * random.random() ** (1.0 / (n - i))  # the sum of n-i uniform random variables
        vectU.append(sumU - nextSumU)
        sumU = nextSumU
    vectU.append(sumU)

    return vectU


def write_object_to_file(input_obj, filename):
    """ Write the input object to a Pickle file """

    print("Writing as a Pickle object...")
    with gzip.open(filename, 'wb') as handle:
        dill.dump(input_obj, handle)


def load_object_from_file(filename):
    """ Load the given object from Pickle file """

    with gzip.open(filename, 'rb') as handle:
        output = dill.load(handle)

    return output
