## -*- coding: utf-8 -*-

import logging

log = logging.getLogger(__name__)

import sklearn.metrics

def mean_squared_error(y_true, y_pred, test_idx=None):
    if test_idx == None:
    	score = sklearn.metrics.mean_squared_error(y_true, y_pred)
    else:
    	score = sklearn.metrics.mean_squared_error(y_true[:test_idx], y_pred[:test_idx])

    return score

def mean_absolute_error(y_true, y_pred, test_idx=None):
    if test_idx == None:
        score = sklearn.metrics.mean_absolute_error(y_true, y_pred)
    else:
        score = sklearn.metrics.mean_absolute_error(y_true[:test_idx], y_pred[:test_idx])

    return score

def roc_auc_score(y_true, y_pred, test_idx=None):
    if test_idx == None:
    	score = sklearn.metrics.roc_auc_score(y_true, y_pred)
    else:
    	score = sklearn.metrics.roc_auc_score(y_true[:test_idx], y_pred[:test_idx])

    return score

def accuracy_score(y_true, y_pred, test_idx=None):
    if test_idx == None:
    	score = sklearn.metrics.accuracy_score(y_true, y_pred)
    else:
    	score = sklearn.metrics.accuracy_score(y_true[:test_idx], y_pred[:test_idx])

    return score

def recall_score(y_true, y_pred, test_idx=None):
    if test_idx == None:
    	score = sklearn.metrics.recall_score(y_true, y_pred, average='macro')
    else:
    	score = sklearn.metrics.recall_score(y_true[:test_idx], y_pred[:test_idx], average='macro')

    return score

def precision_score(y_true, y_pred, test_idx=None):
    if test_idx == None:
    	score = sklearn.metrics.precision_score(y_true, y_pred, average='macro')
    else:
    	score = sklearn.metrics.precision_score(y_true[:test_idx], y_pred[:test_idx], average='macro')

    return score

def f1_score(y_true, y_pred, test_idx=None):
    if test_idx == None:
    	score = sklearn.metrics.f1_score(y_true, y_pred, average='macro')
    else:
    	score = sklearn.metrics.f1_score(y_true[:test_idx], y_pred[:test_idx], average='macro')

    return score

def mean_roc_auc_score(y_true, y_pred, test_idx=None):
    if test_idx == None:
        return sklearn.metrics.roc_auc_score(y_true, y_pred)
    else:
        return sklearn.metrics.roc_auc_score(y_true[:test_idx], y_pred[:test_idx])

def root_mean_squared_error(y_true, y_pred, test_idx=None):
    if test_idx == None:
    	score = sklearn.metrics.mean_squared_error(y_true, y_pred)**0.5
    else:
    	score = sklearn.metrics.mean_squared_error(y_true[:test_idx], y_pred[:test_idx])**0.5

    return score
