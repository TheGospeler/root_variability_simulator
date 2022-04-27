import sys

# Get the location of the module
sys.path.append('/home/johnsalako/Desktop/cmse802/root_variability_simulator/root_simulator')
import read_res_data
import pytest
import numpy as np

test_file = "test_data.stg"
test_file2 = "test_data2.dat"

def test_missing_file_sp():
    # Test if the function raises the exception if non-existing file name is passed as parameter.
    with pytest.raises(ValueError) as excinfo:
        read_res_data.supersting_processing('invalid_data.stg')

    assert "does not exist" in str(excinfo.value)


def test_file_format():
    with pytest.raises(ValueError) as info:
        read_res_data.supersting_processing(test_file2)
        
    assert "not a supersting file" in str(info.value)


def test_missing_file_s4b():
    # Test if the function raises the exception if non-existing file name is passed as parameter in the s4BERT.
    with pytest.raises(ValueError) as excinfo:
        read_res_data.standardized_bert("super_data.stg")

    assert "does not exist" in str(excinfo.value)
