# -*- coding: utf-8 -*-
"""Define a class to use cnn to predict the stock index."""
from functools import reduce

import tensorflow as tf

from KBPA_StockPrediction.model.basisModel import BasicModel
import settings.parameters as para


class CNN(BasicModel):
    """use the convolution neural network for time series prediction."""

    def __init__(self):
        """init."""
        super(CNN, self).__init__()
        # define
        self.num_steps = 1
        self.define_placeholder(
            shape_x=[None, para.SIZE_WORDVEC, para.NUM_WORDS],
            # shape_x=[None, self.num_steps, para.NUM_INPUT],
            shape_y=[None, para.NUM_OUTPUT])
        self.define_parameters_totrack()

    def inference(self):
        """use the cnn to output the result."""
        # expand the dimension
        expanded_input = tf.expand_dims(self.input_x, -1)
        # expanded_input = tf.expand_dims(expanded_input, -1)
        # expanded_input = self.input_x

        # create a CONV + RELU + POOL for each filter size
        pooled_outputs = []
        filters = zip(para.FILTER_SIZES, para.NUM_FILTERS)
        for i, (filter_size, num_filters) in enumerate(filters):
            with tf.name_scope("conv-relu-maxpool-%s" % filter_size):
                W = self.weight_variable(
                    shape=[filter_size, 1, 1, num_filters])
                b = self.bias_variable(
                    shape=[num_filters])
                conv = self.conv2d(
                    expanded_input,
                    W,
                    strides=[1, 1, 1, 1],
                    padding="VALID")
                h = self.relu(conv, b)
                pooled = self.max_pool(
                    h,
                    # ksize=[1, para.CONTINUOUS_WINDOW-filter_size+1, 1, 1],
                    ksize=[1, para.CONTINUOUS_WINDOW - filter_size + 1, para.NUM_WORDS, 1],
                    strides=[1, 1, 1, 1],
                    padding="VALID"
                    )
                pooled_outputs.append(pooled)

        num_filters_total = reduce(lambda a, b: a + b, para.NUM_FILTERS)
        self.h_pool = tf.concat(pooled_outputs, 3)
        self.h_pool_flat = tf.reshape(self.h_pool, [-1, num_filters_total])
        # self.h_pool_flat = tf.reshape(self.h_pool, [para.BATCH_SIZE, num_filters_total])
        # # fully_connect dense层
        # self.dense1 = tf.layers.dense(self.h_pool_flat, para.NUM_OUTPUT, activation=tf.nn.relu)
        # # # 也可以对全连接层的参数进行正则化约束：
        # # dense1 = tf.layers.dense(inputs=pool3, units=1024,
        # #                          activation=tf.nn.relu, kernel_regularizer = tf.contrib.layers.l2_regularizer(0.003))

        # add dropout
        with tf.name_scope("dropout"):
            self.h_drop = tf.nn.dropout(
                self.h_pool_flat, self.dropout_keep_prob)
        # with tf.name_scope("dropout"):
        #     self.h_drop = tf.nn.dropout(
        #         self.dense1, self.dropout_keep_prob)

        # Final (unnormalized) scores and predictions
        with tf.name_scope("output"):
            W = tf.get_variable(
                "W",
                shape=[num_filters_total, para.NUM_OUTPUT],
                initializer=tf.contrib.layers.xavier_initializer())
            # W = self.weight_variable(
            #     [num_filters_total, para.NUM_OUTPUT])
            b = self.bias_variable([para.NUM_OUTPUT])
            self.l2_loss += tf.nn.l2_loss(W)
            self.l2_loss += tf.nn.l2_loss(b)
            self.scores = tf.nn.xw_plus_b(
                self.h_drop,
                W,
                b,
                name="scores")
            # self.scores = tf.transpose(tf.nn.xw_plus_b(
            #     self.h_drop,
            #     W,
            #     b,
            #     name="scores"))
