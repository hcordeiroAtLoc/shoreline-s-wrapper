import matlab.engine
import os
import signal
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from shoreline_s_wrapper.dimensions import MODELLING_PROJECT_ROOT

# TODO-1: Add error handling for MATLAB engine startup
#         (matlab.engine.EngineError)
# TODO-5: Add MATLAB version compatibility check
#         (eng.version() >= '9.11' for R2021b+)

# Set up logging
logger = logging.getLogger(__name__)

class MATLABSession:
    """Managed MATLAB session with graceful shutdown handling"""
    
    def __init__(self):
        self.eng: Optional[matlab.engine.MatlabEngine] = None
        self._original_sigint_handler = None
        self._original_sigterm_handler = None
        
    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - always cleanup"""
        self.quit()
        
    def start(self) -> matlab.engine.MatlabEngine:
        """Start MATLAB engine with signal handlers"""
        logger.info("Starting MATLAB engine...")
        self.eng = matlab.engine.start_matlab()
        
        # Set up signal handlers for graceful shutdown
        self._setup_signal_handlers()
        
        logger.info("MATLAB engine started successfully")
        return self.eng
        
    def quit(self):
        """Gracefully shutdown MATLAB engine"""
        if self.eng is not None:
            try:
                logger.info("Shutting down MATLAB engine...")
                self.eng.quit()
                logger.info("MATLAB engine shutdown complete")
            except Exception as e:
                logger.warning(f"Error during MATLAB shutdown: {e}")
            finally:
                self.eng = None
                self._restore_signal_handlers()
                
    def _setup_signal_handlers(self):
        """Set up signal handlers for graceful interruption"""
        def graceful_shutdown(signum, frame):
            logger.warning(f"Received signal {signum}, shutting down MATLAB...")
            self.quit()
            # Re-raise signal to allow normal process termination
            signal.signal(signum, signal.SIG_DFL)
            os.kill(os.getpid(), signum)
            
        # Save original handlers
        self._original_sigint_handler = signal.signal(signal.SIGINT, graceful_shutdown)
        self._original_sigterm_handler = signal.signal(signal.SIGTERM, graceful_shutdown)
        
    def _restore_signal_handlers(self):
        """Restore original signal handlers"""
        if self._original_sigint_handler:
            signal.signal(signal.SIGINT, self._original_sigint_handler)
        if self._original_sigterm_handler:
            signal.signal(signal.SIGTERM, self._original_sigterm_handler)
            
    def is_active(self) -> bool:
        """Check if MATLAB engine is active"""
        return self.eng is not None


def initialize_matlab_paths(
        eng, 
        root_path = None
        ):
    """Set up MATLAB paths from Python"""
    matlab_functions_dir = Path("mat_functions")
    if root_path:
        root_path = Path(root_path)
    else:
        # NOTE: sensitive to changes in dir structure
        # Get the absolute path to this file's directory
        current_file = Path(__file__).resolve()
        root_path = current_file.parent.parent 
        logging.info(f"root path: {root_path}")

    paths_to_add = [
        root_path / matlab_functions_dir,
    ]
    
    for path in paths_to_add:
        ml_paths = eng.genpath(str(path))
        eng.addpath(ml_paths, nargout=0)

def looks_like_matlab_cell(s: str) -> bool:
    s = s.strip()
    return s.startswith("{") and s.endswith("}") and "," in s

def is_known_str_type_list(k: str) -> bool:
        str_type_list_keys = {"LDBplot"}  # TODO move to dimensions
        return k in str_type_list_keys

def config_to_matlab_struct(eng: matlab.engine.MatlabEngine, 
                          config: Dict[str, Any]) -> Any:
    """
    Converts Python dictionary to MATLAB struct
    Args:
        eng: MATLAB engine instance
        config: Configuration dictionary
    Returns:
        MATLAB struct ready for ShorelineS
    """
    ml_struct = eng.struct()

    for key, value in config.items():
        # logging.info(f"Processing: {key}, {value}")
        # Skip any remaining metadata fields
        if key.startswith('_'):
            continue
            
        # Handle null/None values
        if value is None:
            ml_struct[key] = eng.nan  # TODO validate this behavior
        # Convert lists to MATLAB arrays

        if isinstance(value, str) and looks_like_matlab_cell(value):
             ml_struct[key] = eng.eval(value)   ## FIXME dangerous

        elif isinstance(value, list):
            if len(value) == 0:
                ml_struct[key] = matlab.double([])
            elif is_known_str_type_list(key):
                ml_struct[key] = eng.cellstr(value)
            else:
                clean_list = [v if v is not None else eng.nan for v in value]  # mixing types ......
                ml_struct[key] = matlab.double(clean_list)
            
        # Pass through other values
        else:
            ml_struct[key] = value
    
    return ml_struct