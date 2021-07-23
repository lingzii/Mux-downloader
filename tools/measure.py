from time import perf_counter


def measureTime(target):
    beg = perf_counter()
    target()
    end = perf_counter()
    return f'{end-beg:.1f}'
