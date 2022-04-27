"""The root_simulator module is the computational engine of the root_simulator package."""

import os
from pygimli.physics import ert
from IPython.display import HTML, clear_output
import imageio
import matplotlib.pyplot as plt
import numpy as np
import pygimli as pg
import pygimli.meshtools as mt
import read_res_data as rrd


class RootSimulator:
    """The Root simulator simulates the spatial distribution of tree roots at the subsurface.

    The RootSimulator class contains functions that enables the simulations of the subsurface to
    access the spatial variability of roots using created synthetic data to simulate the model
      accuracy and to create Electrical Resistivity Tomography (ERT).
    This package makes use of the python library for Geophysical modeling and Inversion (pyGIMLi).

    Dependable: numpy, matplotlib, pygimli.

    Functions
    ----------
    create_geom: creates an arbitrary region of the subsurface with a specific feature.
    forward_model: simulates the resistivity distribution within the created mesh.
    inversion_2D: performs simulations and return the true resistivity model.
    animate_simulation: visualizes the results of the different array configuration.

    """

    def __init__(self):
        """Initialize global variable."""
        self.mesh = 'Run create_mesh'
        self.geometry = 'Run create_geom'
        self.scheme = 'Run the create_mesh'
        # private inherent variables needed
        self.__rhomap = ''  # Makes the value of the input rhomap global
        self.__inv_data = ''  # Stores the data from the forward model, we can use for inversion
        self.__x_start = ''  # The starting point of the electrode array
        self.__x_stop = ''  # The ending point of the electrode array
        self.__layer = ''  # Used for setting up the depth of the para_domain during inversion
        self.__sch = ''  # used in the animate_simulation to create unique names of the models
        self.__unstructured_mesh_inv = ''
        self.__inversion = ''
        self.__manager = ''  # will store the inverted data

    def create_geom(self, x_ext, y_ext, layer, feature):
        """Create a 2D array using finite element method in the pygimli package.

        parameters
        ----------
        x_ext: The horizontal extension (x_axis). Should be a list... [end, start]
        y_ext: The depth profile. y_ext must be a negative value, since we are investigating
               below the subsurface.
        layer: A slice within the depth profile we want to investigate>> [start, end]
        feature: A nested list containing (x, y) nodes of the feature within the confinement
                 of the layer.

        Example-- create_geom(x_ext=[50, -50], y_ext= -50,layer=[-1, -20],
                              feature=[(-10, -1), (17, -8), (5,-1)])

        """
        # Check for errors in input parameters.
        
        # Check if the feature consists of x and y points
        for ind, _ in enumerate(feature):
            if len(feature[ind]) != 2:
                raise ValueError("The Individual points in feature must contain (x, y)")

        maxx, minx = x_ext  # Gets the overall lateral extent of the layer
        miny, maxy = layer  # Gets the depth extent

        for xx, yy in feature:
            if yy > miny or yy < maxy:
                # checks depth correctness
                raise ValueError("The feature points must be within the layer's depth")
	
            if xx > maxx - 20 or xx < minx + 20:
                raise ValueError(f"{xx} is too close to the boundary points.")
                print("To avoid issues, the lateral extent should be atleast 20 meters between \
                features to each point")

        # reassign the global y_ext
        self.__layer = layer
        # creates the dimension of the given size in the subsurface.
        world = mt.createWorld(start=[y_ext, 0], end=x_ext, layers=layer, worldMarker=True)
        # creates the feature architecture in the subsurface
        root_feature = mt.createPolygon(feature, isClosed=True, addNodes=3, marker=4)
        # integrate the feature to the layer under consideration.
        self.geometry = world + root_feature

        return self.geometry

    def display_geometry(self):
        """Display all the components created at the subsurface."""
        return pg.show(self.geometry)

    def create_mesh(self, scheme_name, start=-30, end=30, num=21, mesh_quality=34):
        """create a desired electrode configuration used investigate feature.

        parameters
        ----------
        scheme_name: should be one out of the following 'dd', 'wa', 'wb', 'pp', 'slm', 'pd'.
                     where wa- wenner alpha, slm- schlumberger, pp- pole-pole, dd- dipole-dipole
        start: commencing points should be at least 10 meter within the layer boundary
        end: ending points should also be at least 10 meter within the end of the layer boundary.
        num: num of electrode spacing.
        mesh_quality: 34 should be the maximum. The smaller the mesh the faster the computation.

        """
        if scheme_name.lower() not in ['dd', 'wa', 'wb', 'pp', 'slm', 'pd']:
            raise ValueError(f"{scheme_name} is not a valid scheme_name. Review documentation")

        self.scheme = ert.createData(elecs=np.linspace(start=start, stop=end, num=num),
                                     schemeName=scheme_name)
        # Update the selected scheme
        self.__sch = scheme_name
        # incorporate the created electrode configuration scheme inside the geometry
        for pos in self.scheme.sensors():
            self.geometry.createNode(pos)
            # adds refinement nodes in a distance of 10% of electrode spacing
            self.geometry.createNode(pos - [0, 0.1])

        # reassign the global electrode configuration
        self.__x_start = start
        self.__x_stop = end

        self.mesh = mt.createMesh(self.geometry, quality=mesh_quality)
        return self.mesh

    def plot_rhomap(self, rhomap):
        """Visualize the resistivity distribution within the mesh.

        parameter
        ---------
        rhomap: nested list consisting of the region and the associated resistivity value.

        example >> rhomap =[[1, 100], [2, 75], [4, 50], ...]
        The example above have four regions. This is dependent on the nature of the geometry,
        layer, and feature created.

        if the depth profile starts from 0, there will be only three regions in the overall
        geometry, and thus only three resistivity map values will be needed, tied to the
        region (marker). visualizing the geometry will help knowing the marker of each region.
        """
        self.__rhomap = rhomap
        return pg.show(self.mesh, data=self.__rhomap, label=pg.unit('res'), showMesh=True)

    def display_mesh(self):
        """Plot the subsurface with the created mesh"""
        return pg.show(self.mesh)

    def forward_model(self, rhomap):
        """Simulate the interpolation of the mesh, scheme and resistivity values.

        parameter
        ---------
        rhomap: resistivity of the region. For simplicity, use the regional rhomap available,
                if the individual points are not available.
        """
        data = ert.simulate(self.mesh, scheme=self.scheme, res=rhomap, noiseLevel=1,
                            noiseAbs=1e-6, seed=1337)
        # remove the values below 0
        data.remove(data['rhoa'] < 0)
        # print out the confirmation of the minimum value
        pg.info('Filtered rhoa (min/max)', min(data['rhoa']), max(data['rhoa']))
        self.__inv_data = data

        return ert.show(data, label=pg.unit('res'))

    def inversion2d(self, para_depth=30):
        """Create an inversion of the forward model to produce the feature and the layers.

        parameter
        ---------
        para_depth: the slice of the depth containing our feature
        """
        self.__manager = ert.ERTManager(self.__inv_data)
        self.__inversion = self.__manager.invert(lam=20, verbose=True, paraDepth=para_depth)

        # performs the inversion calculations and plots the inversion.
        self.__manager.showResultAndFit()
        # reassign the inversion result to the unstructured_mesh_inv
        self.__unstructured_mesh_inv = pg.Mesh(self.__manager.paraDomain)

        # perform regularization on the inverted profile
        __run_regularized = self.__perform_grid_regularization()

    def __perform_grid_regularization(self):
        # creates a regular grid for the inversion.
        x_pos = np.linspace(self.__x_start, self.__x_stop, 33)
        y_pos = pg.cat([0], pg.utils.grange(0.5, self.__layer[1], n=5))

        inversion_domain = pg.createGrid(x=x_pos, y=y_pos[::-1], marker=2)
        grid = pg.meshtools.appendBoundary(inversion_domain, marker=1, xbound=50, ybound=50)
        inversion_model = self.__manager.invert(self.__inv_data, mesh=grid, lam=20, verbose=True)
        __model_para_depth = self.__manager.paraModel(inversion_model)
        return __model_para_depth

    def display_inverted_img(self):
        """Display the inverted Image in a regular Mesh."""
        # plot the result of the inversion...
        _, axis = plt.subplots(1, 1)
        self.__manager.showResult(ax=axis, cMin=25, hold=True, cMax=150)
        axis.set_title('Inversion regular grid')

    def __true_model(self):
        """Plot and save the true model in figures directory."""
        # create directory for figures if not already created.
        if not os.path.isdir('figures'):
            os.makedirs('figures')

        # Plot the 'True Model' of the Simulation
        fig, axis = plt.subplots(1, 1, figsize=(8, 6))
        pg.show(self.mesh, self.__rhomap, ax=axis, hold=True, cMap="Spectral_r", logScale=True,
                cMin=25, cMax=150, label=pg.unit('res'))
        axis.set_title('True Model')
        axis.set_xlim(self.__manager.paraDomain.xmin(), self.__manager.paraDomain.xmax())
        axis.set_ylim(self.__manager.paraDomain.ymin(), self.__manager.paraDomain.ymax())
        plt.savefig(f'figures/TM_{self.__sch}.png')
        fig.clear()
        clear_output(wait=True)

    def __unstructured_mesh(self):
        """Plot and save the inversion unstructured mesh model in figures directory."""
        fig, axis = plt.subplots(1, 1, figsize=(8, 6))
        pg.show(self.__unstructured_mesh_inv, self.__inversion, ax=axis, hold=True,
                cMap="Spectral_r", logScale=True,
                cMin=25, cMax=150, label=pg.unit('res'))
        axis.set_title('Inversion unstructured mesh')
        axis.set_xlim(self.__manager.paraDomain.xmin(), self.__manager.paraDomain.xmax())
        axis.set_ylim(self.__manager.paraDomain.ymin(), self.__manager.paraDomain.ymax())
        plt.savefig(f'figures/IU_{self.__sch}.png')
        fig.clear()
        clear_output(wait=True)

    def __regular_mesh(self):
        """Plot and save the inversion a regular grid model in figures directory."""
        fig, axis = plt.subplots(1, 1, figsize=(8, 6))
        self.__manager.showResult(ax=axis, cMin=25, hold=True, cMax=150)
        axis.set_title('Inversion regular grid')
        axis.set_xlim(self.__manager.paraDomain.xmin(), self.__manager.paraDomain.xmax())
        axis.set_ylim(self.__manager.paraDomain.ymin(), self.__manager.paraDomain.ymax())
        plt.savefig(f'figures/IR_{self.__sch}.png')
        fig.clear()
        clear_output(wait=True)

    def animate_simulation(self):
        """Animate the transitions of three model simulations.

        The RootSimulator class simulates three models, and the animate_simulator function
        visualizes the image of the subsurface using the three models created from the synthetic
        data. The three models are the True model (which is the actual representation of the
        subsurface), the inversion using unstructured mesh, and the inversion with a regularized
        mesh.

        In Practice we may not truly identify the true model, but this is a good way to access
        the model performance with the known structure or layers under consideration; with such
        information, we can measure the performance of unknown structures with real data.
        """
        # initiate all of the models to enable saving their functions at in the figures folder
        print('Running True Model......')
        self.__true_model()
        print('Running Inversion with Unstructured Mesh Model......')
        self.__unstructured_mesh()
        print('Running Inversion with regularized grid Model......')
        clear_output(wait=True)
        print('Preparing Animation......')
        self.__regular_mesh()
        print('Starting Animation......')

        # create the animation and save it in the figures folder
        with imageio.get_writer(f'figures/res_mod_{self.__sch}.gif', mode='I', duration=1)\
                as writer:
            for filename in [f'TM_{self.__sch}.png', f'IU_{self.__sch}.png',
                             f'IR_{self.__sch}.png']:
                image = imageio.imread(f'figures/{filename}')
                writer.append_data(image)
        return HTML(f'<img src="figures/res_mod_{self.__sch}.gif">')


class RootSimulator2:
    """Produce the Forward and Inverse model of the processed supersting file.

    The RootSimulator2 class performs two major modeling to the processed data. The two main
    functions are the forward_model and inverse_model that enables the simulations of the
    surveyed subsurface using the resulting supersting.stg file.

    The raw file is processed using the standardized_bert function in the read_res_data module to
    produce the .dat file for the inversion simulation, while the data for the forward model is
    obtained via the supersting_processing to produce the *_res.dat

    This package makes use of the python library for Geophysical modeling and Inversion (pyGIMLi).

    Dependable: read_res_data, numpy, matplotlib, pygimli.

    Parameter
    ----------
    data - raw supersting file *.stg

    Functions
    ----------
    forward_model: Returns the model of the apparent resistivity across the profile.
    inverse_model: Returns the true resistivity of the subsurface under investigation.
    """

    def __init__(self, data):
        """Input data should be in the .dat format.

        The .dat file can be obtained using the standardized_bert function in the read_res_data
        module."""
        self.data = data
        self.mesh = "Run generate_mesh"
        self.__data_tr = ''  # stores the read in data
        self.__sim = ''
        self.__tr_res = ''

    def __activate_data(self):
        """Activate variables for general use."""
        # Ensure the right data file is used for the class
        if not os.path.isfile(self.data):
            raise ValueError(f"{self.data} does not exist, make sure file is in the same directory")
        if self.data[-4:] != '.stg':
            raise ValueError(f"{self.data} is not a supersting file. Input a supersting file(.stg)")

        # Updates the global variable to be used across boards
        self.__data_tr = rrd.standardized_bert(self.data)
        self.__data_tr["err"] = ert.estimateError(self.__data_tr, relativeError=0.02)
        return self.__data_tr

    def generate_mesh(self, boundary=200, depth=200, quality=34.5):
        """Generate the mesh for the inversion simulations.

        Parameters
        ----------
        boundary: The extent of allowance of current flow during the inversion calculations
                  (Margin for parameter domain in absolute sensor distances).
        depth: The depth we want to investigate (The Maximum depth for parametric domain).
        quality: Number of notes. High value creates more refined nodes. 34.5 is the maximum
        """
        # activate the data
        self.__activate_data()
        self.mesh = mt.createParaMesh(self.__data_tr.sensorPositions(), paraDX=0.5, paraDepth=200,
                                      paraBoundary=boundary, boundary=depth, quality=quality)
        return pg.show(self.mesh, markers=True)

    def forward_model(self):
        """Plots the apparent resistivity based on the x-position and Depth of Investigation.

        Visualizing the subsurface to filter outliers are a necessity to obtaining an optimal
        inversion results. Hence, the forward_model helps visualize the data and recognize the
        general distribution of the resistivity of the subsurface.
        """
        file = rrd.supersting_processing(self.data)
        # Get the midpoint with the resistivity value and plot estimation
        data = file[file[:, 1] > 0] # scale data to remove negative resistivity (anomalous data)

        # create dictionary to store position and depth of each electrode configuration
        data_bank = {}

        # Get the rows containing Wenner array based on the configuration arrangement
        wen_arr = data[data[:, 5] > data[:, 2]]

        # midpoint of the mn electrode >> (n-m/2) + m for wenner array
        # the addition of m is to maintain the exact location of the midpoint.
        x_pos_wa = ((wen_arr[:, 11] - wen_arr[:, 8]) / 2) + wen_arr[:, 8]
        depth_wa = 0.2 * (wen_arr[:, 5] - wen_arr[:, 2])  # 0.2*AB

        # update dictionary
        data_bank['Wenner Array'] = [x_pos_wa, depth_wa, wen_arr]

        # Get the rows containing dipole-dipole based on the configuration arrangement
        dip_dip = data[data[:, 5] < data[:, 2]]

        x_pos_dd = ((dip_dip[:, 5] - dip_dip[:, 8]) / 2) + dip_dip[:, 8]  # dip_dip ~ BA
        depth_dd = abs(0.2 * (dip_dip[:, 2] - dip_dip[:, 11]))  # 0.2*BN
        # update dictionary
        data_bank['Dipole-Dipole'] = [x_pos_dd, depth_dd, dip_dip]

        # Plot the two electrode configuration models
        for arr_name, values in data_bank.items():
            fig, axis = plt.subplots(figsize=(10, 7))
            info = axis.scatter(values[0], values[1], s=75, c=values[2][:, 1])
            axis.set_xlabel('Distance (m)')
            axis.xaxis.tick_top()
            axis.xaxis.set_label_position('top')
            axis.set_ylabel('Depth (m)')
            axis.invert_yaxis()  # Transforms the data to start from depth 0 - 25 meters
            axis.set_title(arr_name, fontweight='bold')
            fig.colorbar(info, orientation='horizontal', label='Res (Ωm)')

    def inverse_simulation(self):
        """Inversion Modeling of the Resistivity Data."""
        print("Creating regions....")
        simulate = ert.ERTModelling(sr=False)
        simulate.setMesh(self.mesh)
        simulate.data = self.__activate_data()
        simulate.setRegionProperties(1, background=True)
        # reassigning global variable
        self.__sim = simulate

        print("Starting Inversions ...")
        trans_log = pg.trans.TransLog()
        calc_inversion = pg.Inversion(fop=simulate, verbose=True)
        calc_inversion.transData = trans_log
        calc_inversion.transModel = trans_log

        true_resistivity = calc_inversion.run(self.__data_tr['rhoa'], self.__data_tr['err'], lam=20)
        self.__tr_res = true_resistivity

        return pg.show(simulate.paraDomain, true_resistivity, colorBar=True, cMap="Spectral_r",
                       cMin=8, cMax=1500, label=pg.unit('res'))

    def plot_inverse(self, min_res=8, max_res=1500):
        """print and edit the inverse_simulation Image.

        parameters
        ---------
        min_res: The lowest resistivity values based on the simulation
        max_res: The highest resistivity values based on the simulation
        """
        return pg.show(self.__sim.paraDomain, self.__tr_res, colorBar=True, cMap="Spectral_r",
                       cMin=min_res, cMax=max_res, label=pg.unit('res'))
