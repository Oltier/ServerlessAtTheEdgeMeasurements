import mxnet as mx
import cv2
import numpy as np
from collections import namedtuple
Batch = namedtuple('Batch', ['data'])


class Model(object):

    def __init__(self, synset_path, network_prefix):

        with open(synset_path, 'r') as file:
            self.synsets = [line.rstrip() for line in file]

        symbol, arg_params, aux_params = mx.model.load_checkpoint(network_prefix, 0)

        self.module = mx.mod.Module(symbol, label_names=['prob_label'], context=mx.cpu())
        self.module.bind([('data', (1, 3, 224, 224))], for_training=False)
        self.module.set_params(arg_params, aux_params)

    def predict_from_image(self, image):
        reshape = (224, 224)

        img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        if img is None:
            return 'unkown'

        img = cv2.resize(img, reshape)
        img = np.swapaxes(img, 0, 2)
        img = np.swapaxes(img, 1, 2)
        img = img[np.newaxis, :]

        self.module.forward(Batch([mx.nd.array(img)]))
        prob = self.module.get_outputs()[0].asnumpy()
        prob = np.squeeze(prob)

        a = np.argsort(prob)[::-1]
        return prob[0], self.synsets[0]

