from functools import reduce

def arr_to_map(arr, by):
    def set_value(map, obj):
        key = obj[by]
        map[key] = obj
        return map
    return reduce(set_value, arr, {})
