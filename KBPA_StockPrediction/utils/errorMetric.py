# -*- coding: utf-8 -*-
"""some helper functions."""
from functools import reduce
from os.path import join
import numpy as np


def compute_rmse(y, pred):
    """compute the rmse."""
    mse = np.mean((y - pred) ** 2, axis=0)
    rmse = np.array(mse).tolist()
    return np.sqrt(rmse)

def compute_mae(y, pred):
    """compute the mae."""
    mae_a = np.mean(abs(y - pred), axis=0)
    mae = np.array(mae_a).tolist()
    return mae

def compute_mape(y, pred):
    """compute the mape."""
    mape_a = np.mean(abs(y - pred) / abs(y), axis=0)
    mape = np.array(mape_a).tolist()
    return mape

def avg(y):
    # avg = 0
    if len(y) != 0:
        avg = sum(y) / len(y)
    return avg

def compute_loss(y_pred, mapping, save_to_path):
    """compute the loss."""
    y, pred = y_pred
    rmse_norm = compute_rmse(y, pred)
    # pred = pred * (
    #     mapping["max_labels"] - mapping["min_labels"]) + mapping["min_labels"]
    # y = y * (
    #     mapping["max_labels"] - mapping["min_labels"]) + mapping["min_labels"]

    pred = pred * (
            avg(np.subtract(mapping["max_labels"], mapping["min_labels"]))) + avg(mapping["min_labels"])
    y = y * (
        avg(np.subtract(mapping["max_labels"], mapping["min_labels"]))) + avg(mapping["min_labels"])

    np.savetxt(join(save_to_path, "y_test.txt"), y)
    np.savetxt(join(save_to_path, "y_pred.txt"), pred)
    rmse_unnorm = compute_rmse(y, pred)
    mae_norm, mae_unnorm, mape_unnorm = compute_error(y_pred, mapping)
    error = np.array([np.mean(rmse_norm), np.mean(rmse_unnorm),
                      np.mean(mae_norm), np.mean(mae_unnorm),
                      np.mean(mape_unnorm)])
    np.savetxt(join(save_to_path, "error_metric.txt"), error)
    return rmse_norm, rmse_unnorm

def compute_error(y_pred, mapping):
    """compute the mae & mape."""
    y, pred = y_pred
    mae_norm = compute_mae(y, pred)
    # mape_norm = compute_mape(y, pred)

    # pred = pred * (
    #     mapping["max_labels"] - mapping["min_labels"]) + mapping["min_labels"]
    # y = y * (
    #     mapping["max_labels"] - mapping["min_labels"]) + mapping["min_labels"]

    pred = pred * (
            avg(np.subtract(mapping["max_labels"], mapping["min_labels"]))) + avg(mapping["min_labels"])
    y = y * (
        avg(np.subtract(mapping["max_labels"], mapping["min_labels"]))) + avg(mapping["min_labels"])

    mae_unnorm = compute_mae(y, pred)
    mape_unnorm = compute_mape(y, pred)
    return mae_norm, mae_unnorm, mape_unnorm

def format_data(y_pred):
    """reshape a list of scores to a vector."""
    return reduce(
        lambda a, b: (
            np.vstack((a[0], b[0])),
            np.vstack((a[1], b[1]))),
        y_pred)
