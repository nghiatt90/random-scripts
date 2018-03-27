
# coding: utf-8

# ## Try to learn the minimum function with keras

# In[1]:


import numpy as np
from keras.layers import Dense, Activation, BatchNormalization, Input
from keras.models import Model, Sequential
from keras.optimizers import SGD, Adam
import matplotlib.pyplot as plt
get_ipython().magic('matplotlib inline')


# In[2]:


def create_dataset(m = 10000, max_X = 10000):
    """
    m: number of data entries
    max_X: data is constrained in [-max_X, max_X)
    """
    x = np.random.randint(-max_X, max_X, (m, 2))
    y = np.argmin(x, axis=1)
    y = np.eye(2)[y]  # One hot encoding
    return x, y


# In[3]:


X_train, Y_train = create_dataset()
X_val, Y_val = create_dataset(1000)


# In[4]:


def create_model():
    X_input = Input(batch_shape=(None, 2))
    
    X = Dense(3)(X_input)
    X = BatchNormalization()(X)
    X = Activation('tanh')(X)
    
    X = Dense(3)(X)
    X = BatchNormalization()(X)
    X = Activation('tanh')(X)
    
    X = Dense(2)(X)
    X = Activation('sigmoid')(X)
    
    model = Model(inputs=X_input, outputs=X)
    return model


# In[5]:


model = create_model()
optimizer = Adam(lr=0.03, beta_1=0.9, beta_2=0.999)
model.compile(optimizer=optimizer, loss='binary_crossentropy', metrics=['accuracy'])


# In[6]:


model.fit(X_train, Y_train, epochs=100, batch_size=10000)


# In[7]:


plt.plot(model.history.history['loss'])


# In[8]:


loss, accuracy = model.evaluate(X_val, Y_val)
print(f'Loss = {loss}, accuracy = {accuracy}')


# In[9]:


# Check if the model generalizes well with bigger numbers
X_test, _ = create_dataset(10, 10000000)
for inp in X_test:
    print(inp, inp[np.argmax(model.predict(np.expand_dims(inp, axis=0)))])

