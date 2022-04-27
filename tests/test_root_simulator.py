import sys

# Get the location of the module
sys.path.append('/home/johnsalako/Desktop/cmse802/root_variability_simulator/root_simulator')
from root_simulator import RootSimulator, RootSimulator2
import pytest
import numpy as np

# Unit Test for the RootSimulator class
root_simulator = RootSimulator()
def test_feature_input1():
    with pytest.raises(ValueError) as excinfo:
        # one of the points is devoid of (x, y)
        root_simulator.create_geom([50, -50], -50,[-1, -20], [(-10,), (17, -8), (5,-1)]) 
    assert "must contain (x, y)" in str(excinfo.value)
    
def test_feature_input2():
    with pytest.raises(ValueError) as excinfo:
        # -30 and 30 are beyond the specified depth extent
        root_simulator.create_geom(x_ext=[50, -50], y_ext= -50,layer=[-1, -20], feature=[(-10, -30), (17, 30), (5,-1)])
    assert "within the layer's depth" in str(excinfo.value)
    
def test_feature_input3():
    with pytest.raises(ValueError) as excinfo:
        # 40 (one of the given x points) is close to the boundary (50)
        # The inversion process requires a space of atleast 20 meters between the objects
        # and the boundary for optimal results
        root_simulator.create_geom(x_ext=[50, -50], y_ext= -50, layer=[-1, -20], feature=[(-10, -1), (40, -12), (5,-1)])
    assert "close to the boundary points" in str(excinfo.value)
    
def test_create_mesh():
    with pytest.raises(ValueError) as excinfo:
        # kk is not a valid electrode scheme available
        root_simulator.create_mesh('kk')
    assert "not a valid scheme_name" in str(excinfo.value)
    
    
# Unit Test for the RootSimulator2 class
# Confirm the data format is in the right format
missing_dat = RootSimulator2('invalid_data.stg')
data_format = RootSimulator2('test_data2.dat')

def test_missing_file():
    # Test if the function raises the exception if non-existing file name is passed as parameter.
    with pytest.raises(ValueError) as excinfo:
        missing_dat.generate_mesh()
    assert "does not exist" in str(excinfo.value)

def test_extract_electrode():
    with pytest.raises(ValueError) as info:
        data_format.generate_mesh()
    assert "not a supersting file" in str(info.value)

