import random
import numpy as np


def pick_new(word_dict, l_word, word_list):
    rng = list(range(len(word_dict[l_word])))
    random.shuffle(rng)
    random.shuffle(rng)
    choices = list(np.array(word_dict[l_word])[rng])
    for i in range(len(choices)):
        l = len(choices)
        if l > 0:
            if choices[i] in word_dict.keys():
                if choices[i] not in word_list:
                    new_word = choices[i]
                    word_list.append(new_word)
                    break
                else:
                    choices.remove(choices[i])
        else:
            raise ValueError('No choices left')
    return new_word, word_list

def pick_set(word_dict):
    word_list = []
    word1 = random.choice(list(word_dict.keys()))
    word_list.append(word1)
    
    word2, word_list = pick_new(word_dict, word1, word_list)
    word3, word_list = pick_new(word_dict, word2, word_list)
    word4, word_list = pick_new(word_dict, word3, word_list)
    word5, word_list = pick_new(word_dict, word4, word_list)
    word6, word_list = pick_new(word_dict, word5, word_list)
    word7, word_list = pick_new(word_dict, word6, word_list)
    word8, word_list = pick_new(word_dict, word7, word_list)
    word9, word_list = pick_new(word_dict, word8, word_list)
    _, word_list = pick_new(word_dict, word9, word_list)
    return word_list