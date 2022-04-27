import sys

# Get the location of the module
sys.path.append('/home/johnsalako/Desktop/cmse802/root_variability_simulator/root_simulator')
import sensitivity_build as sb
import pytest
import numpy as np

mis_sens_build = sb.ElectrodeScheme('invalid_data.stg')
extract_sens_build = sb.ElectrodeScheme('test_data.stg')

def test_missing_file():
    # Test if the function raises the exception if non-existing file name is passed as parameter.
    with pytest.raises(ValueError) as excinfo:
        mis_sens_build.extract_electrode()

    assert "does not exist" in str(excinfo.value)

def test_extract_electrode():
    with pytest.raises(ValueError) as info:
        extract_sens_build.extract_electrode()
        
    assert "not surported" in str(info.value)

