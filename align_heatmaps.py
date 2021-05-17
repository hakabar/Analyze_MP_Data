"""
Script to open different heatmaps and align them in funciton of the point selected on the image
"""
import sys
import glob
import yaml
from Exp_Info import Exp_Info
import numpy as np
import h5py
import matplotlib.pyplot as plt 



def load_metaData():
	""" Load constant values related to the experiment setup and workspaces
	"""
	try: 
		metaFile= 'ExpMetaData.yaml'
		with open(metaFile, 'r') as f:
			metaData= yaml.load(f, Loader=yaml.FullLoader)
		return metaData
	except:
		sys.exit(1)

def find_files_list(path, ext):
	""" Find all exp configuration files (.yaml files) in folder. They are needed to load their corresponding h5 files later
	"""
	return glob.glob(path+'/*'+ext)

def load_expConfig_only(fname, metaData):
	""" Load the configuration settings of an experiment and its data from FLydra
	"""
	try: 
		with open(fname, 'r') as f:
			#dataMap= Exp_Info.Exp_Info(yaml.load(f))
			dataMap= Exp_Info(yaml.load(f, Loader=yaml.FullLoader))
			print(' Configuration settings for experiment on %s loaded sucessfuly'%dataMap.expDate)
		return dataMap
	except Exception as e: 
		print(' ERROR while loading experiment configuration settings for file: %s'%fname)
		print(e)

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


def align_data_for_heatmaps(expList):
	tmpX= []
	tmpY=[]
	tmpZ=[]
	tmpStim=[]

	for exp in expList:
		if ((exp.cuePosToAlign) and (None not in exp.cuePosToAlign)):
			xPos= (expMetaData['LIM_X'] - float(exp.posClrTEST[0]))*(-1)
			deltaX= xPos  - exp.cuePosToAlign[0]
			deltaY= float(exp.posClrTEST[1]) - exp.cuePosToAlign[1]
		else:
			deltaX= 0
			deltaY=0

		option= expMetaData['ODOR']	#option 2 == only CO2
		odorIndex= np.where(exp.stim_List == option)
		
		xAligned= exp.X_List[odorIndex]+deltaX
		yAligned= exp.Y_List[odorIndex]+deltaY

		tmpX= np.hstack((tmpX, xAligned))
		tmpY= np.hstack((tmpY, yAligned))
		tmpZ= np.hstack((tmpZ, exp.Z_List[odorIndex]))
		tmpStim= np.hstack((tmpStim, exp.stim_List[odorIndex]))

	return tmpX, tmpY,tmpZ, tmpStim



def generate_grp_heatmap_for_dataAligned(xVal, yVal, zVal, stimVal, option, ct, cb, metaData, figName):
	# create heatmap
	if (option == 1): stim= 'AIR'
	elif (option == 2): stim='CO2'
	else: stim= 'PostCO2'

	nbins= (600,200)
	heatmapXY, xedges, yedges= np.histogram2d(xVal, yVal, bins=nbins)
	extentXY= [xedges[0], xedges[-1], yedges[-1], yedges[0]]
	heatmapXZ,xedges, yedges = np.histogram2d(xVal, zVal, bins=nbins)
	extentXZ= [xedges[0], xedges[-1], yedges[-1], yedges[0]]
	
	# The height of each bar is the relative number of observations, 
	# (Number of observations in bin / Total number of observations). The sum of the bar heights is 1.
	topValNorm=  metaData['NORM'] #0.00008	#0.0001 #
	normHeatmXY= np.empty(nbins, float)
	normHeatmXZ= np.empty(nbins, float)
	countsSumXY= np.sum(heatmapXY)
	countsSumXZ= np.sum(heatmapXZ)
	for i in range(nbins[0]):
		for j in range(nbins[1]):
#				print('i: %s - j:%s'%(i,j))
			normHeatmXY[i][j] = float(heatmapXY[i][j]) / countsSumXY 
			normHeatmXZ[i][j] = float(heatmapXZ[i][j]) / countsSumXZ 
	normHeatmXY= np.transpose(normHeatmXY)
	normHeatmXZ= np.transpose(normHeatmXZ)
	
	#plot heatmap
	fig, hm= plt.subplots(nrows=2,ncols=1)
	hm[0].set_title('heatmap %s vs %s x-y axis with stim= %s'%(ct, cb, stim))
	hm[0].set_xlabel('X axis')
	hm[0].set_ylabel('Y axis')
	val= hm[0].imshow(normHeatmXY, vmin=0, vmax=topValNorm, extent= extentXY, cmap='jet')
	hm[0].invert_yaxis()
	#hm[0].set_xlim([-LIM_X, LIM_X])
	#hm[0].set_ylim([-LIM_Y, LIM_Y])
	fig.colorbar(val, ax=hm[0])

	hm[1].set_title('heatmap %s vs %s x-z axis with stim= %s'%(ct, cb, stim))
	hm[1].set_xlabel('X axis')
	hm[1].set_ylabel('Z axis')
	val2= hm[1].imshow(normHeatmXZ, vmin=0, vmax=topValNorm,  extent= extentXZ, cmap='jet')
	hm[1].invert_yaxis()
	hm[1].set_ylim([0,0.6])	
	fig.colorbar(val2, ax=hm[1])

	#Save figure
	#heatmaps file naming format: 'hm_date_bc_tc_{1-3}_od
	try:
		figName= figName+'_'+stim+'_'+str(topValNorm)+'.png'
		outputPath= metaData['OUT_PATH']+'python_heatmaps/'
		fig.savefig(outputPath+figName, dpi=600)
		print('  -Heatmap: %s saved in path: %s'%(figName,outputPath))
	except:
		print('  -ERROR! while saving img: %s in path: %s'%(figName,outputPath))

	#CLose figure
	plt.close(fig)


if __name__=='__main__':
	expList=[]
	#Load CONSTANTS related to the experiment
	expMetaData= load_metaData()
	#Find all the .yaml files (experiment cfg file) in folder
	filesList= find_files_list(expMetaData['IN_PATH'], '.yaml')
	#Var to keep track of the positions to be alligned
	posToAlign=[]
	# Load data from .yaml (experiment cfg file) and .h5 (exp raw data) files
	for i, fname in enumerate(filesList):
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

		expList[i].generate_heatmap_with_UI(expMetaData['ODOR'], expMetaData, posToAlign)

		# if (('Pve' in expMetaData['GRP_BY']) and ('-' not in expList[i].posClrTEST[1])) or (('Nve' in expMetaData['GRP_BY']) and ('-' in expList[i].posClrTEST[1])):
		# 	# If the TEST Cue is in the POSITIVE Y axis, load the experiment and group it to the other exp with TEST Cue in similar position
		# 	load_exp_data(expList[i], expMetaData)
		# 	expList[i].generate_heatmap_with_UI(expMetaData['ODOR'], expMetaData, posToAlign)

	#Once the the user has found the expList[X].cuePosToAlign, align each experiment XYZ to its corresponding new cue center
	tmpX, tmpY, tmpZ, tmpStim= align_data_for_heatmaps(expList)
	# Generate the grouped heatmap
	imgTitle= expMetaData['HM_GRP_NAME']
	generate_grp_heatmap_for_dataAligned(tmpX, tmpY, tmpZ, tmpStim, expMetaData['ODOR'], 'black', 'white', expMetaData, imgTitle)

	
	print('end')


