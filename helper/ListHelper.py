def all2(key, arr):
    """ 判断 arr 中是否都满足 key 条件 """
    for item in arr:
        if not key(item): return False
    return True


def any2(key, arr):
    """ 判断 arr 中是否有满足 key 条件 """
    for item in arr:
        if key(item): return True
    return False


def remove_empty(arr):
    """ 删除列表中的空串 """
    if any2(lambda x: not isinstance(x, str), arr): return arr
    return list(filter(lambda x: bool(x), list(map(lambda x: x.strip(), arr))))
