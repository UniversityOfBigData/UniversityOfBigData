from . import evaluation
from django_pandas.io import pd
import numpy as np

def calculate_score(evaluation_type, y_true, y_pred, test_idx, final_idx):
    # test_idx:分割部分のindex、final_idx:末端index
    if evaluation_type == 'mean_squared_error':
        score = evaluation.mean_squared_error(y_true, y_pred, test_idx)
        final_score = evaluation.mean_squared_error(y_true, y_pred, final_idx)

    elif evaluation_type == 'roc_auc_score':
        score = evaluation.roc_auc_score(y_true, y_pred, test_idx)
        final_score = evaluation.roc_auc_score(y_true, y_pred, final_idx)

    elif evaluation_type == 'mean_absolute_error':
        score = evaluation.mean_absolute_error(y_true, y_pred, test_idx)
        final_score = evaluation.mean_absolute_error(y_true, y_pred, final_idx)

    elif evaluation_type == 'root_mean_squared_error':
        score = evaluation.root_mean_squared_error(y_true, y_pred, test_idx)
        final_score = evaluation.root_mean_squared_error(y_true, y_pred, final_idx)

    elif evaluation_type == 'mean_roc_auc_score':
        score = evaluation.mean_roc_auc_score(y_true, y_pred, test_idx)
        print(score)
        final_score = evaluation.mean_roc_auc_score(y_true, y_pred, final_idx)

    elif evaluation_type == 'accuracy':
        score = evaluation.accuracy_score(y_true, y_pred, test_idx)
        final_score = evaluation.accuracy_score(y_true, y_pred, final_idx)

    elif evaluation_type == 'recall':
        score = evaluation.recall_score(y_true, y_pred, test_idx)
        final_score = evaluation.recall_score(y_true, y_pred, final_idx)

    elif evaluation_type == 'precision':
        score = evaluation.precision_score(y_true, y_pred, test_idx)
        final_score = evaluation.precision_score(y_true, y_pred, final_idx)

    elif evaluation_type == 'f1':
        score = evaluation.f1_score(y_true, y_pred, test_idx)
        final_score = evaluation.f1_score(y_true, y_pred, final_idx)

    else:
        raise ValueError(f'Unknown evaluation_type: {evaluation_type}')

    return score, final_score

def read_file_key(file_key):
    df_data = pd.read_csv(file_key, header=None)
    y_data = df_data[0].values
    return y_data
