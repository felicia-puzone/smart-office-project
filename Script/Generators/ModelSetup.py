from tensorflow.keras.models import load_model


class Network:

    def __init__(self, network_model):
        self.network_model = network_model

    def load_model(self, path):
        return load_model(path)
