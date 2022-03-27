"""Import Dependency"""
import numpy as np


class ElectrodeScheme:
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
        self.to_save = []
        self.before_data_info = []
        self.data_info = []
        self.array_name = ""
        self.curr_a = ""  # current A electrode
        self.curr_b = ""  # current B electrode
        self.pot_m = ""  # Potential M electrode
        self.pot_n = ""  # Potential N electrode

    def extract_electrode(self, save_file=True):
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

        sensor = int(file[0].split()[0])
        self.to_save.append(str(sensor) + '\n')

        sensor_header = file[1]
        self.to_save.append(sensor_header)

        sensor_info = np.loadtxt(self.data, skiprows=2, max_rows=sensor)
        for sen in sensor_info.tolist():
            self.to_save.append(f'{sen[0]} {sen[1]} {sen[2]}\n')

        data_num = file[sensor + 2]
        self.to_save.append(data_num)

        data_header = file[sensor + 3][:9] + '\n'  # only interested in the a b m n
        self.to_save.append(data_header)

        # The before_data_info contains all the information before the addition of the data_info.
        # This is useful, as the manipulated electrode configuration can be easily attached to it.
        for line in self.to_save:
            self.before_data_info.append(line)

        self.data_info = np.loadtxt('supersting.dat', skiprows=sensor + 3,
                                    max_rows=int(data_num))[:, :4]

        # unpack the first row to identify the electrode configuration.
        # cur_1, cur_2 represents the current A and B electrodes, and, pot_1, pot_2 represent the
        # potential M and N, electrodes.
        cur_1, cur_2, pot_1 = self.data_info[0, 0], self.data_info[0, 1], self.data_info[0, 2]
        pot_2 = self.data_info[0, 3]

        self.curr_a, self.curr_b = self.data_info[:, 0], self.data_info[:, 1]
        self.pot_m, self.pot_n = self.data_info[:, 2], self.data_info[:, 3]

        # Get the name of the array
        if cur_2 < cur_1 < pot_1 < pot_2 and cur_1 - cur_2 != pot_1 - cur_1:
            self.array_name = 'Dipole-Dipole'

        if cur_1 < cur_2 and cur_2 > pot_1 and pot_1 < pot_2 and pot_1 - cur_1 != pot_2 - pot_1:
            self.array_name = 'Schlumberger'

        if cur_1 < cur_2 and cur_2 > pot_1 and pot_1 < pot_2:
            self.array_name = 'Wenner Alpha'

        if cur_2 < cur_1 < pot_1 < pot_2:
            self.array_name = 'Wenner Beta'

        if cur_1 < pot_1 < cur_2 < pot_2:
            self.array_name = 'Wenner Gamma'

        # append the new sorted array configuration in the list
        for dat in self.data_info.tolist():
            self.to_save.append(f'{dat[0]} {dat[1]} {dat[2]} {dat[3]}\n')

        if save_file:
            with open(f'{self.data[:-4]}_electrodes.dat', 'w', encoding='utf-8') as files:
                for line in self.to_save:
                    files.write(line)

        return self.to_save

    def get_electrode_conf(self):
        """Return the electrode configuration present in the input data."""
        return self.array_name

    def __save_modification(self):
        """Save the file in present directory if the user chooses to save file.

        This is a private function that helps reduces unnecessarily length of the codes, since
        I will be using the same structure for the different boolean construct.
        """
        save_new_file = input('Do you want to save file? Y/N: ')
        if save_new_file.upper() == 'Y':
            with open(f'{self.data[:-4]}_mod_electrodes.dat', 'w', encoding='utf-8') as files:
                for line in self.before_data_info:
                    files.write(line)

    def modify_electrode(self):
        """Modify the inherit array if change of array positions are possible.

        Based on the the electrode configuration existing in the Electrical Resistivity Geophysical
        Techniques, the Wenner Configurations are the only array that can be interchanged because
        the electrode spacing are the same, while the others are not.

        This is not an easy modification as it requires critical thinking. The modification must
        not change the bert perception as arranging the the electrode configuration as A, B, M, N.
        """
        if self.array_name == "Wenner Alpha":
            print("The array configuration is Wenner Alpha, and can be modified to Beta or Gamma")
            choice = input("Enter 'B' to modify to Wenner Beta or 'G' to modify to Wenner Gamma: ")

            if choice.upper() == 'B':
                beta_data_info = np.vstack([self.curr_b, self.curr_a, self.pot_m, self.pot_n]).T

                for line in beta_data_info.tolist():
                    self.before_data_info.append(f'{line[0]} {line[1]} {line[2]} {line[3]}\n')
                self.__save_modification()

            elif choice.upper() == 'G':
                gamma_data_info = np.vstack([self.curr_a, self.pot_m, self.curr_b, self.pot_n]).T

                for line in gamma_data_info.tolist():
                    self.before_data_info.append(f'{line[0]} {line[1]} {line[2]} {line[3]}\n')
                self.__save_modification()

            else:
                print('You entered a wrong letter... printing out the sensor information only')

        elif self.array_name == "Wenner Beta":
            print("The array configuration is Wenner Beta, and can be modified to Alpha or Gamma")
            choice = input("Enter 'A' to modify to Wenner Alpha or 'G' to modify to Wenner Gamma: ")

            if choice.upper() == 'A':
                alpha_data_info = np.vstack([self.curr_b, self.pot_m, self.pot_n, self.curr_a]).T

                for line in alpha_data_info.tolist():
                    self.before_data_info.append(f'{line[0]} {line[1]} {line[2]} {line[3]}\n')
                self.__save_modification()

            elif choice.upper() == 'G':
                gamma_data_info = np.vstack([self.curr_b, self.pot_m, self.curr_a, self.pot_n]).T

                for line in gamma_data_info.tolist():
                    self.before_data_info.append(f'{line[0]} {line[1]} {line[2]} {line[3]}\n')
                self.__save_modification()

            else:
                print('You entered a wrong letter... printing out the sensor information only')

        elif self.array_name == "Wenner Gamma":
            print("The array configuration is Wenner Gamma, and can be modified to  Alpha or Beta")
            choice = input("Enter 'A' to modify to Wenner Alpha or 'B' to modify to Wenner Gamma: ")

            if choice.upper() == 'A':
                alpha_data_info = np.vstack([self.curr_a, self.pot_m, self.pot_n, self.curr_b]).T

                for line in alpha_data_info.tolist():
                    self.before_data_info.append(f'{line[0]} {line[1]} {line[2]} {line[3]}\n')
                self.__save_modification()

            elif choice.upper() == 'B':
                beta_data_info = np.vstack([self.curr_b, self.curr_a, self.pot_m, self.pot_n]).T

                for line in beta_data_info.tolist():
                    self.before_data_info.append(f'{line[0]} {line[1]} {line[2]} {line[3]}\n')
                self.__save_modification()

            else:
                print('You entered a wrong letter... printing out the sensor information only')

        elif self.array_name in ["Schlumberger", "Dipole-Dipole"]:
            print(f"The array configuration is {self.array_name}, hence due to the complexity of"
                  " the electrodes configuration, a modification cannot be done")

        return self.before_data_info
