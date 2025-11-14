import numpy as np

def to_serializable(obj):
    if isinstance(obj, (np.int64, np.int32, np.integer)):
        return int(obj)
    if isinstance(obj, (np.float64, np.float32, np.floating)):
        return float(obj)
    if isinstance(obj, (np.bool_)):
        return bool(obj)
    return obj
