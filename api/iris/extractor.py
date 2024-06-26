from keras.preprocessing import image
from keras.applications.inception_v3 import InceptionV3, preprocess_input
from keras.models import Model, load_model
from keras.layers import Input
import numpy as np

class Extractor():
    def __init__(self, weights=None):
        """Either load pretrained from imagenet, or load our saved
        weights from our own training."""

        self.weights = weights  # so we can check elsewhere which model

        if weights is None:
            # Get model with pretrained weights.
            base_model = InceptionV3(
                weights='imagenet',
                include_top=True
            )

            # We'll extract features at the final pool layer.
            self.model = Model(
                inputs=base_model.input,
                outputs=base_model.get_layer('avg_pool').output
            )

        else:
            # Load the model first.
            self.model = load_model(weights)

            # Then remove the top so we get features not predictions.
            # From: https://github.com/fchollet/keras/issues/2371
            self.model.layers.pop()
            self.model.layers.pop()  # two pops to get to pool layer
            self.model.outputs = [self.model.layers[-1].output]
            self.model.output_layers = [self.model.layers[-1]]
            self.model.layers[-1].outbound_nodes = []

    #Returns the extracted features of the frame
    #image_path, Default is None. If given, will extract the features from the the image from my image path
    #frame: The array representation of the image. example: ret, img = cap.read() (Using open CV it returns 'image' as the array)
    def extract(self, frame = None, image_path=None):
        img = None

        if image_path is not None:
            img = image.load_img(image_path, target_size=(299, 299))
           #img = image.img_to_array(img).astype('float32')/255 no need to this this because preprocess_input does it for inception 
        else:
            img = frame



        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)

        # Get the prediction.
        features = self.model.predict(x)

        if self.weights is None:
            # For imagenet/default network:
            features = features[0]
        else:
            # For loaded network:
            features = features[0]

        return features
