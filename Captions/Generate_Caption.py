import tensorflow as tf
from Create_Model import mapping, build_model
from random import choice

def generate_text(model, start_string, char2idx, idx2char, temperature = 1):
  """
  Generating text from trained model

  Low temperatures results in more predictable text.
  Higher temperatures results in more surprising text.
  """

  # Maximum number of characters to generate
  num_generate = 1000

  # Converting start string to numbers
  input_eval = [char2idx[s] for s in start_string]
  input_eval = tf.expand_dims(input_eval, 0)

  # Empty string to store results
  text_generated = []

  # Here batch size == 1
  model.reset_states()
  for i in range(num_generate):
    predictions = model(input_eval)
    # remove the batch dimension
    predictions = tf.squeeze(predictions, 0)

    # using a categorical distribution to predict the word returned by the model
    predictions = predictions / temperature
    predicted_id = tf.random.categorical(predictions, num_samples=1)[-1,0].numpy()

    # We pass the predicted word as the next input to the model along with the previous hidden state
    input_eval = tf.expand_dims([predicted_id], 0)

    text_generated.append(idx2char[predicted_id])

  return (start_string + ''.join(text_generated))

def generate_caption(model, char2idx, idx2char, temperature = 1):
  """
  Generating a caption from a model
  """

  # words = []

  # # Loads all words from captions
  # with open("./Captions/Captions.txt", "r", encoding="utf8") as captions:
  #   for line in captions:
  #     words += line.split(sep=" ")
  
  # Generates text
  Generated_string = generate_text(model, start_string="§", char2idx = char2idx, idx2char = idx2char, temperature = temperature)

  print(Generated_string)

  Captions = Generated_string.split(sep="§")[1:-1] #Separate all different captions generated (first and last are not counted)

  return choice(Captions)

def import_mapping(file_dir):
  """
  Import mapping from a file
  """

  text = open(file_dir, 'rb').read().decode(encoding='utf-8') #Reads file and decodes it

  vocab = sorted(set(text))
  print ('{} unique characters'.format(len(vocab)))

  vocab_size = len(vocab)
  char2idx, idx2char = mapping(vocab)
  return vocab_size, char2idx, idx2char

if __name__ == "__main__":
  vocab_size, char2idx, idx2char = import_mapping('./Captions/vocab.txt')

  model = tf.keras.models.load_model('./Captions/CaptionRNN_v1.h5')

  print(generate_caption(model, char2idx = char2idx, idx2char = idx2char, temperature = 1.25))