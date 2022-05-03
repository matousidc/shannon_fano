"""
How to run example:
python -m shannon_fano file.txt encode
python -m shannon_fano text_test.txt decode

header:
letter as a byte, len(key of letter) as byte, key of letter, '@@@' as bytes - end of header
"""
import argparse
import json
from bitarray import bitarray


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="data file")
    parser.add_argument("process", help="encode or decode", choices=['encode', 'decode'])
    return parser.parse_args()


def inputs(text: str) -> (list, str):
    with open(text, 'r') as file:
        text = file.read()
    input_list = [i for i in text]
    list_unique = list(set(input_list))
    nodes = []
    for i in list_unique:
        nodes.append({'p': input_list.count(i) / len(input_list), 'char': i})
    return nodes, text


def split(value: list) -> (list, list):
    check = []
    j = 0
    for i in range(len(value)):
        first = value[:len(value) // 2 - i]
        second = value[len(value) // 2 - i:]
        if not first:
            j = i - 1
            break
        check.append(sum(i['p'] for i in second) / sum(i['p'] for i in first))
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
    keys = [i for i in keys if len(i) == len(keys[-1])]  # include only latest tree level
    output = []
    for i in keys:
        output.append(i + '0')
        output.append(i + '1')
    return output


def next_values(values: list, keys: list) -> (list, dict):
    values = values[int(len(values) - len(keys) / 2):]  # include only latest tree level
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


def starting(nodes: list) -> (list, list, dict):
    nodes = sorted(nodes, key=lambda k: k['p'], reverse=True)
    one, two = split(nodes)                          # first split
    tree_dict = {'0': one, '1': two}
    return nodes, tree_dict


def binary_tree(tree: dict) -> dict:
    keys = next_keys([i for i in tree.keys()])
    values = next_values([i for i in tree.values()], keys)
    keys[:] = [x for x, y in zip(keys, values) if y]        # deleting empty indexes
    values[:] = [x for x in values if x]
    for i, j in zip(keys, values):
        tree[i] = j
    if all(len(x) == 1 for x in values):
        return tree
    else:
        binary_tree(tree)
    return tree


def replace_binary(tree: dict) -> (dict, dict):
    tree = {key: value for (key, value) in tree.items() if len(value) == 1}
    result = dict()
    for (k, l) in tree.items():
        result[k] = l[0]['char']
    return tree, result


def create_body(text: str, result: dict) -> bitarray:
    output = bitarray()
    for num, i in enumerate(text):
        for (j, k) in result.items():
            if i == k:
                for m in j:
                    output.append(int(m))
    return output


def create_header(result: dict) -> bitarray:
    byte_letters = []
    byte_lens = []
    byte_keys = []
    byte_separator = 3*' '.join('{0:08b}'.format(ord(x), 'b') for x in '@')
    for i, j in result.items():
        byte_letter = ' '.join('{0:08b}'.format(ord(x), 'b') for x in j)
        byte_len = '{0:08b}'.format(len(i))
        byte_keys.append(i)
        byte_letters.append(byte_letter)
        byte_lens.append(byte_len)

    header = bitarray()
    for i, j, k in zip(byte_letters, byte_lens, byte_keys):
        for m in i:
            header.append(int(m))
        for n in j:
            header.append(int(n))
        for o in k:
            header.append(int(o))
    for i in byte_separator:
        header.append(int(i))           # separator - end of header
    return header


def decode(text: bitarray) -> str:
    key = {}
    text = ''.join(str(text[i]) for i in range(len(text)))
    for i in range(len(text)):
        if chr(int(text[:8], 2)) == '@':
            if chr(int(text[:8], 2)) == '@':
                if chr(int(text[:8], 2)) == '@':
                    text = text[3*8:]
                    break
        letter = chr(int(text[:8], 2))
        text = text[8:]
        length = int(text[:8], 2)
        text = text[8:]
        key[text[:length]] = letter
        text = text[length:]
    result = ''
    num = min([len(i) for i in key.keys()]) - 1
    while num <= length:
        for j, k in key.items():
            if text[:num] == j:
                result += k
                text = text[num:]
                num = 0
        num += 1
    return result


def main():
    args = arguments()
    file = args.file
    if args.process == 'encode':
        nodes, text = inputs(file)
        nodes, tree_dict = starting(nodes)
        tree = binary_tree(tree_dict)
        tree, result = replace_binary(tree)
        final = create_body(text, result)
        header = create_header(result)
        final = header + final
        with open('text_encoded.txt', 'wb') as file:
            final.tofile(file)
    elif args.process == 'decode':
        a = bitarray()
        with open(file, 'rb') as file:
            a.fromfile(file)
        final = decode(a)
        with open('text_decoded.txt', 'w') as file:
            file.write(final)


if __name__ == "__main__":
    main()
