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

        self.module = mx.mod.Module(symbol=symbol, label_names=['prob_label'], context=mx.cpu())
        self.module.bind(data_shapes=[('data', (1, 3, 224, 224))], for_training=False)
        self.module.set_params(arg_params, aux_params)

    def predict_from_image(self, img_str):
        reshape = (224, 224)

        nparr = np.frombuffer(img_str, np.uint8)
        image = cv2.imdecode(nparr, cv2.CV_LOAD_IMAGE_COLOR)

        N = 5
        topN = []

        # Switch RGB to BGR format (which ImageNet networks take)
        img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        if img is None:
            return topN

        # Resize image to fit network input
        img = cv2.resize(img, reshape)
        img = np.swapaxes(img, 0, 2)
        img = np.swapaxes(img, 1, 2)
        img = img[np.newaxis, :]

        # Run forward on the image
        self.module.forward(Batch([mx.nd.array(img)]))
        prob = self.module.get_outputs()[0].asnumpy()
        prob = np.squeeze(prob)

        # Extract the top N predictions from the softmax output
        a = np.argsort(prob)[::-1]
        for i in a[0:N]:
            topN.append((prob[i], self.synsets[i]))
        return topN

