def find_index(listOfDict, dict_key, value):
    return next((index for (index, d) in enumerate(listOfDict) if d[dict_key] == value), None)