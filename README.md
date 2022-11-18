# root_variability_simulator 
![res_mod_dd](https://user-images.githubusercontent.com/97548163/202792254-3c4f5fd4-eaed-417f-b6a0-a649a01515e3.gif)

The Root variability Simulator seeks to visualize and represent the root spatial variation of trees in the soil using mainly resistivity values obtained from the Electrical Resistivity Geophysical Survey.

The main package (root_simulator) contains three modules namely:
- read_res_data
- root_simulator
- sensitivity_build

# GETTING STARTED!
##### Create an environment for the root_simulator software.
The software dependency and requirements has been exported to the root_simulator.yml found in the parent directory (root_variability_simulator), and can be installed and activated using the following command lines

1. 
for linux or Mac users:
`conda env create -f ./<location>/root_variability_simulator/root_simulator.yml`

for windows users:
`conda env create -f .\<location>/root_variability_simulator\root_simulator.yml`

2. 
Activate environment:
`conda activate root_simulator`

The two major dependencies used for this project are pygimli and pybert developed by the same author. For some reasons, the pybert on anaconda is not functional. Hence, you'd have one more task to do.

3. 
Run the following code in a preferred folder, and copy `pybert` folder to the root_simulator environment.
- `git clone https://gitlab.com/resistivity-net/bert.git`
- navigate to  `./bert/python/` and copy `pybert` folder to the root_simulator environment site-package.
- paste `pybert` in `~/anaconda3/envs/root_simulator/lib/python3.10/site-packages` or  `~\Anaconda3\envs\root_simulator\lib\python3.10\site-packages` for windows users. 

### Running the Notebooks provided in the example directory
- The example folder contain examples on the application of the root_simulator package.

PATH: `../root_variability_simulator/example/`

There are three jupyter notebook that displays how to use the individual modules.
There are two sub-directories in the example folders:

- The `read_n_modify_data folder` contains Two raw supersing files that can be used to perform several procedural changes to the supersting raw file.
The read_res_data module is used to process the raw file into a unified data format as displayed in the notebook, producing .dat file. The sensitivity_build module takes it up from there and performs several engineering features that modifies the given electrode configuration as shown in the notebook. Producing this phenomenon was one of the major milestone of this project. The sensitivity_build module is perhaps the first module to contain the capability of transforming an investigated data point to other electrode configuration to be used for later advanced studies. 

- The `root_simulator` folder also contains two jupyter notebook, namely simulate_root and simulate_root_data. The simulate_root notebook performs simulation of root variability in the subsurface using created synthetic data, and performs several sensitivity test of each electrode configuration in accurately producing and predicting the best inversion results of the root distribution under consideration. 
The simulate_root_data contains example codes on how to analyze the collected data, using the RootSimulator2 class from the root_simulator module.
The figures folder created has some beautiful results from the simulations and can be recreated using any desirable electrode configuration as stipulated in the notebook. This can also be extended to model the depth of the acquifer or other contrasting resistivity material located below the surface, and can be used to ascertain the depth of the feature being investigated.

The root_variablity_simulator software offers a novel approach to simulate the structure to be investigated at the subsurface, and via the results of the simulation, more informed and strategic action can be taken and used for the geophysical survey.

Having a vast usability, the root_variability_simulator can present the best electrode configutation method to deploy depending on the performance of the individual simulations.
