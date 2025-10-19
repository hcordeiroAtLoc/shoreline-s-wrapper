# shoreline-s-wrapper **IN DEVELOPMENT**

A lightweight Python interface for the **ShorelineS** one-line shoreline evolution model (Roelvink et al., 2020).  
The user provides a YAML configuration file that defines simulation parameters and allows inclusion of comments.  
The library manages communication with **MATLAB**, executes the ShorelineS model, and returns results as structured matrices (pandas DataFrames).  

This implementation facilitates automated shoreline simulations, model calibration, and seamless integration with Python-based data science workflows.


## MATLAB Engine Setup

This package requires the **MATLAB Engine API for Python**. Install it manually by following these steps:

1. Find your MATLAB installation directory  
2. Open a terminal and run:  
   cd "matlabroot/extern/engines/python"
3. Then install the engine:  
   python setup.py install


## Example Usage

import shoreline_s_wrapper as ssw

config_path = Path("configs/refactored_forte.yaml")

_, _ = ssw.run_shoreline_simulation(config_path=config_path)

## Requirements
- Python ≥ 3.8   
- MATLAB Engine API for Python  
- pandas, PyYAML  

## Reference
Roelvink, D., et al. (2020). *ShorelineS: A one-line model for long-term shoreline evolution*.  
Coastal Engineering.
