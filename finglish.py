#!/usr/bin/env python3

import itertools
from functools import reduce

def load_conversion_file(filename):
    with open(filename) as f:
        l = list(f)
        l = [i for i in l if i.strip()]
        l = [i.strip().split() for i in l]
    return {i[0]: i[1:] for i in l}

print('Loading converters...')
beginning = load_conversion_file('f2p-beginning.txt')
middle = load_conversion_file('f2p-middle.txt')
ending = load_conversion_file('f2p-ending.txt')

print('Loading persian word list...')
with open('persian-word-freq.txt') as f:
    word_freq = list(f)
word_freq = [i.strip() for i in word_freq if i.strip()]
word_freq = [i.split() for i in word_freq if not i.startswith('#')]
word_freq = {i[0]: int(i[1]) for i in word_freq}

def f2p_word_internal(word):
    # this function receives the word as separate letters
    persian = []
    for i, letter in enumerate(word):
        if i == 0:
            converter = beginning
        elif i == len(word) - 1:
            converter = ending
        else:
            converter = middle
        conversions = converter.get(letter)
        if conversions == None:
            conversions = letter
        else:
            conversions = ['' if i == 'nothing' else i for i in conversions]
        persian.append(conversions)

    alternatives = itertools.product(*persian)
    alternatives = [''.join(i) for i in alternatives]

    alternatives = [(i, word_freq[i]) if i in word_freq else (i, 0)
                    for i in alternatives]

    if len(alternatives) > 0:
        max_freq = max(freq for _, freq in alternatives)
        alternatives = [(w, float(freq / max_freq)) if freq != 0 else (w, 0.0)
                        for w, freq in alternatives]
    else:
        alternatives = [(''.join(word), 1.0)]

    alternatives.sort(key=lambda r: r[1], reverse=True)

    return alternatives

def variations(word):
    """Create variations of the word based on letter combinations like oo,
sh, etc."""

    if len(word) == 1:
        return [[word[0]]]
    elif word in ['oo', 'ou']:
        return [['u']]
    elif word == 'kha':
        return [['kha'], ['kh', 'a']]
    elif word in ['kh', 'gh', 'ch', 'sh']:
        return [[word]]
    elif len(word) == 2 and word[0] == word[1]:
        return [[word[0]]]

    if word[:2] in ['oo', 'ou']:
        return [['u'] + i for i in variations(word[2:])]
    elif word[:3] == 'kha':
        return \
            [['kha'] + i for i in variations(word[3:])] + \
            [['kh', 'a'] + i for i in variations(word[3:])] + \
            [['k', 'h', 'a'] + i for i in variations(word[3:])]
    elif word[:2] in ['kh', 'gh', 'ch', 'sh']:
        return \
            [[word[:2]] + i for i in variations(word[2:])] + \
            [[word[0]] + i for i in variations(word[1:])]
    elif len(word) >= 2 and word[0] == word[1]:
        return [[word[0]] + i for i in variations(word[2:])]
    else:
        return [[word[0]] + i for i in variations(word[1:])]

def f2p_word(word):
    results = []
    for w in variations(word):
        results.extend(f2p_word_internal(w))

    # return the top three results in order to cut down on the number
    # of possibilities.
    return results[:3]

def f2p(phrase):
    # split the phrase into words and then convert each word.
    results = [f2p_word(w) for w in phrase.strip().split()]

    # create the Cartesian product of the results
    results = list(itertools.product(*results))

    # the results now contain (word, confidence) pairs. re-group these
    # so that words are in one tuple and the confidence values are in
    # another
    results = [list(zip(*r)) for r in results]

    # join the words into phrases, while calculate the multiplication
    # product of the confidence values
    results = [(' '.join(words), reduce(lambda x, y: x * y, confs))
               for words, confs in results]

    # sort based on the confidence (product)
    results.sort(key=lambda r: r[1], reverse=True)

    return results

def main():
    print('finglish: ', end='')
    phrase = input()
    results = f2p(phrase)
    for p, c in results[:10]:
        print(c, p)

if __name__ == '__main__':
    main()