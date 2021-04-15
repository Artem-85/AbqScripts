import os
import csv
import xlsxwriter as xw
import re
import png
import sys

##############################

class DataSet:

    fls_list = []

    mat_list = []

    mod_list = []

    inc_list = []

    plt_list = []

    __data_set__ = []

    def __init__(self,data_set):

        self.__data_set__ = data_set

        self.fls_list = self.__get_elements__('file')

        self.mat_list = self.__get_elements__('material')

        self.mod_list = self.__get_elements__('mode')

        self.inc_list = self.__get_elements__('increment')

        self.plt_list = self.__get_elements__('plot')

    def __get_subset__(self,key,filter):

        subset = []

        for data_entry in self.__data_set__:

            if data_entry[key] == filter:

                subset.append(data_entry)

        return subset

    def __get_elements__(self,key):

        elements = []

        for data_entry in self.__data_set__:

            if data_entry[key] not in elements:

                elements.append(data_entry[key])

        return elements

    def items(self,index=None):

        if index == None:

            return self.__data_set__

        else:

            return self.__data_set__[index]

    def get_files(self):

        return self.__get_elements__('file')

    def get_mats(self):

        return self.__get_elements__('material')

    def get_modes(self):

        return self.__get_elements__('mode')

    def get_incs(self):

        return self.__get_elements__('increment')

    def get_plots(self):

        return self.__get_elements__('plot')

##############################

class CSVData(DataSet):

    def __init__(self,csv_files):

        self.__get_data_set__(csv_files)

        self.fls_list = self.__get_elements__('file')

        self.mat_list = self.__get_elements__('material')

        self.mod_list = self.__get_elements__('mode')

        self.inc_list = self.__get_elements__('increment')

        self.plt_list = self.__get_elements__('plot')

    def __get_data_set__(self,csv_files):

        for csv_file in csv_files:

            file_dir,file_name = os.path.split(csv_file)

            with open(csv_file, 'rt', encoding='utf8') as f:

                reader = csv.reader(f, delimiter=';')
            
                data = list(reader)

                x_data = []

                y_data = []

                first = True

                for line in data:

                    if first: 
                        
                        max_mises = float(line[0].strip('$'))

                        max_node = float(line[1])

                        first = False

                    else:
                    
                        if line and (line[0].strip())[0] != '#':
                        
                            if not re.search('[a-zA-Z]+',str(line)):

                                x_data.append(float(line[0]))

                                y_data.append(float(line[1]))

                prefix,mat,mode,inc,study,plot = file_name[:-4].split('_',5)

                data_entry = {

                    'file': file_name,

                    'path': file_dir,

                    'x data': x_data,

                    'y data': y_data,

                    'prefix': prefix,
                    
                    'mode': mode,
                    
                    'material': mat,
                    
                    'increment': inc,

                    'study': study,
                    
                    'plot': plot,
                    
                    'max mises': max_mises,
                    
                    'max node': max_node }

                self.__data_set__.append(data_entry)

    def modes(self,filter):

        return ModeSubSet(self.__get_subset__('mode',filter))

##############################

class ModeSubSet(DataSet):

    def incs(self,filter):

        return IncSubSet(self.__get_subset__('increment',filter))

##############################

class IncSubSet(DataSet):

    def plots(self,filter):

        return PlotSubSet(self.__get_subset__('plot',filter))

##############################

class PlotSubSet(DataSet):

    def mats(self,filter):

        return MatSubSet(self.__get_subset__('material',filter))

##############################

class MatSubSet(DataSet):

    pass

##############################

shift_h = 10

shift_v = 0 #105

shift_c = 25

c0 = 10

cc0 = 0

ch_width = 600

ch_height = 400

if '.py' in sys.argv[-1]:

    print("Please provide the job template name\n")
    quit()

job_dir, job_template = os.path.split(sys.argv[-1]) #'UMAT-plast-validation'

csv_dir = job_dir + '/data_sets/'

if not os.path.isdir(csv_dir):

    if not os.path.exists(csv_dir):

        os.makedirs(csv_dir)
    
    else:

        # error_log("Delete the file called 'data_sets' from the working directory\n")
        print("Delete the file called 'data_sets' from the working directory\n")
        quit()

wkbook_name = job_template

workbook = xw.Workbook(csv_dir + wkbook_name + '.xlsx')

search_str = "^{}.+\.csv$".format(job_template)

files = [csv_dir + f_name for f_name in os.listdir(csv_dir) if re.search(r'{}'.format(search_str), f_name)]

csv_data = CSVData(files)

modes = csv_data.mod_list

modes.sort()

charts = []

header1_format = workbook.add_format({'bold': True, 'size':13})

header2_format = workbook.add_format({'bold': True, 'size':11})

for mode in modes:

    mod_data_set = csv_data.modes(mode)

    incs = (mod_data_set.get_incs())

    incs.sort()

    for inc in incs:

        inc_data_set = mod_data_set.incs(inc)

        plots = inc_data_set.get_plots()

        plots.sort()

        sheet_name = '_'.join((mode,inc))

        worksheet = workbook.add_worksheet(sheet_name)

        r = 0

        rc = 5

        shift_v = 0

        for plot in plots:

            worksheet.write(r, c0, plot, header1_format)

            plot_data_set = inc_data_set.plots(plot)

            mats = plot_data_set.get_mats()

            mats.sort()

            c = c0

            chart = workbook.add_chart({'type': 'scatter', 'subtype': 'straight'})

            for mat in mats:

                worksheet.write(r + 1, c, mat, header2_format)

                mat_data_set = plot_data_set.mats(mat)

                for job_data_set in mat_data_set.items():

                    max_mises = 'Maximum Mises stress: {} at node {}'.format(job_data_set['max mises'],job_data_set['max node'])

                    worksheet.write(r + 1, c + 2, max_mises, header2_format)

                    worksheet.write_column(r + 2, c, job_data_set['x data'])

                    worksheet.write_column(r + 2, c + 1, job_data_set['y data'])

                    # image_name = job_data_set['file'].replace('.odb','_max-mises.png')

                    image_name = job_data_set['path'].replace('/data_sets', '/maxmises/')
                    image_name += '_'.join((job_data_set['prefix'],mat,mode,inc,job_data_set['study']))
                    image_name += '_max-mises.png'

                    from PIL import Image

                    png = Image.open(image_name)

                    png.load() # required for png.split()

                    # print(png.getchannel('A'))

                    background = Image.new("RGB", png.size, (255, 255, 255))

                    # print(png.split())

                    # background.paste(png, mask = png.split()[3]) # 3 is the alpha channel
                    background.paste(png) # 3 is the alpha channel

                    background.save(image_name, 'PNG')

                    worksheet.insert_image(r + 5, c + 1, image_name, {'x_scale': 0.5, 'y_scale': 0.5})

                    len_x = len(job_data_set['x data'])

                    len_y = len(job_data_set['y data'])

                    chart.add_series({
                        'name': mat,
                        'categories': [sheet_name, r + 2, c, r + 2 + len_x, c],
                        'values': [sheet_name, r + 2, c + 1, r + 2 + len_y, c + 1],
                        })

                    shift_v = shift_v if shift_v > (len_x + 4) else len_x + 4

                    shift_v = shift_v if shift_v > 26 else 26

                    # print(shift_v)

                    c += shift_h

            x_title = "Deflection [mm]" if 'RF' in plot else "Rotation angle [rad]"

            y_title = "Reaction force [N]" if 'RF' in plot else "Reaction moment [N*m]"

            chart.set_title ({'name': plot})

            chart.set_x_axis({'name': x_title})

            chart.set_y_axis({'name': y_title})

            chart.set_size({'width': ch_width, 'height': ch_height})

            worksheet.insert_chart(rc, cc0, chart, {'x_offset': 0, 'y_offset': 0})

            r += shift_v

            rc += shift_c

workbook.close()

print("Success")