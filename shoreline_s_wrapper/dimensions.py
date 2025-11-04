"""
Constants and required field definitions for ShorelineS wrapper
"""


MODELLING_PROJECT_ROOT = "d:\HCORDEIRO\shorelines_project"  # TODO dynamize
DEFAULT_DATE_FORMAT = "%Y-%m-%d"

# Required fields for ShorelineS (must be present in config)
REQUIRED_FIELDS = [
    "storageinterval",
    ]

KNOWN_PATH_FIELDS = {
    'LDBcoastline', 'LDBnourish', 'fnorfile', 'outputdir',
    'coastline_file', 'nourishment_file', 'output_directory'
}

# Unit definitions for documentation
UNITS = {
    'd': 'meters',
    'Hso': 'meters',
    'phiw0': 'degrees',
    'dt': 'days',
    'ds0': 'meters',
    'storageinterval': 'days',
}