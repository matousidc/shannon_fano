"""
Má to fungovat tak, že se tomu hodí input.. třeba nejaký soubor, nebo stdin (standard input)
Ten to zmenší
A má to fungovat i tak aby to ten zmenšenej vratilo zpět
Takže bych si predstavoval nejaký parametry
Treba -e jako encode
A -d jako decode
recursion

How to run example:
python -m shannon_fano 'abcfdedf' encode
"""
import argparse
import json

text0 = 'Its had resolving otherwise she contented therefore. Afford relied warmth out sir hearts sister'
text_test = 25 * 'a' + 25 * 'b' + 20 * 'c' + 15 * 'd' + 10 * 'e' + 5 * 'f'


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="data file")
    parser.add_argument("process", help="encode or decode", choices=['encode', 'decode'])
    return parser.parse_args()


def inputs(text: str) -> (list, list):
    with open(text, 'r') as file:
        text = file.read()
    input_list = [i for i in text]
    list_unique = list(set(input_list))
    prob = []
    for i in list_unique:
        prob.append(input_list.count(i)/len(input_list))
    return list_unique, prob


def split(value: list) -> (list, list):
    check = []
    j = 0
    for i in range(len(value)):
        first = value[:len(value) // 2 - i]
        second = value[len(value) // 2 - i:]
        if not first:
            j = i - 1
            break
        check.append(sum(second) / sum(first))
        if i > 0:
            if abs(1 - check[i]) < abs(1 - check[i - 1]):
                continue
            else:
                j = i - 1
                break
    first = value[:len(value) // 2 - j]
    second = value[len(value) // 2 - j:]
    return first, second


def next_keys(keys: list) -> list:
    keys = [i for i in keys if len(i) == len(keys[-1])]     # include only latest tree level
    output = []
    for i in keys:
        output.append(i+'0')
        output.append(i+'1')
    return output


def next_values(values: list, keys: list) -> list:
    values = values[int(len(values)-len(keys)/2):]      # include only latest tree level
    output = []
    for i in values:
        if len(i) == 1:
            output.append([])
            output.append([])
        else:
            one, two = split(i)
            output.append(one)
            output.append(two)
    return output


def starting(list_unique: list, prob: list) -> (list, list, dict):
    prob, list_unique = (list(t) for t in zip(*sorted(zip(prob, list_unique), reverse=True)))   # sorting
    one, two = split(prob)                              # first split
    tree_dict = {'0': one, '1': two}
    return list_unique, prob, tree_dict


def binary_tree(tree: dict) -> dict:
    keys = next_keys([i for i in tree.keys()])
    values = next_values([i for i in tree.values()], keys)
    keys[:] = [x for x, y in zip(keys, values) if y]       # deleting empty indexes
    values[:] = [x for x in values if x]
    for i, j in zip(keys, values):
        tree[i] = j
    if all(len(x) == 1 for x in values):
        return tree
    else:
        binary_tree(tree)
    return tree


def replace_binary(list_unique: list, prob: list, tree: dict) -> (dict, dict):
    tree = {key: value for (key, value) in tree.items() if len(value) == 1}
    result = dict()
    for (k, l) in tree.items():
        for i, j in zip(list_unique, prob):
            if j == l[0]:
                result[k] = i
                list_unique.remove(i)
                prob.remove(j)
                break
    return tree, result


def replace_text(text: str, result: dict) -> str:
    output = ''
    for num, i in enumerate(text):
        for (j, k) in result.items():
            if i == k:
                output += j
    return output


def main():
    args = arguments()
    file = args.file
    process = args.process
    print(file, process)
    # list_unique, prob = inputs(text_test)
    list_unique, prob = inputs(file)
    list_unique, prob, tree_dict = starting(list_unique, prob)
    tree = binary_tree(tree_dict)
    check = [x for x in tree.values() if len(x) == 1]
    if len(check) == len(list_unique):
        print(f'Correct, length = {len(check)}')

    tree, result = replace_binary(list_unique, prob, tree)
    print(json.dumps(tree, indent=4))
    print(json.dumps(result, indent=4))
    final = replace_text(text_test, result)
    # with open('text_test.txt', 'w') as file:
    #     file.write(final)


if __name__ == "__main__":
    main()
