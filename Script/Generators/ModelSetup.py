import os.path
import os
import tensorflow as tf
import numpy as np

from sklearn.utils import shuffle
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam


class Network:

    def __init__(self, network_model):
        self.network_model = network_model

    def create_model(self, x_train, y_train, model_path):
        # unique_labels detects the output length
        unique_labels = len(set(np.array(y_train)))
        print(" *** unique_labels: " + str(unique_labels))

        #Dense(units=16, activation='relu'),

        callback = tf.keras.callbacks.EarlyStopping(monitor='loss', patience=4)
        network_model = Sequential([
            Dense(units=32, input_shape=(np.array(x_train).shape[1],), activation='relu'),
            Dense(units=16, activation='relu'),
            Dense(units=unique_labels, activation='softmax')
        ])
        network_model.summary()

        network_model.compile(optimizer=Adam(learning_rate=0.0001),
                              loss='sparse_categorical_crossentropy',
                              metrics=['accuracy'])

        network_model.fit(x=np.array(x_train), y=np.array(y_train),
                          validation_split=0.2,
                          batch_size=16,
                          callbacks=[callback],
                          epochs=2000,
                          shuffle=True)

        network_model.save(model_path)

    def manage_model(self, x_train, y_train, path):
        model_path = path
        # print(" *** model_path: " + str(model_path))
        if os.path.isfile(model_path) is False:
            print(" *** CREATING MODEL...")
            shuffle(x_train, y_train)
            # print(" *** total samples: " + str(len(x_train)))
            self.create_model(x_train, y_train, model_path)
        else:
            print(" *** MODEL EXISTS...")

        model = tf.keras.models.load_model(model_path)
        return model

    def load_model(self, path):
        return tf.keras.models.load_model(path)
