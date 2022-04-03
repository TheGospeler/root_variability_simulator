"""Import Dependency"""
from copy import copy
import numpy as np


class ElectrodeScheme():
    """Modify the supersting.dat file to desired specifications.

    The ElectrodeScheme reads in the *.dat file and return a new .dat file with the desired
    electrode configuration. The class has functions that can modify the inherit electrode
    configuration to other allowable configurations that allows the user to perform simulations
    with known or hypothetical resistivity values in evaluating the sensitivity of similar electrode
    configuration.

    Dependable: numpy, read_res_data.
    Parameter: data- The data should be the output from the standardized_bert function in the
    read_res_data package.

    Functions:
    -----------
    extract_electrode.
    get_electrode_conf.
    modify_electrode.

    Attributes:
    array_name: Displays the electrode configuration present in the input dataset.
    """

    def __init__(self, data):
        """Accept the *.dat data file, and initializes global variables."""
        self.data = data
        self.compiled_data = []
        self.data_without_electr = []
        self.electr_data = []
        self.array_name = "Call get_array_name"
        self.curr_a = "Call extract_electrode() or modify_electrode()"  # current A electrode
        self.curr_b = "Call extract_electrode() or modify_electrode()"  # current B electrode
        self.pot_m = "Call extract_electrode() or modify_electrode()"  # Potential M electrode
        self.pot_n = "Call extract_electrode() or modify_electrode()"  # Potential N electrode
        self.modify_output = "Call the modify_electrodes()"

    def extract_electrode(self, save_file=False):
        """Read the .dat file and return a new file with the electrode configuration data.

        The .dat file contains several other information contained in the data info section,
        and for the forward modeling, where we want to perform certain simulations; we want
        to simulate the electrode configuration with the actual or synthetic resistivity data.
        The extract_electrode function helps isolate the electrode configuration from the .dat
        file and return a new file while still maintaining the bert structure of the input data.

        Parameter:
               save_file: Boolean. You can choose to save the file or perform other operation,
               using the other functions before saving.

        returns:
               A list, structured in the similitude of the saved file."""
        with open(self.data, 'r', encoding='utf-8') as files:
            file = files.readlines()

        # compiled_data holds all the information in the extract_electrodes
        self.compiled_data = []

        sensor = int(file[0].split()[0])
        self.compiled_data.append(str(sensor) + '\n')

        sensor_header = file[1]
        self.compiled_data.append(sensor_header)

        sensor_info = np.loadtxt(self.data, skiprows=2, max_rows=sensor)
        for sen in sensor_info.tolist():
            self.compiled_data.append(f'{sen[0]} {sen[1]} {sen[2]}\n')

        data_num = file[sensor + 2]
        self.compiled_data.append(data_num)

        data_header = file[sensor + 3][:9] + '\n'  # only interested in the a b m n
        self.compiled_data.append(data_header)

        # The data_without_electr contains all the data except electr_data.
        # This is useful, as the manipulated electrode configuration can be easily attached to it.
        self.data_without_electr = copy(self.compiled_data)

        self.electr_data = np.loadtxt(self.data, skiprows=sensor + 3,
                                      max_rows=int(data_num))[:, :4]

        # unpack the first row to identify the electrode configuration.
        # curr_a1, curr_b1 represents the current A and B electrodes, and, pot_m1, pot_n1
        # represent the potential M and N, electrodes.
        curr_a1, curr_b1 = self.electr_data[0, 0], self.electr_data[0, 1]
        pot_m1, pot_n1 = self.electr_data[0, 2], self.electr_data[0, 3]

        self.curr_a, self.curr_b = self.electr_data[:, 0], self.electr_data[:, 1]
        self.pot_m, self.pot_n = self.electr_data[:, 2], self.electr_data[:, 3]

        # Get the name of the array
        if pot_m1 - curr_a1 == pot_n1 - pot_m1 == curr_b1 - pot_n1:
            self.array_name = 'Wenner Alpha'

        elif curr_a1 - curr_b1 == pot_m1 - curr_a1 == pot_n1 - pot_m1:
            self.array_name = 'Wenner Beta'

        elif pot_m1 - curr_a1 == curr_b1 - pot_m1 == pot_n1 - curr_b1:
            self.array_name = 'Wenner Gamma'

        elif curr_a1 - curr_b1 == pot_n1 - pot_m1 and pot_m1 - curr_b1 == pot_n1 - curr_a1:
            self.array_name = 'Dipole-Dipole'

        elif pot_n1 - curr_a1 == curr_b1 - pot_m1 and pot_m1 - curr_a1 == curr_b1 - pot_n1:
            self.array_name = 'Schlumberger'

        else:
            self.array_name = 'Cannot identify array'

        # append the new sorted array configuration in the list
        for dat in self.electr_data.tolist():
            self.compiled_data.append(f'{dat[0]} {dat[1]} {dat[2]} {dat[3]}\n')

        if save_file:
            with open(f'{self.data[:-4]}.shm', 'w', encoding='utf-8') as files:
                for line in self.compiled_data:
                    files.write(line)

        return self.compiled_data

    def get_electrode_conf(self):
        """Return the electrode configuration present in the input data."""

        # activate the extract_electrode to get all the attributes needed.
        __activate_arr = self.extract_electrode()

        return self.array_name

    def __save_modification(self, name, specified_data):
        """Save the file in present directory if the user chooses to save file.

        This is a private function that helps reduces unnecessarily length of the codes, since
        I will be using the same structure for the different boolean construct.
        """
        save_new_file = input('Do you want to save file? Y/N: ')
        if save_new_file.upper() == 'Y':
            with open(f'{self.data[:-4]}_{name}_arr.shm', 'w', encoding='utf-8') as files:
                for line in specified_data:
                    files.write(line)

    def modify_electrode(self):
        """Modify the inherit array if change of array positions are possible.

        Based on the the electrode configuration existing in the Electrical Resistivity Geophysical
        Techniques, the Wenner Configurations are the only array that can be interchanged because
        the electrode spacing are the same, while the others are not.

        This is not an easy modification as it requires critical thinking. The modification must
        not change the bert perception as arranging the the electrode configuration as A, B, M, N.
        """
        # activate the extract_electrode to get all the attributes needed.
        __activate_arr = self.extract_electrode()

        if self.array_name == "Wenner Alpha":
            print("The array configuration is Wenner Alpha, and can be modified to Beta or Gamma")
            choice = input("Enter 'B' to modify to Wenner Beta or 'G' to modify to Wenner Gamma: ")

            if choice.upper() == 'B':
                beta_electr_data = np.vstack([self.pot_m, self.curr_a, self.pot_n, self.curr_b]).T

                # make a duplicate copy of the data_without_electr
                beta_data = copy(self.data_without_electr)

                for line in beta_electr_data.tolist():
                    beta_data.append(f'{line[0]} {line[1]} {line[2]} {line[3]}\n')
                self.__save_modification('beta', beta_data)

                # Modify_electrodes returns this option if selected
                self.modify_output = beta_data

            elif choice.upper() == 'G':
                gamma_electr_data = np.vstack([self.curr_a, self.pot_n, self.pot_m, self.curr_b]).T

                # make a duplicate copy of the data_without_electr
                gamma_data = copy(self.data_without_electr)

                for line in gamma_electr_data.tolist():
                    gamma_data.append(f'{line[0]} {line[1]} {line[2]} {line[3]}\n')
                self.__save_modification('gamma', gamma_data)

                # Modify_electrodes returns this option if selected
                self.modify_output = gamma_data

            else:
                print('You entered a wrong letter... printing out the sensor information only')

        elif self.array_name == "Wenner Beta":
            print("The array configuration is Wenner Beta, and can be modified to Alpha or Gamma")
            choice = input("Enter 'A' to modify to Wenner Alpha or 'G' to modify to Wenner Gamma: ")

            if choice.upper() == 'A':
                alpha_electr_data = np.vstack([self.curr_b, self.pot_n, self.curr_a, self.pot_m]).T

                # make a duplicate copy of the data_without_electr
                alpha_data = copy(self.data_without_electr)

                for line in alpha_electr_data.tolist():
                    alpha_data.append(f'{line[0]} {line[1]} {line[2]} {line[3]}\n')
                self.__save_modification('alpha', alpha_data)

                # Modify_electrodes returns this option if selected
                self.modify_output = alpha_data

            elif choice.upper() == 'G':
                gamma_electr_data = np.vstack([self.curr_b, self.pot_m, self.curr_a, self.pot_n]).T

                # make a duplicate copy of the data_without_electr
                gamma_data = copy(self.data_without_electr)

                for line in gamma_electr_data.tolist():
                    gamma_data.append(f'{line[0]} {line[1]} {line[2]} {line[3]}\n')
                self.__save_modification('gamma', gamma_data)

                # Modify_electrodes returns this option if selected
                self.modify_output = gamma_data

            else:
                print('You entered a wrong letter... printing out the sensor information only')

        elif self.array_name == "Wenner Gamma":
            print("The array configuration is Wenner Gamma, and can be modified to  Alpha or Beta")
            choice = input("Enter 'A' to modify to Wenner Alpha or 'B' to modify to Wenner Beta: ")

            if choice.upper() == 'A':
                alpha_electr_data = np.vstack([self.curr_a, self.pot_n, self.pot_m, self.curr_b]).T

                # make a duplicate copy of the data_without_electr
                alpha_data = copy(self.data_without_electr)

                for line in alpha_electr_data.tolist():
                    alpha_data.append(f'{line[0]} {line[1]} {line[2]} {line[3]}\n')
                self.__save_modification('alpha', alpha_data)

                # Modify_electrodes returns this option if selected
                self.modify_output = alpha_data

            elif choice.upper() == 'B':
                beta_electr_data = np.vstack([self.pot_m, self.curr_a, self.curr_b, self.pot_n]).T

                # make a duplicate copy of the data_without_electr
                beta_data = copy(self.data_without_electr)

                for line in beta_electr_data.tolist():
                    beta_data.append(f'{line[0]} {line[1]} {line[2]} {line[3]}\n')
                self.__save_modification('beta', beta_data)

                # Modify_electrodes returns this option if selected
                self.modify_output = beta_data

            else:
                print('You entered a wrong letter... printing out the sensor information only')

        elif self.array_name in ["Schlumberger", "Dipole-Dipole"]:
            print(f"The array configuration is {self.array_name}, hence due to the complexity of"
                  " the electrodes configuration, a modification cannot be done")

        return self.modify_output
