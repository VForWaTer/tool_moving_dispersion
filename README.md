# Moving window dispersion functions

[![Docker Image CI](https://github.com/VForWaTer/tool_moving_dispersion/actions/workflows/docker-image.yml/badge.svg)](https://github.com/VForWaTer/tool_moving_dispersion/actions/workflows/docker-image.yml)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7358567.svg)](https://doi.org/10.5281/zenodo.7358567)

This tool is a generic moving window - dispersion function / variogram calculation tool,
implemented as a gernalized version of Mälicke et al. (2020).

> Mälicke, M., Hassler, S. K., Blume, T., Weiler, M., & Zehe, E. (2020). Soil moisture: variable in space but redundant in time. Hydrology and Earth System Sciences, 24(5), 2633-2653.

It is part of the V-FOR-WaTer processing toolbox, but can also be run independently.

## How to run?

This template installs the json2args python package to parse the parameters in the `/in/parameters.json`. This assumes that
the files are not renamed and not moved and there is actually only one tool in the container. For any other case, the environment variables
`PARAM_FILE` can be used to specify a new location for the `parameters.json` and `TOOL_RUN` can be used to specify the tool to be executed.
The `run.py` has to take care of that.

To invoke the docker container directly run something similar to:
```
docker run --rm -it -v /path/to/local/in:/in -v /path/to/local/out:/out -e TOOL_RUN="convert-input" tbr_dispersion
```

Then, the output will be in your local out and based on your local input folder. Stdout and Stderr are also connected to the host.

With the toolbox runner, this is simplyfied:

```python
from toolbox_runner import list_tools
tools = list_tools() # dict with tool names as keys

# make up some data
import numpy as np
positions = np.random.randint(10, 2, size=(300, 2))
series = np.random.random(5, 13, size=(300, 1500))

# static vario params
vario = dict(model='exponential', maxlag='mean', n_lags=25)

window = tools.get('moving-window')  # it has to be present there...
window.run(result_path='./', positions=positions, data=series, window_size=60, variogram=vario)
```
The example above will create a temporary file structure to be mounted into the container and then create a `.tar.gz` on termination of all 
inputs, outputs, specifications and some metadata, including the image sha256 used to create the output in the current working directory.


## How generic?

Tools using this template can be run by the [toolbox-runner](https://github.com/hydrocode-de/tool-runner). 
That is only convenience, the tools implemented using this template are independent of any framework.

The main idea is to implement a common file structure inside container to load inputs and outputs of the 
tool. The tool shares this structures with the [Python template](https://github.com/vforwater/tool_template_python), [R template](https://github.com/vforwater/tool_template_r), [NodeJS template](https://github.com/vforwater/tool_template_node) 
and [Octave template](https://github.com/vforwater/tool_template_octave), but can be mimiced in any container.

Each container needs at least the following structure:

```
/
|- in/
|  |- parameters.json
|- out/
|  |- ...
|- src/
|  |- tool.yml
|  |- run.py
```

* `parameters.json` are parameters. Whichever framework runs the container, this is how parameters are passed.
* `tool.yml` is the tool specification. It contains metadata about the scope of the tool, the number of endpoints (functions) and their parameters
* `run.py` is the tool itself, or a Python script that handles the execution. It has to capture all outputs and either `print` them to console or create files in `/out`

## How to build the image?

You can build the image from within the root of this repo by
```
docker build -t tbr_dispersion .
```

Use any tag you like. If you want to run and manage the container with [toolbox-runner](https://github.com/hydrocode-de/tool-runner)
they should be prefixed by `tbr_` to be recognized. 

Alternatively, the contained `.github/workflows/docker-image.yml` will build the image for you 
on new releases on Github. You need to change the target repository in the aforementioned yaml.

