"""Implements in static dir."""

import logging
from .metric_base import (
        MSE, MAE, RMSE, ROCAUC,
        Accuracy, Recall, Precision, F1,
        ExactMatchRatio,
        )

logger = logging.getLogger(__name__)


metrics = {
        'mean_squared_error': MSE,
        'mean_absolute_error': MAE,
        'root_mean_squared_error': RMSE,
        'roc_auc_score': ROCAUC,
        'accuracy': Accuracy,
        'recall': Recall,
        'precision': Precision,
        'f1': F1,
        'exact_match_ratio': ExactMatchRatio,
        }


try:
    from . import user_defined
    metrics.update(user_defined.metrics)
except ImportError:
    logger.info('No custom evaluation')
