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


def initialize_matlab_paths(eng, root_path = MODELLING_PROJECT_ROOT):
    """Set up MATLAB paths from Python"""
    root_path = Path(root_path)
    model_dir = Path("shorelines")

    paths_to_add = [
        root_path / model_dir,
        root_path / Path('workspace'),
        root_path / model_dir / Path('functions'),    
    ]
    
    for path in paths_to_add:
        ml_paths = eng.genpath(str(path))
        eng.addpath(ml_paths, nargout=0)

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
        # Skip any remaining metadata fields
        if key.startswith('_'):
            continue
            
        # Handle null/None values
        if value is None:
            ml_struct[key] = eng.nan  # TODO validate this behavior
        # Convert lists to MATLAB arrays
        elif isinstance(value, list):
            clean_list = [v if v is not None else eng.nan for v in value]
            ml_struct[key] = matlab.double(clean_list)
        # Pass through other values
        else:
            ml_struct[key] = value
    
    return ml_struct