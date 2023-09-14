"""
6.1010 Spring '23 Lab 9: Autocomplete
"""

# NO ADDITIONAL IMPORTS!
import doctest
from text_tokenize import tokenize_sentences


class PrefixTree:
    def __init__(self):
        self.value = None
        self.children = {}

    def get_val(self, key):
        """ "Gets the actual value of the key"""
        if len(key) == 0:
            if self.value is None:
                return 0
            return self.value

        else:
            return self.children[key[0]].get_val(key[1:])

    def __setitem__(self, key, value):
        """
        Add a key with the given value to the prefix tree,
        or reassign the associated value if it is already present.
        Raise a TypeError if the given key is not a string.
        """

        if not isinstance(key, str):
            raise TypeError
        elif len(key) == 0:
            self.value = value
        else:
            if key[0] not in self.children:
                self.children[key[0]] = PrefixTree()

            self.children[key[0]].__setitem__(key[1:], value)

    def __getitem__(self, key):
        """
        Return the value for the specified prefix.
        Raise a KeyError if the given key is not in the prefix tree.
        Raise a TypeError if the given key is not a string.
        # >>> __getitem__(self,'bark')
        #  ':)'
        """

        if not isinstance(key, str):
            raise TypeError
        elif len(key) == 0:
            if self.value is None:
                raise KeyError
            return self.value
        else:
            return self.children[key[0]].__getitem__(key[1:])

    def __delitem__(self, key):
        """
        Delete the given key from the prefix tree if it exists.
        Raise a KeyError if the given key is not in the prefix tree.
        Raise a TypeError if the given key is not a string.
        """
        if not isinstance(key, str):
            raise TypeError

        elif len(key) == 0:
            if self.value is None:
                raise KeyError
            self.value = None
        else:
            return self.children[key[0]].__delitem__(key[1:])

    def __contains__(self, key):
        """
        Is key a key in the prefix tree?  Return True or False.
        Raise a TypeError if the given key is not a string.
        """

        if not isinstance(key,str):
            raise TypeError

        elif len(key) == 0:
            if self.value is None:
                return False
            return True
        else:
            if key[0] not in self.children:
                return False
            return self.children[key[0]].__contains__(key[1:])

    def __iter__(self):
        """
        Generator of (key, value) pairs for all keys/values in this prefix tree
        and its children.  Must be a generator!
        """
        for key, child in self.children.items():

            if child.value is not None:
                yield (key, child.value)

            for tup in child.__iter__():
                yield (key + tup[0], tup[1])

    def __repr__(self) -> str:
        """makes the tree printable"""
        return f"{self.children},{self.value}"

    def get_children(self, key):
        """get subtree when a key is passed in"""
        current = self
        if len(key) == 0:
            return current
        else:
            if key[0] not in self.children:
                return None
            return current.children[key[0]].get_children(key[1:])

    def loop(self):
        """returns a list of single letter keys"""
        keys_list = []
        for key, value in self.children.items():
            keys_list.append(key)
        return keys_list


def sort(tree):
    """sorts the tree from max to min based on values"""
    d_temp = {}
    for key, val in tree:
        d_temp.update([(key, val)])
    sorted_l = sorted(d_temp.items(), key=lambda x: x[1], reverse=True)
    sorted_dict = dict(sorted_l)
    return sorted_dict


def count(strings):
    """takes in a list of strings and returns a dictionary
    with the words and count
    """
    words = {}
    for string_list in strings:
        for word in string_list.split():
            if word in words:

                words[word] += 1
            else:
                words[word] = 1
    return words


def word_frequencies(text):
    """
    Given a piece of text as a single string, create a prefix tree whose keys
    are the words in the text, and whose values are the number of times the
    associated word appears in the text.
    """
    strings = tokenize_sentences(text)

    count_dict = count(strings)

    tree = PrefixTree()
    for key, value in count_dict.items():
        tree[key] = value
    return tree


def autocomplete(tree, prefix, max_count=None):
    """
    Return the list of the most-frequently occurring elements that start with
    the given prefix.  Include only the top max_count elements if max_count is
    specified, otherwise return all.

    Raise a TypeError if the given prefix is not a string.

    """
    cont = []
    new_prefixes = [prefix]
    if not isinstance(prefix, str):
        raise TypeError
    if tree.get_children(prefix) is not None:
        if tree.get_val(prefix) != 0:
            cont.append(prefix)

        sorted_child = sort(tree.get_children(prefix))
        for key, val in sorted_child.items():

            if tree.get_val(prefix + key) != 0:
                cont.append((prefix + key))
                new_prefixes.append(prefix + key)
            else:
                return []
    else:
        return []
    return cont[:max_count]


def autocorrect(tree, prefix, max_count=None):
    """
    Return the list of the most-frequent words that start with prefix or that
    are valid words that differ from prefix by a small edit.  Include up to
    max_count elements from the autocompletion.  If autocompletion produces
    fewer than max_count elements, include the most-frequently-occurring valid
    edits of the given word as well, up to max_count total elements.
    """
    alph = "abcdefghijklmnopqrstuvwxyz"
    words = autocomplete(tree, prefix, max_count)
    temp = {}
    # if len(words)<max_count:
    # add a letter
    for indx in range(len(prefix)):
        for letter in alph:
            new = prefix[:indx] + letter + prefix[indx:]
            if new in tree:
                temp.update([(new, tree[new])])
   
    # replace a letter
    for letter in prefix:
        for alpha in alph:
            new_d = prefix.replace(letter, "")
            if new_d in tree:
                temp.update([(new_d, tree[new_d])])
            new = prefix.replace(letter, alpha)
            if new in tree:
                if new != prefix:
                    temp.update([(new, tree[new])])

    # switch letters
    s_list = list(prefix)
    for i in range(0, (len(prefix))):
        if i == len(prefix) - 1:
            pass
        else:
            s_list[i], s_list[i + 1] = s_list[i + 1], s_list[i]
            x = "".join(s_list)
            if x in tree:
                temp.update([(x, tree[x])])

    # sort dictionary

    temp_list = sorted(temp.items(), key=lambda x: x[1], reverse=True)
    extra = [key for key, val in temp_list]
    words.extend(extra)
    return words[:max_count]


def word_filter(tree, pattern):
    """
    Return list of (word, freq) for all words in the given prefix tree that
    match pattern.  pattern is a string, interpreted as explained below:
         * matches any sequence of zero or more characters,
         ? matches any single character,
         otherwise char in pattern char must equal char in word.
    """

    key = ""
    main_tree = tree
    main_list = set()

    def filter_helper(tree, pattern, key):

        if len(pattern) == 0 and key is not None:
            if key in main_tree:
                main_list.add((key, main_tree[key]))
        else:
            if pattern[0] == "*":
                for k, val in tree.children.items():
                    filter_helper(val, pattern, key + k)
                filter_helper(tree, pattern[1:], key)

            elif pattern[0] == "?":
                for k, val in tree.children.items():
                    filter_helper(val, pattern[1:], key + k)
            else:
                subtree = tree.get_children(pattern[0])
                if subtree is not None:
                    filter_helper(subtree, pattern[1:], key + pattern[0])

    filter_helper(tree, pattern, key)
    return list(main_list)


# you can include test cases of your own in the block below.
if __name__ == "__main__":
    doctest.testmod()
    with open("Pride.txt", encoding="utf-8") as f:
        text = f.read()
    deal=word_frequencies(text)
    print(autocorrect(deal,'hear'))
    # strings=tokenize_sentences(text)
    # words=(count(strings))
    # count=0
    # for key,val in words.items():
       
    #      count+=val
    # print(count)
