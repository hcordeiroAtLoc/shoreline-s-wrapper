import scipy.io as sio
import numpy as np
import pandas as pd
from datetime import timedelta, date
from typing import Dict, Any, List
from pathlib import Path

START_TIME_FIELD_NAME = "reftime"
TIMESTEP_FIELD_NAME = "dt"


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
        "model_state": mat_data.get("S", np.array([])),  # Input settings
        "output": mat_data.get("O", np.array([])),  # Output results
        # 'P': mat_data.get('P', np.array([])),  # ignore
        "metadata": {
            "header": mat_data.get("__header__", b"").decode("utf-8"),
            "version": mat_data.get("__version__", ""),
            "globals": mat_data.get("__globals__", []),
        },
    }

    return results


def extract_nested_array(data, field_name: str, default=None):
    """
    Extract nested arrays from MATLAB structures
    """
    # TODO improve, make safe
    field_data = data[field_name][0][0]  # Unnest the array
    return field_data if field_data.size > 0 else default


def extract_time_vector(model_data: Dict[str, Any], config: dict) -> np.array:
    """
    Extract time information from MAT file results
    """
    # TODO allow timesteps smaller than days
    model_output_data = model_data.get("output")

    iteration_cnt_key = "it"
    iterations = extract_nested_array(
        model_output_data, iteration_cnt_key, np.array([])
    )

    start_date = config.get(START_TIME_FIELD_NAME)  # already a date/datetime

    time_interval_in_years = config.get(TIMESTEP_FIELD_NAME)
    time_interval_in_days = timedelta(days=time_interval_in_years / (1 / 365))

    return np.array(
        [start_date + time_interval_in_days * it for it in iterations.flatten()]
    )


def extract_coastline_data(model_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract coastline data
    """
    # TODO make safe, warn when arrays empty
    model_output_data = model_data.get("output")
    coastline = {
        "x": extract_nested_array(model_output_data, "x", np.array([])),
        "y": extract_nested_array(model_output_data, "y", np.array([])),
    }

    return coastline


def make_time_indexed_coastline_df(
    coastline_coords_dict: dict,
    time_vector: List[date],
) -> pd.DataFrame:

    group_size, timesteps = coastline_coords_dict.get("x").shape

    assert (
        len(time_vector) == timesteps
    ), """Time vector must be same size as number of columns in modeled coastline data!"""

    x_flat = coastline_coords_dict.get("x").flatten()
    y_flat = coastline_coords_dict.get("y").flatten()

    time_index = pd.DatetimeIndex(dt for dt in time_vector for _ in range(group_size))

    return pd.DataFrame(dict(x=x_flat, y=y_flat), index=time_index)
