import re, datetime, os, subprocess

dirpath = os.getcwd()

input_file = "SpillTool.dat"

exe_dir = (dirpath+"//exe")
mohid_log = (exe_dir+"//Mohid.log")

data_dir = (dirpath+"//data")
file_lagrangian = "Lagrangian_1.dat"

#Define number of solutions
number_of_solutions = 1

#Define hydrodynamic solutions directory
solution_dir_file = [0]*number_of_solutions
#solution_dir_file [0] = ["F:\MOHID\Babitonga\Backup\Level_1", "Hydrodynamic_2_Surface.hdf5"]
#solution_dir_file [1] = ["F:\MOHID\CEP\Backup\Level_1", "Hydrodynamic_2_Surface.hdf5"]
#solution_dir_file [2] = ["F:\MOHID\PR_SC\Backup\Level_2", "Hydrodynamic_2_Surface.hdf5"]
#solution_dir_file [3] = ["F:\MOHID\Plataforma_SE\Backup\Level_1", "Hydrodynamic_2_Surface.hdf5"]
#solution_dir_file [0] = ["F:\CMEMS\Brasil", "CMEMS.hdf5"]
solution_dir_file [0] = [r"D:\CMEMS\GLOBAL_ANALYSIS_FORECAST_PHY_SA\Backup", "CMEMS_SA.hdf5"]

meteo_dir = (r"D:\GFS\Backup")
file_name_meteo = "gfs.hdf5"


#####################################################
def read_input():
	global initial_date
	global end_date
	global number_of_days
	global emission_temporal
	global lon, lat
	
	with open(input_file) as file:
		for line in file:
			if re.search("^START.+:", line):
				words = line.split()
				initial_date = datetime.datetime(int(words[2]),int(words[3]),int(words[4]),int(words[5]))
			elif re.search("^END.+:", line):
				words = line.split()
				end_date = datetime.datetime(int(words[2]),int(words[3]),int(words[4]),int(words[5]))
			elif re.search("^EMISSION_TEMPORAL.+:", line):
				words = line.split()
				emission_temporal = words[2]
			elif re.search("^POSITION_COORDINATES.+:", line):
				words = line.split()
				lon = words[2]
				lat = words[3]
				
	interval = end_date - initial_date
		
	number_of_days = interval.days
#####################################################
def write_date():
	
	os.chdir(data_dir)
	file_name = "Model_1.dat"
	
	with open(file_name) as file:
		file_lines = file.readlines()
		
	number_of_lines = len(file_lines)
	
	for n in range(0,number_of_lines):
		line = file_lines[n]		
		if re.search("^START.+:", line):
			file_lines[n] = "START " + ": " + str(initial_date.strftime("%Y %m %d %H ")) + "0 0\n"

		elif re.search("^END.+:", line):
			file_lines[n] = "END " + ": " + str(end_date.strftime("%Y %m %d %H ")) + "0 0\n"
			
	with open(file_name,"w") as file:
		for n in range(0,number_of_lines) :
			file.write(file_lines[n])

#####################################################
def write_lagrangian():
	
	os.chdir(data_dir)
	
	with open(file_lagrangian) as file:
		file_lines = file.readlines()
		
	number_of_lines = len(file_lines)
	
	for n in range(0,number_of_lines):
		line = file_lines[n]		
		if re.search("^START_PARTIC_EMIT.+:", line):
			file_lines[n] = "START_PARTIC_EMIT " + ": " + str(initial_date.strftime("%Y %m %d %H ")) + "0 0\n"

		elif re.search("^STOP_PARTIC_EMIT.+:", line):
			file_lines[n] = "STOP_PARTIC_EMIT " + ": " + str(end_date.strftime("%Y %m %d %H ")) + "0 0\n"
			
		elif re.search("^EMISSION_TEMPORAL.+:", line):
			file_lines[n] = "EMISSION_TEMPORAL " + ": " + emission_temporal + "\n"
			
		elif re.search("^POSITION_COORDINATES.+:", line):
			file_lines[n] = "POSITION_COORDINATES " + ": " + lon + " " + lat + "\n"
		
		elif re.search("^NBR_PARTIC.+:", line):
			if emission_temporal == "Continuous" :
				file_lines[n] = "NBR_PARTIC " + ": 1" + "\n"
			elif emission_temporal == "Instantaneous" :
				file_lines[n] = "NBR_PARTIC " + ": 100" + "\n"
		elif re.search("^<EndOrigin>", line):
			end_line = n 
			
	with open(file_lagrangian,"w") as file:
		for n in range(0,end_line+1) :
			file.write(file_lines[n])
		
		
	write_meteo_ocean()
		
#####################################################
def write_meteo_ocean():
	property_name = ["velocity U", "velocity V"]
	with open(file_lagrangian,"a") as file:
		file.write ("\n<BeginMeteoOcean>\n")
		for property in range(0,len(property_name)):
			file.write ("<<BeginProperty>>\nNAME : " + property_name[property] +"\nDESCRIPTION : velocity from operational models\nUNITS : m/s\nMASK_DIM : -99\nFILE_LIST_MODE : 1\n")
			for n in range(0,number_of_solutions):
				file.write("<<<BeginMeteoOceanFiles>>>\n")
				for i in range (0,number_of_days):
					next_initial_date = initial_date + datetime.timedelta(days = i)
					next_end_date = initial_date + datetime.timedelta(days = i+1)
					file.write(solution_dir_file[n][0] + "/" + str(next_initial_date.strftime("%Y%m%d")) + "_" + str(next_end_date.strftime("%Y%m%d") + "/" + solution_dir_file[n][1] + "\n"))
				file.write("<<<EndMeteoOceanFiles>>>\n")
			file.write("<<EndProperty>>\n")
	
	property_name = ["wind velocity X", "wind velocity Y"]
	with open(file_lagrangian,"a") as file:
		for property in range(0,len(property_name)):
			file.write ("<<BeginProperty>>\nNAME : " + property_name[property] +"\nDESCRIPTION : wind from operational models\nUNITS : m/s\nMASK_DIM : -99\nFILE_LIST_MODE : 0\n")
			file.write("<<<BeginMeteoOceanFiles>>>\n")
			for i in range (0,number_of_days):
				next_initial_date = initial_date + datetime.timedelta(days = i)
				next_end_date = initial_date + datetime.timedelta(days = i+1)
				file.write(meteo_dir + "/" + str(next_initial_date.strftime("%Y%m%d")) + "_" + str(next_end_date.strftime("%Y%m%d") + "/" + file_name_meteo + "\n"))
			file.write("<<<EndMeteoOceanFiles>>>\n")
			file.write("<<EndProperty>>\n")
		file.write ("<EndMeteoOcean>")
#####################################################

read_input()
write_date()
write_lagrangian()
os.chdir(exe_dir)
output = subprocess.call(["run.bat"])