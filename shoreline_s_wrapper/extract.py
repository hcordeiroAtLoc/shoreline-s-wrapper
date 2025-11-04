import scipy.io as sio
import numpy as np
import pandas as pd
from datetime import timedelta, date
from typing import Dict, Any, List, Union, Optional
from pathlib import Path

START_DATE_FIELD = "reftime"
END_DATE_FIELD = "endofsimulation"
TIMESTEP_FIELD = "dt"


class TimeAxis:
    def __init__(
        self,
        timestep_in_years: int,
        iteration_array: np.ndarray,
        start_date: Optional[Union[str, pd.Timestamp]] = None,
    ):
        """
        A unified time-axis generator for both calendar-based and synthetic model runs.
        """
        self.timestep_in_days = pd.to_timedelta(timestep_in_years * 365, unit="D").round("s")
        self.iteration_array = iteration_array
        self.start_date = pd.Timestamp(start_date) if start_date else None
        self.synthetic = self.start_date is None
        self.time_vector = self._build_time_vector()

    def _build_time_vector(self):
        """Constructs the time vector depending on the mode."""
        
        if self.synthetic:
            raise ValueError("Synthetic time vector creation not implemented.")
        
        # Calendar-based run
        if self.start_date is not None:
            return np.array(
                [self.start_date + self.timestep_in_days * it for it in self.iteration_array]
            )
        
    def __len__(self):
        """Return number of time steps in time vector."""
        return len(self.time_vector)

    def __repr__(self):
        mode = "synthetic" if self.synthetic else "calendar"
        freq = self.timestep_in_days * self.iteration_array[1]

        return f"<TimeAxis mode={mode}, dt_in_days={freq}, len={len(self.time_vector)}>"


def load_shoreline_matfile(matfile_path: Path) -> Dict[str, Any]:
    """
    Load ShorelineS MAT file and extract useful data structures
    """
    if not matfile_path.exists():
        raise FileNotFoundError(f"MAT file not found: {matfile_path}")

    # Load the MAT file
    mat_data = sio.loadmat(str(matfile_path))

    # Extract main components
    results = {
        "model_state": mat_data.get("S", np.array([])),  # Input and state settings
        "output": mat_data.get("O", np.array([])),  # Output results
        # 'P': mat_data.get('P', np.array([])),  # ignore
        "metadata": {
            "header": mat_data.get("__header__", b"").decode("utf-8"),
            "version": mat_data.get("__version__", ""),
            "globals": mat_data.get("__globals__", []),
        },
    }

    return results

def extract_from_matlab_array(data, field_name: str, default=np.array([])):
    # TODO  make key-safe
    field_data = np.array(data[field_name]).squeeze()
    return field_data if len(field_data) > 0 else default


def extract_time_vector(modeled_data: Dict[str, Any], config: dict) -> TimeAxis:
    """
    Extracts or constructs a time vector from model configuration and outputs,
    using the TimeAxis abstraction for consistency between calendar and synthetic runs.
    """
    # read configuration parameters
    start_date = config.get(START_DATE_FIELD)
    timestep_in_years = config.get(TIMESTEP_FIELD)

    iterations_array_key = "it"
    timesteps_array_key = "nt"

    iterations = extract_from_matlab_array(modeled_data, iterations_array_key)
    timesteps = extract_from_matlab_array(modeled_data, timesteps_array_key)
    
    # Arrays of iterations carry the number of dts passed until output
    # The frequency is given by ShorelineS param "storageinterval"
    # i.e: [0, 360] for a dt of 1 hour -> [0, 15 days]
    # i.e: [0, 365] for a dt of 1 day  -> [0, 1 year]
    iteration_array = iterations if len(iterations) > 0 else timesteps
    
    if start_date:
        return TimeAxis(
            timestep_in_years=timestep_in_years, 
            iteration_array=iteration_array, 
            start_date=start_date
            )

    return TimeAxis(
            timestep_in_years=timestep_in_years, 
            iteration_array=iteration_array, 
            )


def extract_coastline_data(modeled_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract coastline data
    """
    # TODO make safe, warn when arrays empty
    return {
            "x": extract_from_matlab_array(modeled_data, "x"),
            "y": extract_from_matlab_array(modeled_data, "y"),
            }


def make_time_indexed_coastline_df(
    coastline_coords_dict: dict,
    time_vector: Union[np.ndarray, pd.DatetimeIndex],
) -> pd.DataFrame:
    """
    Create a time-indexed coastline DataFrame from modeled coordinates and a time array.

    Parameters
    ----------
    coastline_coords_dict : dict
        Dictionary with keys "x" and "y", each shaped (n_points, n_timesteps).
    time_vector : np.ndarray or pd.DatetimeIndex
        Time vector of length equal to the number of timesteps.

    Returns
    -------
    pd.DataFrame
        DataFrame indexed by time with columns ['x', 'y'].
    """
    x = np.asarray(coastline_coords_dict["x"])
    y = np.asarray(coastline_coords_dict["y"])

    group_size, timesteps = x.shape
    if len(time_vector) != timesteps:
        raise ValueError(
            f"Time vector length ({len(time_vector)}) must match number of timesteps ({timesteps})."
        )

    time_index = np.repeat(time_vector, group_size)
    df = pd.DataFrame({"x": x.flatten(), "y": y.flatten()}, index=pd.DatetimeIndex(time_index))
    df.index.name = "time"
    return df
