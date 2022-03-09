"""importing dependency modules."""
import os
import numpy as np
import pybert as pb
import pygimli as pg


def supersting_processing(file, row=1, col=[-4, -1], savefile=False):
    """Read in the supersting file and extract the measured resistivity values and electrodes arrangement.

    The Supersting file has a standard output format. The total number of records measured is situated at
    the end of the second row.

    The supersting_processing function returns the following in an array: resistance, apparent resistivity,
    current electrodes(xyz), and potential electrodes(xyz), from the supersting file.

    Depending on the information you need, you might just need to slightly adjust some parameters to get
    what you need. See the SuperSting Manual for column positions of information needed.

    Dependence: os, numpy
    Parameters: file- The name of the file should be in the current directory or the path should be added.
                row- The row shouldn't change except in case of special cases.
                col- The default used is hundreds of points. if the record is not up to hundred,
                change to [-3, -1], if total points are up to a thousand, change to [-5:-1].
                savefile- boolean. To save the file, change the parameter to True to save as .txt.
    """
    if not os.path.isfile(file):
        raise ValueError("{} does not exist, make sure file is in the same directory".format(file))

    with open(file, 'r') as f:
        supersting_file = f.readlines()

    if type(int(supersting_file[row][col[0]:col[1]])) not in [int]:
        raise ValueError('Please make sure you enter the correct col position')

    record = int(supersting_file[row][col[0]:col[1]])

    # remove the header
    supersting = supersting_file[3:]

    # The position of the resistance, resistivity and the ABMN(xyz for each):
    relevant_col = [4, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]

    # create the numpy array size to accommodate the resistance, resistivity and ABMN files
    data = np.ones((record, len(relevant_col)))

    # extract each line of the supersting file and separate each information. filling the array
    for i in range(len(supersting)):
        line = supersting[i].replace(',', " ").split()
        for j in range(len(relevant_col)):
            data[i][j] = line[relevant_col[j]]

    if savefile == True:
        np.savetxt("Resistivity.dat", data, header='R rhoa A(xyz) B(xyz) M(xyz) N(xyz)')

    return data


def standardized_4BERT(file_name, precision=2, save_file=False):
    """The Standardized_4Bert function returns the required data needed for the BERT model.

    Dependencies: numpy, pybert, pygimli
    Parameters: file_name- The supersting input file.
                precision- default is set to 2. It is used to create the pseudo data used for inversion.
                savefile- boolean. To save the file, change the parameter to True to save as .txt.

    The output consist of the topography and the ABMN electrode position with the apparent resistivity.
    """
    if not os.path.isfile(file_name):
    	raise ValueError("{} does not exist, make sure file is in the same directory".format(file_name))
	
    processed_file = supersting_processing(file_name)
    # extract the xyz positions of the array and stack them vertically
    Apos = processed_file[:, 2:5]
    Bpos = processed_file[:, 5:8]
    Mpos = processed_file[:, 8:11]
    Npos = processed_file[:, 11:14]

    electrode_pos = np.vstack((Apos, Bpos, Mpos, Npos))

    # rounds the floats in the array to the nearest integer tending to zero
    pseudo_data = 100 ** precision
    datafix = np.fix(electrode_pos * pseudo_data) / pseudo_data + 0.0

    # gets the actual electrodes numbering of the ABMN electrodes and create synthetic data.
    dtype = np.dtype((np.void, datafix.dtype.itemsize * datafix.shape[1]))
    byte = np.ascontiguousarray(datafix).view(dtype)
    _, ia = np.unique(byte, return_index=True)
    _, ib = np.unique(byte, return_inverse=True)

    # get electrode configuration and obtain the forward and reverse index
    org_pos = np.unique(byte).view(datafix.dtype).reshape(-1, datafix.shape[1])
    fwd_ind, rev_ind = ia, ib

    # create an instance of the pybert DataContainerERT
    data = pg.DataContainerERT()
    for ipos in org_pos:
        data.createSensor(ipos)

    # Add more information from the supersting file
    all_info = np.genfromtxt(file_name, delimiter=',', skip_header=3)

    data.resize(len(all_info))
    ABMN = rev_ind.reshape(4, -1).T

    for i, abmn in enumerate(ABMN):
        ind = [int(ii) for ii in abmn]
        data.createFourPointData(i, *ind)  # ind[1], ind[0], ind[2], ind[3])

    data.set('i', all_info[:, 6] * 1e-3)
    data.set('u', all_info[:, 4] * data('i'))  # U=R*I
    data.set('err', all_info[:, 5] * 0.001)
    data.set('rhoa', all_info[:, 7])
    if all_info.shape[1] > 30:
        data.set('ip', all_info[:, 30] * 1000)  # M integrated in msec
        for i in range(6):
            data.set('ip' + str(i + 1), all_info[:, 24 + i])

    data.markValid(data('rhoa') > 0)
    data.checkDataValidity()
    data.sortSensorsX()

    # save the file in .dat format and can be visualized using notepad or any text application.
    if save_file == True:
        pb.exportData(data, 'supersting.dat')

    return data
