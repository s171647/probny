# -*- coding: utf-8 -*-
"""isd_cnn_mnist.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1xSXSxohnTkjusE8cKVq0EWUAxV2CMM_5
"""

# Deep Nets library
import tensorflow
from tensorflow.keras import backend as K
from tensorflow.keras.datasets import mnist  # MNIST dataset

import numpy as np
import matplotlib.pyplot as plt  # VISUALISATION
import sys
import random

# CONSTANTS
displaySize = 4
num_classes = 10
img_rows, img_cols = 28, 28
RANDOM_SEED = 2

# NEURAL NETWORK DEFINITION
from tensorflow.keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPooling2D
from tensorflow.keras.models import Sequential

feature_vector_size = 16  # TODO, adjust those number (cw. 3)
number_of_filters = 16


def get_net(input_shape, num_classes):
    model = Sequential()
    model.add(Conv2D(number_of_filters, kernel_size=(3, 3),
                     activation='relu',
                     input_shape=input_shape))
    model.add(Conv2D(2 * number_of_filters, (3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Flatten())
    model.add(Dense(feature_vector_size, activation='relu'))
    model.add(Dropout(0.25))
    model.add(Dense(num_classes, activation='softmax'))
    return model


def visualisation(x_train, y_train):
    fig = plt.figure()
    for i in range(displaySize * displaySize):
        plt.subplot(displaySize, displaySize, i + 1)
        plt.tight_layout()
        plt.imshow(x_train[i], cmap='gray', interpolation='none')
        plt.title("Digit: {}".format(y_train[i]))
        plt.xticks([])
        plt.yticks([])
    plt.show()


def plot_training_history(history):
    fig = plt.figure()
    print(type(history.history))
    print(history.history.keys())
    plt.subplot(2, 1, 1)
    plt.plot(history.history['accuracy'])
    plt.plot(history.history['val_accuracy'])
    plt.title('model accuracy')
    plt.ylabel('accuracy')
    plt.xlabel('epoch')
    plt.legend(['train', 'val'], loc='lower right')

    plt.subplot(2, 1, 2)
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('model loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['train', 'val'], loc='upper right')

    plt.tight_layout()

    plt.show()


def preprocess_data(x_train, x_test):  # DATA PREPROCESSING
    if K.image_data_format() == 'channels_first':
        x_train = x_train.reshape(x_train.shape[0], 1, img_rows, img_cols)
        x_test = x_test.reshape(x_test.shape[0], 1, img_rows, img_cols)
        input_shape = (1, img_rows, img_cols)
    else:
        x_train = x_train.reshape(x_train.shape[0], img_rows, img_cols, 1)
        x_test = x_test.reshape(x_test.shape[0], img_rows, img_cols, 1)
        input_shape = (img_rows, img_cols, 1)
    x_train = x_train.astype('float32')
    x_train /= 255.
    x_test = x_test.astype('float32')
    x_test /= 255.
    return x_train, x_test, input_shape  #


def test_model(model_name):  # TEST MODEL
    (x_train, y_train), (x_testOrig, y_testOrig) = mnist.load_data()

    model = tensorflow.keras.models.load_model(model_name)

    x_train, x_test, _ = preprocess_data(x_train, x_testOrig)
    y_test = tensorflow.keras.utils.to_categorical(y_testOrig, num_classes)

    score = model.evaluate(x_test, y_test, verbose=0)
    print('Test accuracy:', score[1])


def visualise_examples(model_name):
    (x_train, y_train), (x_test, y_test) = mnist.load_data()
    x_test_vis = np.copy(x_test)  # for visualisation purposes
    x_train, x_test, _ = preprocess_data(x_train, x_test)
    model = tensorflow.keras.models.load_model(model_name)

    # ids and labels of examples to visualise
    ids = []
    labels = []
    for example_id, (x, y) in enumerate(zip(x_test, y_test)):
        x = np.expand_dims(x, 0)
        prediction = model.predict(x)  # run network prediction
        predicted_class = np.argmax(prediction)  # class predicted by the network
        gt_class = y  # correct class
        if predicted_class == gt_class:
            continue
        ids.append(example_id)  # save the id of the example
        labels.append(predicted_class)  # save the predicted label
        if len(labels) == (displaySize * displaySize):  # if enough number of examples is saved
            break
    imgs = x_test_vis[ids]  # get images of wrongly classified images
    visualisation(imgs, labels)  # display examples


from tensorflow.keras.preprocessing.image import ImageDataGenerator

# TRAINING VARIABLES
batch_size = 128  # Can be modified
epochs = 12
VALIDATION_SIZE = 0.2  # should be between 0.05 and 0.3
FRACTION_OF_DATA = 1.


def train(model_name):
    random.seed(RANDOM_SEED)
    assert (VALIDATION_SIZE <= 0.3 and VALIDATION_SIZE >= 0.05)

    # the data, split between train and test sets
    (x_train, y_train), (x_test, y_test) = mnist.load_data()
    if FRACTION_OF_DATA < 1.0:
        train_examples = x_train.shape[0]
        print("Using only {}% of training data".format(100. * FRACTION_OF_DATA))
        val_count = int(FRACTION_OF_DATA * train_examples)
        x_train = x_train[0:val_count]
        y_train = y_train[0:val_count]
    # if RANDOM_TRAINING: Randomly shuffle examples
    #    random.shuffle(y_train
    x_train, x_test, input_shape = preprocess_data(x_train, x_test)
    indices = np.arange(x_train.shape[0])
    random.shuffle(indices)  # random shuffle of training samples

    train_examples = x_train.shape[0]
    val_count = int(VALIDATION_SIZE * train_examples)
    val_indices = indices[0:val_count]
    train_indices = indices[val_count:]
    x_val = x_train[val_indices]
    y_val = y_train[val_indices]
    x_train = x_train[train_indices]
    y_train = y_train[train_indices]

    print(x_train.shape[0], 'train samples')
    print(x_test.shape[0], 'test samples')

    # convert class vectors to binary class matrices
    y_train = tensorflow.keras.utils.to_categorical(y_train, num_classes)
    y_val = tensorflow.keras.utils.to_categorical(y_val, num_classes)
    y_test = tensorflow.keras.utils.to_categorical(y_test, num_classes)

    learning_rate = 0.01
    model = get_net(input_shape, num_classes)
    model.compile(loss=tensorflow.keras.losses.categorical_crossentropy,  # LOSS FUNCTION
                  optimizer=tensorflow.keras.optimizers.Adam(learning_rate=0.001, beta_1=0.9,beta_2=0.999, amsgrad=False),  # change optimizer and or learning rate
                  metrics=['accuracy'])
    model.summary()

    batches_per_epoch = len(x_train) // batch_size
    datagen = ImageDataGenerator(
        featurewise_center=False,  # set input mean to 0 over the dataset
        samplewise_center=False,  # set each sample mean to 0
        featurewise_std_normalization=False,  # divide inputs by std of dataset
        samplewise_std_normalization=False,  # divide each input by its std
        zca_whitening=False,  # apply ZCA whitening
        rotation_range=0,  # TODO: randomly rotate images in the range (degrees, 0 to 180)
        zoom_range=0.,  # TODO: Randomly zoom image
        width_shift_range=0.,  # randomly shift images horizontally (fraction of total width)
        height_shift_range=0.,  # randomly shift images vertically (fraction of total height)
        horizontal_flip=False)  # randomly flip images)

    datagen.fit(x_train)
    history = model.fit_generator(datagen.flow(x_train, y_train, batch_size),
                                  validation_data=(x_val, y_val),
                                  steps_per_epoch=batches_per_epoch,
                                  epochs=epochs)

    plot_training_history(history)
    model.save(model_name)
    print("Training Done. Saving model as {}".format(model_name))
    print(model.summary())


model_name = "model_1"  # here define model name. Use different names for exercises 1,2, etc.#
train(model_name)
visualise_examples(model_name)

