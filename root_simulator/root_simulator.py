"""Importing the pygimli and pybert module."""
import pygimli as pg
import pybert as pb


class RootSimulator():
	"""The Root simulator utilizes the forward and inversion simulations of the BERT module for Root Depth analysis.

	The functionality of this software requires a 2D array. Import the data using the read_res_data module.
	The data utilized for the project is the SuperSting AGI electrical resistivity meter. To use other data format see the BERT 
	documentation.

	----------------------------------
	Dependables: numpy, matplolib, pygimli, pybert
	Parameters
	----------
	data - Processed SuperSting file containing the electrodes configuration and the estimated apparent resistivity.

	Usage:
	import pygimli, pybert

	RT = RootSimulator(data).
	"""

	def __init__(self, data):
		"""Read in the array, arr.

		The parameter, arr is a 2D array...
		"""
		self.data = data


	def resistivity_plot(self):
		"""Plot the resistivity range across number of stations measured in 1D.

		resistivity_plot provides a visulization of the general resistivity variability in the field measured."""
		pass


	def inversion2D(self):
		pass


	def forward_model(self):
		pass


	def animate_simulation(self):
		"""Simulate several conditions of the Tomography imagery.

		The animate_simulation function provides a series of iteration on the individual generated tomography
		which returns a virtual representaion detailed changes in events in time

		Dependence: 
		Parameters:
		-----------


		"""
		pass
