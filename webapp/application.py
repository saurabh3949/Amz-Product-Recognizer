from flask import Flask
from flask import render_template,request, Response, redirect
from StringIO import StringIO
from requests.exceptions import ConnectionError
import os, random, string
import time
import requests
from PIL import Image
import sklearn
import numpy as np
import lasagne
import skimage.transform
from scipy.misc import imread
from lasagne.utils import floatX
import theano
import theano.tensor as T
import matplotlib.pyplot as plt
import json
import pickle
import cPickle
import googlenet

app = Flask(__name__)

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

cnn_layers = googlenet.build_model()
cnn_input_var = cnn_layers['input'].input_var
cnn_feature_layer = cnn_layers['loss3/classifier']
cnn_output_layer = cnn_layers['prob']

get_cnn_features = theano.function([cnn_input_var], lasagne.layers.get_output(cnn_feature_layer))

model_param_values = pickle.load(open('blvc_googlenet.pkl'))['param values']
lasagne.layers.set_all_param_values(cnn_output_layer, model_param_values)
CLASSES = pickle.load(open('blvc_googlenet.pkl'))['synset words']

MEAN_VALUES = np.array([104, 117, 123]).reshape((3,1,1))

def prep_image(im):
    if len(im.shape) == 2:
        im = im[:, :, np.newaxis]
        im = np.repeat(im, 3, axis=2)
    # Resize so smallest dim = 224, preserving aspect ratio
    h, w, _ = im.shape
    if h < w:
        im = skimage.transform.resize(im, (224, w*224/h), preserve_range=True)
    else:
        im = skimage.transform.resize(im, (h*224/w, 224), preserve_range=True)

    # Central crop to 224x224
    h, w, _ = im.shape
    im = im[h//2-112:h//2+112, w//2-112:w//2+112]

    rawim = np.copy(im).astype('uint8')

    # Shuffle axes to c01
    im = np.swapaxes(np.swapaxes(im, 1, 2), 0, 1)

    # Convert to BGR
    im = im[::-1, :, :]

    im = im - MEAN_VALUES
    return rawim, floatX(im[np.newaxis])


get_pred = cPickle.load(open('prediction_model.pkl','rb'))

label_to_class = cPickle.load(open('class_dict.pkl','rb'))



print "Compiled all"


def downloadImages(urls, path):
    if not os.path.exists(path):
        os.makedirs(path)
    for url in urls:
        try:
            image_r = requests.get(url)
            print "Downloaded %s" % url
        except ConnectionError, e:
            print 'could not download %s' % url
            continue
        file = open(os.path.join(path, '%s') % url[-12:].replace("/",""), 'w')
        try:
            img = Image.open(StringIO(image_r.content))
            Image.open(StringIO(image_r.content)).save(file, 'JPEG')
            imread(file.name)
        except IOError, e:
            os.remove(file.name)
            continue
        finally:
            file.close()
    return file.name

@app.route('/')
def hello():
    return render_template('home.html')


@app.route('/geturl', methods=['POST'])
def processImage():
    # url = request.args.get('url', '')
    url = request.form['url']
    url = url.replace("52.9.19.39","localhost")
    path = id_generator()
    path = "data/" + path
    im_path = downloadImages([url], path)
    im = plt.imread(im_path)
    rawim, cnn_im = prep_image(im)
    p = get_cnn_features(cnn_im)
    p = get_pred(p)
    idx = (-p.flatten()).argsort()[:5]
    objects = [label_to_class[i].capitalize() for i in idx]
    # x_cnn = get_cnn_features(cnn_im)
    return json.dumps(objects)
    
if __name__ == '__main__':
    app.debug = False
    app.run(host='0.0.0.0', port = 8002)
