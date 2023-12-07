import tensorflow as tf
import numpy as np
import time
from datetime import datetime

from tensorflow import keras
from keras import Model, layers

import object_recognition.object_position as obj_pos

from base import network, message
from base.message import FilteredObjects, ImageLink, X, Y, DEPTH, DIAMETER
from object_recognition.model_class import InferenceModel

import copy
import sys
import os
from pathlib import Path

# ------------------------------------------ # 
# Describe architecture of neural network    #
# ------------------------------------------ #

KERN_INIT   = 'he_uniform' #'glorot_uniform' #'ones' #'zeros'
def Gen_Conv2D_Block(inp_layer, filters = 50, dilation = 1):
    x = layers.Conv2D(filters = filters,
                    kernel_size = 5,
                    kernel_initializer = KERN_INIT,
                    dilation_rate = dilation,
                    padding = 'same')(inp_layer)
    
    x = layers.Activation("relu")(x)
    x = layers.BatchNormalization()(x)
    res = layers.Resizing(128,128, interpolation="bilinear")(x)
    x = layers.MaxPooling2D(padding = 'same')(x)
    return x, res

def Gen_Conv2D_Block_11(inp_layer, filters = 50, act_func = "relu"):
    x = layers.Conv2D(filters = filters,
                    kernel_size = 1,
                    kernel_initializer = KERN_INIT,
                    padding = 'same')(inp_layer)
    x = layers.BatchNormalization()(x)
    x = layers.Activation(act_func)(x)
    return x

def create_model():
    INPUT_SHAPE = (128, 128, 3)

    CONV_LAYERS = 8

    Input         = layers.Input(INPUT_SHAPE)

    Conv2D_Layers = []
    Res_Layers    = []

    # First Conv2D with connection to input

    conv, res = Gen_Conv2D_Block(Input)
    Conv2D_Layers.append(conv)
    Res_Layers.append(res)

    for i in range(1, CONV_LAYERS):
        conv, res = Gen_Conv2D_Block(Conv2D_Layers[len(Conv2D_Layers) - 1])
        Conv2D_Layers.append(conv)
        Res_Layers.append(res)

    Merge_Layer     = layers.Concatenate()(Res_Layers)
    Conv2D_11_Layer = Gen_Conv2D_Block_11(Merge_Layer, filters = 96)
    Conv2D_11_Layer = Gen_Conv2D_Block_11(Conv2D_11_Layer, filters = 48)
    Conv2D_11_Layer = Gen_Conv2D_Block_11(Conv2D_11_Layer, filters = 24)
    Conv2D_11_Layer = Gen_Conv2D_Block_11(Conv2D_11_Layer, filters = 12)
    Conv2D_11_Layer = Gen_Conv2D_Block_11(Conv2D_11_Layer, filters = 2, act_func = "softmax")

    model = keras.Model(Input, Conv2D_11_Layer)

    model.compile(optimizer='adam',
                loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False),
                metrics=["accuracy"])
    
    return model

# --------------------- #
# Main code             #
# --------------------- #

MAIN_OUT_FOLDER = os.environ['PYTHONPATH'] + "/debug/" #"/ssd/recognition_neural/"
#MAIN_OUT_FOLDER = "/media/ssd/recognition_neural"
NEURAL_MODELS   = "nn_models/"
FPS = 5.0



def Inference(model, image):
    nn_img = tf.image.resize(image/255.0, [128, 128], "nearest").numpy()
    nn_out = model.predict(nn_img[tf.newaxis, ...], verbose=0)

    #nn_out  = tf.cast(tf.argmax(nn_out, axis = -1), dtype=tf.float32)[0]
    #nn_out  = tf.reshape(nn_out, [128, 128, 1])

    #nn_out = tf.image.resize(nn_out, [256, 256], "nearest").numpy()[..., 0]  
    nn_out = tf.stack([nn_out[0, ..., 1], nn_out[0, ..., 1],  nn_out[0, ..., 1]], axis = 2)      
    #print(nn_out.max(), nn_out.min())  
    return nn_out   

def main(argv):
    datetime_now = datetime.now()
    datetime_now_str = datetime_now.strftime("%d-%m-%Y-%H-%M-%S")
    camera = argv[1]
    object = argv[2]

    save_folder = MAIN_OUT_FOLDER + f"/{camera}_{object}/{datetime_now_str}/"
    try:
        Path(save_folder).mkdir(parents=True, exist_ok=True)
    except FileExistsError:
        pass

    counter = 0
    missing_counter = 0

    net = network.Net(timer=1/FPS)
    model = create_model()

    model.load_weights(f"nn_models/{object}/{object}").expect_partial()
    print("Model loaded")    

    robot_pos = [0 for i in range(6)]
    
    local_img_link = None 

    while net.receive():
        if net.id == "Timer":
            if local_img_link != None:            
                file    = tf.io.read_file(local_img_link.path)
                image   = tf.cast(tf.image.decode_png(file, channels = 3), 'float32')

                file_name  = f"{counter:05}.png"

                
                tf_img = tf.cast(Inference(model, image)*255.0, tf.uint8)
                save_image = tf.image.encode_png(tf_img)
                tf.io.write_file(save_folder + file_name, save_image)

                net.send(ImageLink(
                    path=save_folder + file_name,
                    obj=f"NN_{object}",
                    file=file_name,
                    counter=counter
                ))

                counter += 1
                local_img_link = None
                missing_counter = 0
    

        elif net.id == "ImageLink":
            if net.msg.obj == camera:
                local_img_link = copy.deepcopy(net.msg)
                missing_counter += 1
                #DEBUG: Send grayscale output of neural network  
                #
                
                #DEBUG: Get argmax of channels
                #nn_out  = tf.cast(tf.argmax(nn_out, axis = -1), dtype=tf.float32)[0]
                #nn_out  = tf.reshape(nn_out, [128, 128, 1])

               
        elif net.id == "Coord":
            robot_pos = net.msg.pos

if __name__ == "__main__":
    main(sys.argv)
