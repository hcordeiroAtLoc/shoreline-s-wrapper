import logging
import yaml
from typing import Dict, Any
from pathlib import Path
from datetime import datetime, date
from shoreline_s_wrapper.dimensions import (
    REQUIRED_FIELDS,
    DEFAULT_DATE_FORMAT,
    KNOWN_PATH_FIELDS,
)

# TODO enforce isoformat for dates


def is_all_required_fields_present(
    config: Dict[str, any], required_fields: list = REQUIRED_FIELDS
) -> bool:

    missing_fields = [f for f in required_fields if f not in config]
    if missing_fields:
        logging.warning((f"Missing required fields: {', '.join(missing_fields)}"))
        return False
    return True


def cast_config_datetime_obj_to_date_str(config: dict) -> dict:
    # TODO Allow datetimes
    return {
        key: (
            val.strftime(DEFAULT_DATE_FORMAT)
            if (isinstance(val, datetime) | isinstance(val, date))
            else val
        )
        for key, val in config.items()
    }


def load_yaml_config(
    config_path: str,
) -> Dict[str, Any]:
    """
    YAML configuration loader
    Args:
        config_path: Path to YAML config file
    Returns:
        Dictionary with configuration parameters
    """
    with open(Path(config_path), "r") as f:
        config = yaml.safe_load(f)

    # Remove metadata fields if present
    config.pop("config_version", None)
    config.pop("description", None)

    return config
