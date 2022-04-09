"""Import dependent modules."""

import os
from pygimli.physics import ert
from IPython.display import HTML, clear_output
import imageio
import matplotlib.pyplot as plt
import numpy as np
import pygimli as pg
import pygimli.meshtools as mt


class RootSimulator:
    """The Root simulator simulates the spatial distribution of tree roots at the subsurface.

    The RootSimulator class contains functions that enables the simulations of the subsurface to
    access the spatial variability of roots using created synthetic data to simulate the model
      accuracy and to create Electrical Resistivity Tomography (ERT).
    This package makes use of the python library for Geophysical modeling and Inversion (pyGIMLi).

    Dependable: numpy, matplotlib, pygimli.
    Functions
    ----------
    create_geom- creates an arbitrary region of the subsurface with a specific feature.
    forward_model - simulates the resistivity distribution within the created mesh.
    inversion_2D - performs simulations and return the true resistivity model.
    animate_simulation- visualizes the results of the different array configuration.

    Usage:
    from root_simulator import RootSimulator

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
        # Check for errors in input parameter.

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

        parameter:
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
        the model performance with the known structure or layers under consideration, using such
        information to measure the performance with real data with unknown structures.
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
