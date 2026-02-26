import logging
from time import time
from pathlib import Path
from typing import Union, Dict, Any
import shoreline_s_wrapper.config_loader as cl
import shoreline_s_wrapper.matlab_utils as mu
from shoreline_s_wrapper.extract import (
    load_shoreline_matfile,
    extract_time_vector,
    extract_coastline_data,
    make_time_indexed_coastline_df,
)

# TODO: Create output directory if doesn't exist
#         (os.makedirs(config['outputdir'], exist_ok=True))

# TODO: Implement timeout for MATLAB operations
#         (eng.ShorelineS(..., timeout=3600))

# TODO: Document MATLAB struct return format
#         (add Returns section to run_shoreline_simulation docstring)

# TODO: Implement parameter sanitization
#          (prevent path traversal in config paths)

# TODO allow timesteps smaller than days in time vector extraction from output
#

# TODO project root is hardcoded in dimensions
#

# TODO test model for yaml/python array inputs
#

# Configure logging at the module level
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def run_with_engine(config, eng):
    mu.initialize_matlab_paths(eng)
    ml_config = mu.config_to_matlab_struct(eng, config)

    # model execution
    start_time = time()
    state, output = eng.ShorelineS(ml_config, nargout=2)
    logger.info(f"Simulation Done in {round(time() - start_time, 2)} seconds")
    return state, output


def run_shoreline_simulation(config_input: Union[str, Path, Dict[str, Any]], eng=None):
    """
    Complete workflow from config to model execution
    """
    if isinstance(config_input, (str, Path)):
        logger.info(f"Loading yaml config file: {config_input}")
        config = cl.load_yaml_config(str(config_input))
    elif isinstance(config_input, dict):
        logger.info("Loading provided config dictionary")
        config = config_input.copy()
    else:
        raise TypeError(f"config_input must be str, Path, or dict, got {type(config_input)}")
    
    config_date_casted = cl.cast_config_datetime_obj_to_date_str(config)

    if not cl.is_all_required_fields_present(config):
        logger.error("Missing shoreline_s required fields!")
        raise ValueError()

    if not eng:
        with mu.MATLABSession() as session:
            logger.info("Initialized Matlab Engine")
            state, output = run_with_engine(config_date_casted, eng=session.eng)
            return state, output

    state, output = run_with_engine(config_date_casted, eng=eng)
    return state, output


# Export main function for easy import
__all__ = [
    "run_shoreline_simulation",
    "load_shoreline_matfile",
    "extract_time_vector",
    "extract_coastline_data",
    "make_time_indexed_coastline_df",
]
