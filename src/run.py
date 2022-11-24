import os
import sys
import json

from json2args import get_parameter
import skgstat as skg
import numpy as np
import tqdm

# load some helper functions
from tool_lib import align_data, get_strides

# get the toolname
toolname = os.environ.get('TOOL_RUN', 'moving-window').lower()

# get the parameterization
kwargs = get_parameter()

# switch the toolname
if toolname == 'convert-input':
    try:
        positions, data = align_data(**kwargs)
    except Exception as e:
        print(str(e))
        raise e

    # write the files
    np.savetxt('/out/positions.dat', positions)
    np.savetxt('/out/data.dat', data)

# moving window
elif toolname == 'moving-window':
    # get all needed parameters
    try:
        # align the input data
        positions, data = align_data(**kwargs)

        # get the params
        window_size = kwargs['window_size']

        # build the strides-iterator
        strides = get_strides(data, positions, window_size, yield_pos=True)

        # get the variogram
        _v = kwargs.get('variogram', {})
        if isinstance(_v, str):
            with open(_v) as f:
                vario_params = json.load(f)
        else:
            vario_params = _v

    except Exception as e:
        print(str(e))
        raise e

    # container for the variograms
    # TODO: this could be replaced by the 
    varios = []

    # go for each stride 
    for i, (pos, obs) in enumerate(tqdm.tqdm(strides, total=data.shape[1] - window_size)):
        # remove NaN
        vals = obs[~np.isnan(obs)]
        coords = pos[~np.isnan(obs)]

        # here it is possible, that all obs are NaN
        if len(vals) == 0:
            print(f'{i}-All NaN input data at position: {i}')
            continue
        # build the variogram
        varios.append(skg.Variogram(coords, vals, **vario_params))

    # store the results
    params = np.asarray([v.parameters for v in varios])
    np.savetxt('/out/variogram_parameters.dat', params)

    # store empirical as .dat if lags are not auto-derived
    emp = [v.experimental for v in varios]
    if all([v.n_lags == varios[0].n_lags for v in varios]):
        np.savetxt('/out/empirical_variograms.dat', np.asarray(emp))
    
    # as a json in any case
    with open('/out/empirical_variograms.json', 'w') as f:
        json.dump(dict(
            variograms=[e.tolist() for e in emp], 
            bins=[v.bins.tolist() for v in varios]
        ), f)
    
    # save back the positions and data as well
    np.savetxt('/out/positions.dat', positions)
    np.savetxt('/out/data.dat', data)

# no tool selected
else:
    sys.exit(f'The tool {toolname} is not known.')