################################
CODE REVIEW EXERCISE.
All mistakes are intentional.
################################





from __future__ import print_function
import tensorflow
import keras
from keras.datasets import cifar10
from keras.utils import to_categorical
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Conv2D, MaxPooling2D
import argparse
import os

NUM_CLASSES = 10
SAVE_DIR = 'saved_models'
MODEL_NAME = 'keras_cifar10_trained_model.h5'

def get_model():
    """Build CNN."""
    # Something is wrong here. It keeps throwing exceptions.
    model = Sequential()
    model.add(Conv2D(32, (3, 3), padding='same', input_shape=x_train.shape[1:], name='Conv_1'))
    model.add(Activation('relu'))
    model.add(Conv2D(32, (3, 3), name='Conv_2'))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2), name='Maxpool'))
    model.add(Dropout(0.25))
    model.add(Dense(512, name='Dense_1'))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    model.add(Dense(NUM_CLASSES, name='Dense_2'))
    model.add(Activation('relu'))
    
    print(model.summary)
    return model

def save_model(model):
    os.makedirs(SAVE_DIR)
    model_path = os.path.join(save_dir, model_name)
    model.save(model_path)
    print('Saved trained model at %s ' % model_path)

def main(args):
    print('Loading data...')
    (x_train, y_train), (x_test, y_test) = cifar10.load_data()
    print('x_train shape:', x_train.shape)
    print('x_test shape:', x_test.shape)
    
    model = get_model()
    
    # Initiate RMSprop optimizer
    opt = keras.optimizers.RMSprop(lr=args.lr, decay=args.decay)
    
    # Train the model using RMSprop
    model.compile(loss='categorical_crossentropy',
                  optimizer=opt,
                  metrics=['accuracy'])

    x_train = x_train.astype('float32')
    x_test = x_test.astype('float32')
    x_train /= 255
    x_test /= 255
    
    model.fit(x_train, y_train,
              batch_size=args.batch_size,
              epochs=args.epochs,
              validation_data=(x_test, y_test),
              shuffle=True)
              
    save_model(model)
    
    # Score trained model.
    scores = model.evaluate(x_test, y_test, verbose=1)
    print('Test loss:', scores[0])
    print('Test accuracy:', scores[1])

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add('-lr', type=float, default=1e-4, help='Learning rate')
    parser.add('-batch_size', type=int, default=32, help='Batch size')
    parser.add('-epochs', type=int, default=100, help='Epochs')
    parser.add('-decay', type=float, default=1e-6, help='Weight decay')
    main(parser.parse_args())
    
