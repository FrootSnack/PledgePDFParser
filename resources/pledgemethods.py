def find_last(elts, element) -> int:
    """Returns the index of the last time the element is found in the given list if present and -1 otherwise."""
    if element in elts:
        return max(i for i, item in enumerate(elts) if item == element)
    return -1


def find_nth(elts, element, n) -> int:
    """Returns the index of the nth time the element is found in the given list if present and -1 otherwise."""
    counter = 0
    index = 0
    for x in elts:
        if x == element:
            counter += 1
        if counter == n:
            return index
        index += 1
    return -1


def find_nth_containing(elts, phrase, n) -> int:
    """Returns the index of the nth term containing the given phrase if present and -1 otherwise."""
    counter = 0
    index = 0
    for x in elts:
        if phrase in x:
            counter += 1
        if counter == n:
            return index
        index += 1
    return -1
