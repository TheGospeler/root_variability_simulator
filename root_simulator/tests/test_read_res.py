import read_res_data
import pytest
import numpy as np


def test_missing_file_sp():
    # Test if the function raises the exception if non-existing file name is passed as parameter.
    with pytest.raises(ValueError) as excinfo:
        read_res_data.supersting_processing("survey.stg")

    assert "does not exist" in str(excinfo.value)


def test_num_col(file_name):
    with open(file_name, 'r') as file:
        data = file.readlines()
    get_record = data[1][-4:-1] # This will be in string, but can be converted to int, if they're numbers.
    assert type(int(get_record)) == int

    # Test column accuracy
    auth_col = np.genfromtxt(file_name, delimiter=',', skip_header=3)
    assert int(get_record) == auth_col.shape[0]


def test_missing_file_s4b():
    # Test if the function raises the exception if non-existing file name is passed as parameter in the s4BERT.
    with pytest.raises(ValueError) as excinfo:
        read_res_data.standardized_4BERT("survey.stg")

    assert "does not exist" in str(excinfo.value)
