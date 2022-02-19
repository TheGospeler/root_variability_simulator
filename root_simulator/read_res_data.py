"""importing dependency modules."""
import numpy as np
import csv

def res_data(csv_file, header=0):
	"""Read in the csv file location.

	The csv_file should should contain the resistivity and the regional number or depth data, 
	and returns a 2D array of the file to be used in BERT module.

	Dependency: csv_format, csv, numpy module
	Parameters:
	csv_file --location of the csv file ending with '.csv'.The regional number should be in the first column and resistivity values on the second.

	header -- Replace 0 with 1 if file contain header


	For example, csv_file = '../res_data.csv' or 'res_data.csv' if file is in correct directory.
	"""
	res_data = csv.reader(open(csvfile, 'r'), delimiter=',', quotechar='"')
	rows = [row for row in res_data]

	rhomap = np.ones([len(rows)-header, 2])
	for line in rows:
		rhomap[line-header, 0] = rows[line][0]
		rhomap[line-header, 1] = rows[line][1]

	return rhomap