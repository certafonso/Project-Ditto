import os
import numpy as np
import tensorflow as tf

def GetCaptions(path):
    captions = []
    for filename in os.listdir(path):
        if filename.endswith(".txt"):
            with open(path + filename, "r", encoding="utf8") as file:
                for line in file:
                    captions.append(line)

    with open("Captions.txt","w+", encoding="utf8") as file:
        for caption in captions:
            file.write(caption + "\n")

def split_input_target(chunk):
    input_text = chunk[:-1]
    target_text = chunk[1:]
    return input_text, target_text

if __name__ == "__main__":
    path = "./Captions.txt"

    text = open(path, 'rb').read().decode(encoding='utf-8') #Reads file and decodes it

    print ('Length of text: {} characters'.format(len(text)))
    print(text[:250])

    vocab = sorted(set(text))
    print ('{} unique characters'.format(len(vocab)))

    # mapping every unique caracter
    char2idx = {u:i for i, u in enumerate(vocab)}
    idx2char = np.array(vocab)

    text_as_int = np.array([char2idx[c] for c in text])

    print('{')
    for char,_ in zip(char2idx, range(20)):
        print('  {:4s}: {:3d},'.format(repr(char), char2idx[char]))
    print('  ...\n}')

    print ('{} ---- characters mapped to int ---- > {}'.format(repr(text[:13]), text_as_int[:13]))

    seq_length = 100 # Maximum length of the input
    examples_per_epoch = len(text)//(seq_length+1)

    char_dataset = tf.data.Dataset.from_tensor_slices(text_as_int) # creates input slices

    for i in char_dataset.take(5):
        print(idx2char[i.numpy()])

    sequences = char_dataset.batch(seq_length+1, drop_remainder=True)

    for item in sequences.take(5):
        print(repr(''.join(idx2char[item.numpy()])))

    dataset = sequences.map(split_input_target) #creates dataset

    for input_example, target_example in  dataset.take(1):
        print ('Input data: ', repr(''.join(idx2char[input_example.numpy()])))
        print ('Target data:', repr(''.join(idx2char[target_example.numpy()])))

    for i, (input_idx, target_idx) in enumerate(zip(input_example[:5], target_example[:5])):
        print("Step {:4d}".format(i))
        print("  input: {} ({:s})".format(input_idx, repr(idx2char[input_idx])))
        print("  expected output: {} ({:s})".format(target_idx, repr(idx2char[target_idx])))