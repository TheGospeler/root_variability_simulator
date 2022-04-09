# root_variability_simulator

The Root variability Simulator seeks to visualize and represent the root spatial variation of trees in the soil using mainly resistivity values obtained from the Electrical Resistivity Geophysical Survey.

The main package (root_simulator) contains three modules namely:
- read_res_data
- root_simulator
- sensitivity_build

# GETTING STARTED!
##### Create environment for the root_simulator software.
The software dependency and requirements has been exported to the root_simulator.yml found in the parent directory (root_variability_simulator), and can be installed and activated using the following command lines

`conda env create --prefix ./envs --root_simulator.yml`
`conda activate ./envs`

Example jupyter notebooks are found in the example folder in the `Models` directory.
PATH: `../root_variability_simulator/Models/example/`

There are Two jupyter notebook that displays how to use the individual modules for specific reason.

They can be found in the `../root_variability_simulator/Models/example/`
- The `read_n_modify_data folder` contains Two raw supersing files that can be used to perform several procedural changes to the supersting raw file.
The read_res_data module is used to process the raw file into a unified data format as displayed in the notebook, producing .dat file.

The sensitivity_build module takes it up from there and performs several engineering features that modifies the given electrode configuration as shown in the notebook. Producing this phenomenon was one of the major milestone of this project. The sensitivity_build module is perhaps the first module to contain the capability of transforming an investigated data point to other electrode configuration to be used for later advanced studies. 

- The `root_simulator` folder contains the simulate_root example notebook that performs simulation of root variability in the subsurface using created synthetic data and performing several sensitivity test of each electrode configuration in accurately producing the best inversion results of the root distribution under consideration.

The figures folder created has some beautiful results from the simulations and can be recreated using any desirable electrode configuration as stipulated in the notebook. This can also be extended to model the depth of the acquifer or other contrasting resistivity material located below the surface, and can be used to ascertain the depth of the feature being investigated.

The root_variablity_simulator software offers a novel approach to simulate the structure to be investigated at the subsurface, and via the results of the simulation, more informed and strategic action can be taken and used for the geophysical survey.

Having a vast usability, the root_variability_simulator can present the best electrode configutation method to deploy depending on the performance of the individual simulations.