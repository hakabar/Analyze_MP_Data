"""
This script works with a subset of experiments located in the IN_PATH folder of the ExpMetaData.yaml file.
It will check our initial filter condition (there must be an increase in the insects activity when the CO2 is released (compared to the initial AIR activity))

"""
import sys
import glob
import yaml
from Exp_Info import Exp_Info
import numpy as np
import h5py
import matplotlib.pyplot as plt 
import time
import pathlib



def find_files_list(path, ext):
	""" Find all exp configuration files (.yaml files) in folder. They are needed to load their corresponding h5 files later
	"""
	return glob.glob(path+'/*'+ext)


def load_metaData():
	""" Load constant values related to the experiment setup and workspaces
	"""
	try: 
		print(pathlib.Path().absolute())
		metaFile= 'ExpMetaData.yaml'
		with open(metaFile, 'r') as f:
			metaData= yaml.load(f, Loader=yaml.FullLoader)
		print(' Experiments metadata loaded sucessfuly')
		return metaData
	except Exception as e:
		print(' ERROR while loading experiment metaData from: %s'%metaFile)
		print(e)
		sys.exit(1)


def load_expConfig_only(fname, metaData):
	""" Load the configuration settings of an experiment and its data from FLydra
	"""
	try: 
		with open(fname, 'r') as f:
			#dataMap= Exp_Info.Exp_Info(yaml.load(f))
			dataMap= Exp_Info(yaml.load(f, Loader=yaml.FullLoader))
			print(' Configuration settings for experiment on %s loaded sucessfuly'%dataMap.expDate)
		return dataMap
	except: 
		print(' ERROR while loading experiment configuration settings for file: %s'%fname)


def load_exp_data(exp, metaData):
	""" Load the data from FLydra for a given experiment
	"""
	try:
		hf=h5py.File(metaData['IN_PATH']+exp.fileName, 'r')
		#print('file %s loaded'%fname )
		dataset= hf.get(metaData['DATASET'])
		dataset= np.array(dataset)
		#Add the obj_ID, frame, x, y, z and ts to exp
		exp.set_h5_information(dataset['obj_id'], dataset['frame'], dataset['timestamp'], dataset['x'], dataset['y'], dataset['z'])
		#Clean the data outside the startExp and endExp
		exp.apply_start_end_ts()
		#Remove points outside volume
		exp.erase_pos_outside_wt(metaData)
		#set the odor stimulus used in each par of the experiment
		exp.set_odor_stim()
		print(' Experiment %s data loaded'%exp.fileName)
	except:
		print(' ERROR while loading data for file: %s'%exp.fileName)


def get_trajectory_duration(trajTime):
	""" Calculate the time duration of the trajectory
	"""
	return np.max(trajTime) - np.min(trajTime)


def estimate_flight_activity(exp, trajTimeFilter):
	""" Estimate the flight activity when an odor is being released
	"""
	trajsDuration= []
	trajsCounted= []
	for odorValue in range(1,4):
		totalDurationFlights= 0
		totalTraj= 0
		#Select indexes for each of the 3 odor sections (1=AIR, 2=CO2, 3=PostCO2)
		odorIxs= np.where(exp.stim_List== odorValue)
		for id in np.unique(exp.ID_List[odorIxs]):
			#Find indexes related to this trajectory ID
			idIxs= np.where(exp.ID_List[odorIxs])
			#Get trajectory duration
			duration= get_trajectory_duration(exp.TS_List[odorIxs][idIxs])
			#Estimate overall activity for the given odor
			if duration >= trajTimeFilter:
				totalDurationFlights= totalDurationFlights + duration
				totalTraj= totalTraj+1
		trajsDuration.append(totalDurationFlights)
		trajsCounted.append(totalTraj)
	return trajsCounted, trajsDuration








# == MAIN ==
if __name__== '__main__':
	expList=[]
	#Load CONSTANTS related to the experiment
	expMetaData= load_metaData()
	#Find all the .yaml files (experiment cfg file) in folder
	filesList= find_files_list(expMetaData['IN_PATH'], '.yaml')
	
	# Load data from .yaml (experiment cfg file) and .h5 (exp raw data) files
	tmpX=[]
	tmpY= []
	tmpZ=[]
	tmpStim=[]
	for i, fname in enumerate(filesList):
		#t1=time.time()
		expList.append(load_expConfig_only(fname, expMetaData))
		if ('Pve' in expMetaData['GRP_BY']):
			# If the TEST Cue is in the POSITIVE Y axis, load the experiment and group it to the other exp with TEST Cue in similar position
			load_exp_data(expList[i], expMetaData)

			if ('-' in expList[i].posClrTEST[1]):
					expList[i].Y_List = expList[i].Y_List*(-1)

		elif ('Nve' in expMetaData['GRP_BY']):
			# If the TEST Cue is in the POSITIVE Y axis, load the experiment and group it to the other exp with TEST Cue in similar position
			load_exp_data(expList[i], expMetaData)

			if ('-' not in expList[i].posClrTEST[1]):
					expList[i].Y_List = expList[i].Y_List*(-1)
		expTrajs, expTrajDur= estimate_flight_activity(expList[i], expMetaData['MIN_FLIGHT_TIME'])

		# print("TRAJECTORY ACTIVITY ESTIMATION for %s"%expList[i].fileName)
		# print("	- AIR: %s 	- CO2: %s	- PostCO2: %s"%(expTrajDur[0]/expTrajDur[0],expTrajDur[1]/expTrajDur[0], expTrajDur[2]/expTrajDur[1] ))
		# print("	- Total traj counted for	- AIR: %s	- CO2:%s	- PostCO2:%s"%(expTrajs[0], expTrajs[1], expTrajs[2]))
		# print("	- Total traj duration for	- AIR: %s 	- CO2: %s	- PostCO2: %s"%(expTrajDur[0],expTrajDur[1], expTrajDur[2]))

		print("TRAJECTORY ACTIVITY ESTIMATION for %s"%expList[i].fileName)
		print("	- AIR: %s 	- CO2: %s	- PostCO2: %s"%(expTrajDur[0]/expTrajDur[0],expTrajDur[1]/expTrajDur[0], expTrajDur[2]/expTrajDur[1] ))
		print("	- Total traj counted for	- AIR: %s	- CO2:%s	- PostCO2:%s"%(expTrajs[0], expTrajs[1], expTrajs[2]))
		print("	- Total traj duration for	- AIR: %s 	- CO2: %s	- PostCO2: %s"%(expTrajDur[0],expTrajDur[1], expTrajDur[2]))
