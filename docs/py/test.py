def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def get_bin(x, n):
    '''
    Return the 2's complement of the integer number $x$
    for a given bitwidth $n$.
    '''
    if (not is_number(x)):
        raise ValueError('get_bin: parameter {} is not a number.'.format(x))

    return '{0:{fill}{width}b}'.format((int(x) + 2**n) % 2**n,
                                       fill='0', width=n)

def bitstr(x, n, signed=False):
    assert(n > 0)
    if signed:
        assert(-2**(n-1) <= x <= 2**(n-1) - 1)
    else:
        assert(0 <= x <= 2**n - 1)

    result = ['0'] * n

    if signed:
        if x < 0:
            result[n-1] = '1'
            x = 2**n + x
        else:
            result[n-1] = '0'
    else:
        if x > 2**(n-1):
            result[n-1] = '1'
            x = x - 2**(n-1)
        else:
            result[n-1] = '0'

    for i in range(n-1):
        result[i] = '{}'.format(x % 2);
        print("i: ", i, " result[i]: ", result[i])
        x = int((x - int(result[i])) / 2);

    return "".join(result)

