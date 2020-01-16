import tensorflow as tf
from Create_Model import mapping, build_model

def generate_text(model, start_string, char2idx, idx2char, temperature = 1):
  # Evaluation step (generating text using the learned model)

  # Number of characters to generate
  num_generate = 1000

  # Converting our start string to numbers (vectorizing)
  input_eval = [char2idx[s] for s in start_string]
  input_eval = tf.expand_dims(input_eval, 0)

  # Empty string to store our results
  text_generated = []

  # Low temperatures results in more predictable text.
  # Higher temperatures results in more surprising text.
  # Experiment to find the best setting.
  # temperature = 1

  # Here batch size == 1
  model.reset_states()
  for i in range(num_generate):
    predictions = model(input_eval)
    # remove the batch dimension
    predictions = tf.squeeze(predictions, 0)

    # using a categorical distribution to predict the word returned by the model
    predictions = predictions / temperature
    predicted_id = tf.random.categorical(predictions, num_samples=1)[-1,0].numpy()

    # We pass the predicted word as the next input to the model
    # along with the previous hidden state
    input_eval = tf.expand_dims([predicted_id], 0)

    text_generated.append(idx2char[predicted_id])

  return (start_string + ''.join(text_generated))

def import_mapping(file_dir):
  text = open(file_dir, 'rb').read().decode(encoding='utf-8') #Reads file and decodes it

  vocab = sorted(set(text))
  print ('{} unique characters'.format(len(vocab)))

  vocab_size = len(vocab)
  char2idx, idx2char = mapping(vocab)
  return vocab_size, char2idx, idx2char

if __name__ == "__main__":
  vocab_size, char2idx, idx2char = import_mapping('./Captions/vocab.txt')

  model = build_model(vocab_size, embedding_dim = 256, rnn_units = 1024, batch_size=1)

  model.load_weights(tf.train.latest_checkpoint('./Captions/training_checkpoints_11_01_19'))

  model.build(tf.TensorShape([1, None]))

  model.summary()

  while True:
    try:
      temp = float(input("temp="))

      print(generate_text(model, start_string=u"Olá ", char2idx = char2idx, idx2char = idx2char, temperature = temp))
    except: pass