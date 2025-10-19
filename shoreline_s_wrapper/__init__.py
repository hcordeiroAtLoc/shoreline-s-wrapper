import logging

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


def run_shoreline_simulation(config_path: str):
    """
    Complete workflow from YAML to model execution
    """
    logger.info("Loading yaml config file")
    config = cl.load_yaml_config(config_path)
    config_date_casted = cl.cast_config_datetime_obj_to_date_str(config)

    if not cl.is_all_required_fields_present(config):
        logger.error("Missing shoreline_s required fields!")
        raise ValueError()

    with mu.MATLABSession() as session:
        logger.info("Initialized Matlab Engine")
        eng = session.eng
        logger.info(eng.pwd())
        mu.initialize_matlab_paths(eng)
        ml_config = mu.config_to_matlab_struct(eng, config_date_casted)
        logger.info(ml_config)

        # Your model execution - will cleanup even if interrupted
        S, O = eng.ShorelineS(ml_config, nargout=2)
        return S, O


# Export main function for easy import
__all__ = [
    "run_shoreline_simulation",
    "load_shoreline_matfile",
    "extract_time_vector",
    "extract_coastline_data",
    "make_time_indexed_coastline_df",
]


if __name__ == "__main__":
    config_path = (
        "d:\HCORDEIRO\shorelines_project\workspace\configs\ShorelineS_spit_base.yaml"
    )
    inputs, results = run_shoreline_simulation(config_path)
