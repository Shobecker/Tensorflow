# how to use a common layer and Lambda layer, and then initialize the state of GRU unit
from keras.layers import Dense, Input, Embedding, Dropout, GRU
from keras.models import Model
from keras.layers.core import Lambda
from keras.optimizers import RMSprop
from keras import metrics
from keras import backend as K
import tensorflow as tf

# configure option for GPU memory usage
from keras.backend.tensorflow_backend import set_session
config = tf.ConfigProto()
config.gpu_options.per_process_gpu_memory_fraction = 0.3
set_session(tf.Session(config=config))

import numpy as np
import random

feature_len = 2
units = 8
pre_len = 2
embedding_size = 3
feature_size = 4

x_feature = np.array([[1, 2], [3, 4]])
x_prelen = np.array([[2, 3], [4, 3]])
y = np.array([[1, 0, 0, 0], [0, 1, 0, 0]])

# the emmdedding layer is a common layer for 'scan_input' and 'feature_input'
embedding_layer = Embedding(output_dim=embedding_size,
                            input_dim=feature_size + 1,
                            input_length=pre_len)

data = Input(shape=(pre_len,), name='scan_input')
x = embedding_layer(data)

feature_input = Input(shape=(feature_len,), name='feature_input')
temp_out = embedding_layer(feature_input)

# use the Lambda layer of Keras, do not use the K.mean() directly, else error like 
# 'AttributeError: 'Tensor' object has no attribute '_keras_history''
mean_temp = Lambda(lambda x: K.mean(x, axis=1))(temp_out)
initial_state = Dense(units)(mean_temp)

# first dense to get units, then average the result
# feature_output = TimeDistributed(Dense(units))(temp_out)
# initial_state = Lambda(lambda x: K.mean(x, axis=1))(feature_output)

# for GRU unit, there is only one state
# lstm_output = GRU(units=units, return_sequences=False)(x, initial_state=initial_state)

# for LSTM unit, there are two states, one is hidden state and the other is cell state
lstm_output = LSTM(units=units, return_sequences=False)(x, initial_state=[initial_state, initial_state])

lstm_output = Dropout(0.1)(lstm_output)

output = Dense(feature_size, activation='softmax', name='scan_output')(lstm_output)

model = Model(inputs=[feature_input, data],
              outputs=[output])

optimizer = RMSprop(lr=1e-3, rho=0.9, epsilon=1e-6, decay=0)
model.compile(optimizer=optimizer,
              loss='categorical_crossentropy',
              metrics=[metrics.categorical_accuracy, metrics.top_k_categorical_accuracy])
print(model.summary())

model.fit(x=[x_feature, x_prelen], y=y, batch_size=1, epochs=2)
