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

def build_model(vocab_size, embedding_dim, rnn_units, batch_size):
    model = tf.keras.Sequential([
                                tf.keras.layers.Embedding(vocab_size, embedding_dim,
                                batch_input_shape=[batch_size, None]),
    tf.keras.layers.GRU(rnn_units,
                        return_sequences=True,
                        stateful=True,
                        recurrent_initializer='glorot_uniform'),
    tf.keras.layers.Dense(vocab_size)
    ])
    return model

def loss(labels, logits):
    return tf.keras.losses.sparse_categorical_crossentropy(labels, logits, from_logits=True)

def Create_Model(source, seq_length, vocab_dir = './vocab.txt'):

    text = open(source, 'rb').read().decode(encoding='utf-8') #Reads file and decodes it

    print ('Length of text: {} characters'.format(len(text)))
    print(text[:250])

    vocab = sorted(set(text))
    print ('{} unique characters'.format(len(vocab)))
    
    # saving vocab to a file that can be used later
    with open(vocab_dir, 'w', encoding="utf8") as file:
        for item in vocab:
            file.write(item)

    char2idx, idx2char = mapping(vocab)

    text_as_int = np.array([char2idx[c] for c in text])

    print('{')
    for char,_ in zip(char2idx, range(20)):
        print('  {:4s}: {:3d},'.format(repr(char), char2idx[char]))
    print('  ...\n}')

    print ('{} ---- characters mapped to int ---- > {}'.format(repr(text[:13]), text_as_int[:13]))

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

    # Batch size
    BATCH_SIZE = 64

    # Buffer size to shuffle the dataset
    # (TF data is designed to work with possibly infinite sequences,
    # so it doesn't attempt to shuffle the entire sequence in memory. Instead,
    # it maintains a buffer in which it shuffles elements).
    BUFFER_SIZE = 10000

    dataset = dataset.shuffle(BUFFER_SIZE).batch(BATCH_SIZE, drop_remainder=True)

    print(dataset)

    # Length of the vocabulary in chars
    vocab_size = len(vocab)

    # The embedding dimension
    embedding_dim = 256

    # Number of RNN units
    rnn_units = 1024

    model = build_model(
        vocab_size = vocab_size,
        embedding_dim=embedding_dim,
        rnn_units=rnn_units,
        batch_size=BATCH_SIZE)

    return model, dataset, idx2char, char2idx, vocab_size

def train_model(model, dataset, EPOCHS, checkpoint_dir = './training_checkpoints', vocab_dir = './vocab.txt'):

    for input_example_batch, target_example_batch in dataset.take(1):
        example_batch_predictions = model(input_example_batch)
        print(example_batch_predictions.shape, "# (batch_size, sequence_length, vocab_size)")

    model.summary()

    for input_example_batch, target_example_batch in dataset.take(1):
        example_batch_predictions = model(input_example_batch)
        print(example_batch_predictions.shape, "# (batch_size, sequence_length, vocab_size)")

    sampled_indices = tf.random.categorical(example_batch_predictions[0], num_samples=1)
    sampled_indices = tf.squeeze(sampled_indices,axis=-1).numpy()

    print(sampled_indices)

    print("Input: \n", repr("".join(idx2char[input_example_batch[0]])))
    print()
    print("Next Char Predictions: \n", repr("".join(idx2char[sampled_indices ])))

    example_batch_loss  = loss(target_example_batch, example_batch_predictions)
    print("Prediction shape: ", example_batch_predictions.shape, " # (batch_size, sequence_length, vocab_size)")
    print("scalar_loss:      ", example_batch_loss.numpy().mean())

    model.compile(optimizer='adam', loss=loss)    

    # Name of the checkpoint files
    checkpoint_prefix = os.path.join(checkpoint_dir, "ckpt_{epoch}")

    checkpoint_callback=tf.keras.callbacks.ModelCheckpoint(
        filepath=checkpoint_prefix,
        save_weights_only=True)

    history = model.fit(dataset, epochs=EPOCHS, callbacks=[checkpoint_callback])

def mapping(vocab):
    # mapping every unique caracter
    char2idx = {u:i for i, u in enumerate(vocab)}
    idx2char = np.array(vocab)
    return char2idx, idx2char

if __name__ == "__main__":
    from Generate_Caption import generate_text, import_mapping

    model, dataset, idx2char, char2idx, vocab_size = Create_Model("./Captions/Captions.txt", 50)

    train_model(model, dataset, EPOCHS = 10, checkpoint_dir = './Captions/training_checkpoints', vocab_dir = './vocab.txt')

    tf.train.latest_checkpoint('./Captions/training_checkpoints') 

    model = build_model(vocab_size, embedding_dim = 256, rnn_units = 1024, batch_size=1)

    model.load_weights(tf.train.latest_checkpoint('./Captions/training_checkpoints'))

    model.build(tf.TensorShape([1, None]))

    model.summary()

    print(generate_text(model, start_string=u"Olá ", char2idx = char2idx, idx2char = idx2char))

