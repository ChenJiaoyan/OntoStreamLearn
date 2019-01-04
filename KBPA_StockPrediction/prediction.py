# -*- coding: utf-8 -*-
"""use various model to do the prediction."""
import os
from os.path import join
import datetime

import numpy as np
import tensorflow as tf

import settings.parameters as para
import utils.formData as form_data
from utils.myprint import myprint
from utils.visualizeLabels import visualize_histogram

from model.cnn import CNN
from model.lstm import LSTM


def evaluate_data(train_labels, test_labels, mapping, out_path):
    """evaluate the dataset."""
    train_labels = train_labels * (
        mapping["max_labels"] - mapping["min_labels"]) + mapping["min_labels"]
    # print(test_labels.size)
    scope = train_labels[:, 0]
    min_scope = np.min(scope)
    max_scope = np.max(scope)
    length = train_labels[:, 1]
    min_length = np.min(length)
    max_length = np.max(length)
    myprint(
        "Train: max scope={}, min scope={}, max length={}, min length={}".
        format(max_scope, min_scope, max_length, min_length))
    visualize_histogram(train_labels, join(out_path, "histogram_train"))

    test_labels = test_labels * (
        mapping["max_labels"] - mapping["min_labels"]) + mapping["min_labels"]
    scope = test_labels[:, 0]
    min_scope = np.min(scope)
    max_scope = np.max(scope)
    length = test_labels[:, 1]
    min_length = np.min(length)
    max_length = np.max(length)
    myprint(
        "Test: max scope={}, min scope={}, max length={}, min length={}".
        format(max_scope, min_scope, max_length, min_length))
    visualize_histogram(test_labels, join(out_path, "histogram_test"))


def run(MODEL, data):
    """setup the model and train the model."""
    train_data, train_labels, \
        val_data, val_labels, \
        test_data, test_labels, mapping = form_data.normalize_data(data)


    with tf.Graph().as_default():
        session_conf = tf.ConfigProto(
            allow_soft_placement=para.ALLOW_SOFT_PLACEMENT,
            log_device_placement=para.LOG_DEVICE_PLACEMENT)
        sess = tf.Session(config=session_conf)

        with sess.as_default():
            # init model
            model = MODEL()
            # build the model.
            model.inference()
            model.loss()
            # Define Training procedure
            model.training(decay_steps=data["train_data"].shape[0])
            # Keep track of gradient values and sparsity (optional)
            model.keep_tracking(sess)
            # # Apply some statistics on the train and test labels.
            # evaluate_data(train_labels, test_labels, mapping, model.out_dir)
            # Initialize all variables
            sess.run(tf.initialize_all_variables())
            # run epochs
            best_tr_loss = float('inf')
            best_tr_epoch = 0
            best_val_loss = float('inf')
            best_val_epoch = 0

            for epoch in range(para.MAX_EPOCHS):
                myprint("Epoch {}\n" . format(epoch))

                tr_loss, tr_rmse_norm, tr_rmse_unnorm, tr_prediction, tr_mae_norm, tr_mae_unnorm, tr_mape_unnorm = model.run_epoch(
                    sess, model.train_step,
                    train_data, train_labels, mapping, train=True)
                myprint(
                    "train mae(unnorm, norm): {},\t{}\ntrain mape(unnorm, norm): {}".
                        format(np.mean(tr_mae_unnorm), np.mean(tr_mae_norm), np.mean(tr_mape_unnorm)))
                myprint(
                    "train rmse(unnorm, norm): {},\t{}".
                        format(np.mean(tr_rmse_unnorm), np.mean(tr_rmse_norm)))
                myprint(
                    "train loss: {}\n". format(tr_loss))

                val_loss, val_rmse_norm, val_rmse_unnorm, val_prediction, val_mae_norm, val_mae_unnorm, val_mape_unnorm, \
                    = model.run_epoch(sess, model.dev_step, val_data, val_labels, mapping)
                myprint(
                    "valid mae(unnorm, norm): {},\t{}\nvalid mape(unnorm): {}".
                        format(np.mean(val_mae_unnorm), np.mean(val_mae_norm), np.mean(val_mape_unnorm)))
                myprint(
                    "valid rmse(unnorm, norm): {},\t{}".
                        format(np.mean(val_rmse_unnorm), np.mean(val_rmse_norm)))
                myprint(
                    "valid loss: {}\n".format(val_loss))

                # if tr_loss < best_tr_loss:
                #     best_tr_loss = tr_loss
                #     best_tr_epoch = epoch
                #     myprint("save best model.\n")
                #     model.saver.save(sess, model.best_model)
                # if epoch - best_tr_epoch > para.EARLY_STOPPING:
                #     break

                if val_loss < best_val_loss:
                    best_val_loss = val_loss
                    best_val_epoch = epoch
                    myprint("save best model.\n")
                    model.saver.save(sess, model.best_model)
                if epoch - best_val_epoch > para.EARLY_STOPPING:
                    break

        myprint("\ntest...")
        myprint("restore from path {}".format(model.best_model))
        model.saver.restore(sess, model.best_model)
        te_loss, te_rmse_norm, te_rmse_unnorm, te_prediction, te_mae_norm, te_mae_unnorm, te_mape_unnorm = model.run_epoch(
            sess, model.predict_step, test_data, test_labels, mapping)
        myprint(
            "test mae(unnorm, norm): {},\t{}\ntest mape(unnorm): {}".
                format(np.mean(te_mae_unnorm), np.mean(te_mae_norm), np.mean(te_mape_unnorm)))
        myprint(
            "test rmse(unnorm, norm): {},\t{}".
                format(np.mean(te_rmse_unnorm), np.mean(te_rmse_norm)))
        myprint(
            "test loss: {}\n". format(te_loss))
        # # mv the record and parameter file to the information path
        # os.system(
        #     "mv {o} {d}".format(
        #         o=para.RECORD_DIRECTORY, d=model.out_dir))
        # os.system(
        #     "mv {o} {d}".format(
        #         o=para.PARAMETER_DIRECTORY, d=model.out_dir))

if __name__ == '__main__':
    dataset = "data_stocks.csv"
    model = LSTM

    data = form_data.init_data(dataset, model)
    start_time = datetime.datetime.now()
    run(model, data)
    exection_time = (datetime.datetime.now() - start_time).total_seconds()
    myprint("execution time: {t:.3f} seconds" . format(t=exection_time))

