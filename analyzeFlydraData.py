
import sys
import glob
import yaml
from Exp_Info import Exp_Info
import numpy as np
import h5py
import matplotlib.pyplot as plt 
import time
import logging
import logging.config
# logging DEBUG: Detailed information, typically only when diagnosting problems
# logging INFO: COnfirmation that things are working as they should
# logging WARNING: An indication that something unexpected happened, or indicates a possible problem inthe near future 
#  (i.e. "disk space low"). The SW is still working as expected
# logging ERROR: Due to some more serious problem. The SW hasn't been able of performing some functions
# logging CRITICAL: A serious error, indicating that the SW itself may not continuing running


# == FCTS/METHODS ==

def load_log_config(configFile):
	with open(configFile,'r') as cf:
		logConfig= yaml.load(cf, Loader=yaml.FullLoader)
	logging.config.dictConfig(logConfig)
	logger= logging.getLogger(__name__)
	logger.info(' ***** New run ***** ')
	return  logger



def load_metaData():
	""" Load constant values related to the experiment setup and workspaces
	"""
	try: 
		metaFile= 'ExpMetaData.yaml'
		with open(metaFile, 'r') as f:
			metaData= yaml.load(f, Loader=yaml.FullLoader)
		logger.info(' Experiments metadata loaded sucessfuly')
		return metaData
	except:
		logger.exception(' ERROR while loading experiment metaData from: %s'%metaFile)
		sys.exit(1)


def find_files_list(path, ext):
	""" Find all exp configuration files (.yaml files) in folder. They are needed to load their corresponding h5 files later
	"""
	return glob.glob(path+'/*'+ext)


def load_file(fname, metaData):
	""" Load the configuration settings of an experiment and its data from FLydra
	"""
	try: 
		with open(fname, 'r') as f:
			#dataMap= Exp_Info.Exp_Info(yaml.load(f))
			dataMap= Exp_Info(yaml.load(f, Loader=yaml.FullLoader))
			logger.info(' Configuration settings for experiment on %s loaded sucessfuly'%dataMap.expDate)
			load_exp_data(dataMap, metaData)
		return dataMap
	except: 
		logger.exception(' ERROR while loading experiment configuration settings for file: %s'%fname)

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
		logger.info(' Experiment %s data loaded'%exp.fileName)
	except:
		logger.exception(' ERROR while loading data for file: %s'%exp.fileName)




# == MAIN ==
if __name__== '__main__':

	# Set the level of logging
	configF= 'logConfig.yaml'
	logger= load_log_config(configF)
	
	stt= time.time()
	expList=[]

	#Load CONSTANTS related to the experiment
	expMetaData= load_metaData()
	
	#Find all the .yaml files (experiment cfg file) in folder
	filesList= find_files_list(expMetaData['IN_PATH'], '.yaml')
	
	#Load data from .yaml (experiment cfg file) and .h5 (exp raw data) files
	for i, fname in enumerate(filesList):
		t1=time.time()
		#expData= load_file(path, fname)
		expList.append(load_file(fname, expMetaData))
		t2=time.time()
		#Plot heatmaps
		for opt in [1,2,3]:
			expList[i].generate_heatmap(opt, expMetaData)
		t3=time.time()
		logger.debug('  - Data loaded in %s seg - heatmaps generated in %s seg - total time %s'%(t2-t1,t3-t2, t3-t1))

# # For debugging
# 	expList.append(load_file(filesList[0], expMetaData))
# 	for opt in [1,2,3]:
# 		#expData.generate_heatmap(opt)
# 		expList[0].generate_heatmap(opt, expMetaData)
	end= time.time()
	logger.debug('All data Analyzed. time: %s'%(end-stt))