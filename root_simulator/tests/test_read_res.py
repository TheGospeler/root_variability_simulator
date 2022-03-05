import read_res_data
import pytest
import numpy as np 

def test_load_res_data():
    # Test if the function raises the exception if nonexisting file name is passed as a parameter.
    with pytest.raises(ValueError) as excinfo:
        read_res_data.res_data("res_data.mg")
        assert "file not found" in str(excinfo.value)

