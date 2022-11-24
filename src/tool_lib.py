from typing import Union, Tuple
import warnings

import pandas as pd
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view


def align_data(positions: Union[pd.DataFrame, np.ndarray], data: Union[pd.DataFrame, np.ndarray], **kwargs) -> Tuple[np.ndarray, np.ndarray]:
    if isinstance(data, np.ndarray) and isinstance(positions, np.ndarray):
        assert data.shape[0] == positions.shape[0]
        return positions, data
    
    # Otherwise one of inputs is a CSV and the data has to be aligned.
    # valid dimnesion names
    DIM = ('x', 'y', 'z')
    # first go for the data array
    if isinstance(data, np.ndarray):
        data = pd.DataFrame(data=data, columns=[f'pos_{i}' for i in range(data.shape[0])])
    
    # set the positions
    if isinstance(positions, np.ndarray):
        positions = pd.DataFrame(data=positions, columns=[DIM[i] for i in range(positions.shape[1])])
        positions['pos'] = [f'pos_{i}' for i in range(positions.shape[0])]
    
    # make the positions column
    id_col = [c for c in positions.columns if c not in DIM]
    if len(id_col) == 0:
        positions['pos'] = [f'pos_{i}' for i in range(positions.shape[0])]
    else:
        positions['pos'] = positions[[id_col[0]]].values
    
    # make sure there are enough positions
    assert all([col in positions.pos.values for col in data.columns])

    # get the positions into the right order
    ord_pos = positions.set_index('pos').loc[data.T.index,]
    
    # create the output arrays
    posarr = ord_pos[[_ for _ in ord_pos.columns if _ in DIM]].values
    dataarr = data.T.values

    return posarr, dataarr


def get_strides(data: np.ndarray, positions: np.ndarray, window_size: int, agg_func=np.nanmean, yield_pos=True):
    # derive the needed shape
    shape = (positions.shape[0], window_size)

    # create the strides
    strides = sliding_window_view(data, shape)[0]
    
    # iterate over each stride
    for stride in strides:
        if agg_func is not None:
            with warnings.catch_warnings():
                # there will be warnings about empty slices at the beginning of window.
                warnings.simplefilter('ignore')
                # aggregate the slice
                obs = agg_func(stride, axis=1)
        else:
            obs = stride
        
        # yield positions and data
        if yield_pos:
            yield positions, obs
        else:
            yield obs
