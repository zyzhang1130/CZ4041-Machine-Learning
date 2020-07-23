# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 19:47:36 2020

@author: Lenovo
"""


from tensorflow.keras.datasets import mnist
from tensorflow.keras.layers import Input, Dense, Conv2D, MaxPooling2D, UpSampling2D
from tensorflow.keras.models import Model
import tensorflow.keras as k

import numpy as np
import matplotlib.pyplot as plt
from keras.utils import multi_gpu_model
from keras.models import load_model




(x_train, _), (x_test, _) = mnist.load_data()

x_train = x_train.astype('float32') / 255.
x_test = x_test.astype('float32') / 255.
x_train = np.reshape(x_train, (len(x_train), 28, 28, 1))
x_test = np.reshape(x_test, (len(x_test), 28, 28, 1))



#adding some noise
noise_factor = 0.5
x=x_train[1]
x=np.reshape(x, (1, 28, 28, 1))
x_noisy=x + noise_factor * np.random.normal(loc=0.0, scale=1.0, size=x.shape) 
for i in range(999):
    a = x + noise_factor * np.random.normal(loc=0.0, scale=1.0, size=x.shape) 
    # x_noisy=np.stack((x_noisy, a), axis=0)
    x_noisy=np.concatenate((x_noisy, a), axis=0)


x_noisy = np.clip(x_noisy, 0., 1.)
xx=x_noisy
    
    
x=x_train[0]
x=np.reshape(x, (1, 28, 28, 1))
x_noisy=x + noise_factor * np.random.normal(loc=0.0, scale=1.0, size=x.shape) 
for i in range(999):
    a = x + noise_factor * np.random.normal(loc=0.0, scale=1.0, size=x.shape) 
    # x_noisy=np.stack((x_noisy, a), axis=0)
    x_noisy=np.concatenate((x_noisy, a), axis=0)

x_noisy = np.clip(x_noisy, 0., 1.)


x_train_noisy=np.concatenate((x_noisy[0:800], xx[0:800]), axis=0)
x_test_noisy=np.concatenate((x_noisy[800:-1], xx[800:-1]), axis=0)




# x_train_noisy=x_noisy[0:1600]
# x_test_noisy=x_noisy[1600:-1]



# col_idx = np.random.permutation(x_train_noisy.shape[0])
# shuffled_x = x_train_noisy[col_idx,:,:,:]
# col_idy = np.random.permutation(x_test_noisy.shape[0])
# shuffled_y = x_test_noisy[col_idy,:,:,:]

#isplaying images with noise
plt.figure(figsize=(20, 2))
for i in range(1,10):
    ax = plt.subplot(1, 10, i)
    plt.imshow(x_test_noisy[i].reshape(28, 28), cmap="binary")
plt.show()

model = k.models.Sequential()

model.add(Conv2D(32, (3,3), activation='relu', padding='same', input_shape=(28,28,1)))
model.add(MaxPooling2D((2,2), padding='same'))
model.add(Conv2D(64, (3,3), activation='relu', padding='same'))
model.add(MaxPooling2D((2,2), padding='same'))
          
model.add(Conv2D(64, (3,3), activation='relu', padding='same'))
model.add(UpSampling2D((2,2)))
model.add(Conv2D(32, (3,3), activation='relu', padding='same'))
model.add(UpSampling2D((2,2)))
model.add(Conv2D(1,(3,3), activation='sigmoid', padding='same'))


# model = multi_gpu_model(model, gpus=4)
model.compile(optimizer='adadelta',
             loss='binary_crossentropy')
model.summary()

for i in range(10):
    aa=x_train_noisy[0:800]
    bb=x_train_noisy[800:]
    col_idaa = np.random.permutation(aa.shape[0])
    aa = aa[col_idaa,:,:,:]
    col_idbb = np.random.permutation(bb.shape[0])
    bb = bb[col_idbb,:,:,:]

    shuffled_x=np.concatenate((aa, bb), axis=0)
    
    
    model.fit(x_train_noisy, shuffled_x,
            epochs=2,
            shuffle=True)
    # col_idx = np.random.permutation(x_train_noisy.shape[0])
    # shuffled_x = x_train_noisy[col_idx,:,:,:]
    # col_idy = np.random.permutation(x_test_noisy.shape[0])
    # shuffled_y = x_test_noisy[col_idy,:,:,:]
    

    # model.evaluate(x_test_noisy,  shuffled_y)
    
    model.save('denoising_autoencoder4.h5')
    
no_noise_img = model.predict(x_test_noisy)
    
plt.figure(figsize=(40, 4))
for i in range(10):
    # display original
    ax = plt.subplot(3, 20, i + 1)
    plt.imshow(x_test_noisy[i].reshape(28, 28), cmap="binary")
    
    # display reconstructed (after noise removed) image
    ax = plt.subplot(3, 20, 40 +i+ 1)
    plt.imshow(no_noise_img[i].reshape(28, 28), cmap="binary")

plt.show()