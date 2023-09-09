import random
from __main__ import *


# noinspection PyStatementEffect
def add_to_list_in_dict(dictionary: dict, key, new_element) -> dict:
    if dictionary is None:
        return {key: new_element}
    try:
        dictionary[key]
        exists = True
    except (ValueError, KeyError):
        exists = False
    if not exists:
        dictionary[key] = [new_element]
        return dictionary
    current_list = dictionary[key]
    if not isinstance(current_list, list):
        raise RuntimeError("Key object is not a list.")
    current_list.append(new_element)
    dictionary[key] = current_list
    return dictionary


def randomize(clazz, amount_per_group: int = -1, amount_of_groups=-1, round_up=False):
    names = clazz.get_members()
    if amount_per_group >= len(names):
        raise RuntimeError("The group length cannot be bigger than the length of names.")

    if amount_of_groups == -1:
        amount_of_groups = round(len(names) / amount_per_group)

    groups = {}
    shuffled_names = names
    random.shuffle(shuffled_names)
    for index, name in enumerate(shuffled_names):
        groups = add_to_list_in_dict(groups, index % amount_of_groups, name)

    immutable_group_keys = groups.copy()
    for key in immutable_group_keys.keys():
        values = immutable_group_keys[key]
        if len(values) < amount_per_group and round_up is True:
            for value in values:
                groups = add_to_list_in_dict(groups, key - 1, value)
            groups.pop(key)

    return groups


if __name__ == "__main__":
    os.system("title Group Assigner")

    classes = __main__.get_files("//classes//")
        
    
    per_group = int(input("Per group: "))
    groups = int(input("Groups: "))
    if groups < 1:
        groups = 0
    if per_group < 1:
        per_group = 0
        
