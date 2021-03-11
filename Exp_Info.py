"""
FIle containing the Exp_Info class and all its methods.
This class is used to merge the settings of the experiment with the data from Flydra
"""
import numpy as np
import matplotlib.pyplot as plt
import logging

#Pick logger
logger= logging.getLogger(__name__)



class Exp_Info:
	def __init__(self, obj):
		self.expDate=obj.expDate
		self.fileName= obj.fileName
		self.type=obj.type
		self.gender= obj.gender
		self.clrBASE= obj.clrBASE
		self.clrTEST= obj.clrTEST
		self.posOdor= obj.posOdor
		self.posClrBASE=obj.posClrBASE
		self.posClrTEST=obj.posClrTEST
		self.ts_1_StartExp=obj.ts_1_StartExp
		self.ts_2_CO2= obj.ts_2_CO2
		self.ts_3_PostCO2=obj.ts_3_PostCO2
		self.ts_4_EndExp=obj.ts_4_EndExp
		self.ID_List=[]			# List with the OBJ_IDs from H% file
		self.FR_List=[]			# List with the FRAME number from H5 file
		self.X_List=[]			# List with the X positions from H% file
		self.Y_List=[]			# List with the Y positions from H% file
		self.Z_List=[]			# List with the Z positions from H% file
		self.TS_List=[]			# List with the TIMESTAMPS values from H% file
		self.stim_List=[]		# List with the STIM used at that moment (1=='AIR', 2=='CO2' or 3=='PostCO2')

	# def __init__(self, d, t, g, baseC):
	# 	self.expDate=d
	# 	self.fileName= self.expDate+'.mainbrain.h5'
	# 	self.type=t
	# 	self.gender= g
	# 	self.clrBASE= baseC
	# 	self.clrTEST= ''
	# 	self.posOdor=[]
	# 	self.posClrBASE=[]
	# 	self.posClrTEST=[]
	# 	self.ts_1_StartExp=0
	# 	self.ts_2_CO2=0
	# 	self.ts_3_PostCO2=0
	# 	self.ts_4_EndExp=0
	# 	self.ID_List=[]			# List with the OBJ_IDs from H% file
	# 	self.FR_List=[]			# List with the FRAME number from H5 file
	# 	self.X_List=[]			# List with the X positions from H% file
	# 	self.Y_List=[]			# List with the Y positions from H% file
	# 	self.Z_List=[]			# List with the Z positions from H% file
	# 	self.TS_List=[]			# List with the TIMESTAMPS values from H% file
	# 	self.stim_List=[]		# List with the STIM used at that moment (1=='AIR', 2=='CO2' or 3=='PostCO2')


	def set_color(self, c):
		self.clrTEST= c

	def set_odorPos(self, odor):
		self.posOdor= odor
	
	def set_vCuesPos(self, tc, bc):
		self.posClrTEST=tc
		self.posClrBASE=bc

	def set_ts(self, tsStart, tsCO2, tsPostCO2, tsEnd):
		self.ts_1_StartExp=tsStart
		self.ts_2_CO2=tsCO2
		self.ts_3_PostCO2=tsPostCO2
		self.ts_4_EndExp= tsEnd

	def set_h5_information(self, idList, frList, tsList, xList, yList, zList):
		self.ID_List=idList
		self.FR_List=frList
		self.TS_List=tsList
		self.X_List=xList
		self.Y_List=yList
		self.Z_List=zList

	def apply_start_end_ts(self):
		"""Chop off data recorded from Flydra before and after the experiment duration
		"""
		expIdxs= np.where((self.TS_List >= self.ts_1_StartExp) & (self.TS_List <= self.ts_4_EndExp))
		self.set_h5_information(self.ID_List[expIdxs], self.FR_List[expIdxs], self.TS_List[expIdxs], self.X_List[expIdxs], self.Y_List[expIdxs], self.Z_List[expIdxs] )
		
	def erase_pos_outside_wt(self, metaData):
		"""Delete noisy data recorded outside the wind tunnel test section
		"""		
		#Find the indexes for the values inside the limits of the WT (for each axis X,Y,Z)
		idx= np.where((self.X_List >= -metaData['LIM_X']) & (self.X_List <= metaData['LIM_X']))
		idy= np.where((self.Y_List >= -metaData['LIM_Y']) & (self.Y_List <= metaData['LIM_Y']))
		idz= np.where((self.Z_List >= 0) & (self.Z_List <= metaData['LIM_X']))
		#Intersect these indexes to find the indexes where the (x,y,z) position was inside the WT 
		tmpXY= np.intersect1d(idx, idy, 1)
		idXYZinWT= np.intersect1d(tmpXY, idz,1)
		#the analysis are done only in the (x,y,z) positions inside the WT 3d space
		self.set_h5_information(self.ID_List[idXYZinWT], self.FR_List[idXYZinWT], self.TS_List[idXYZinWT], self.X_List[idXYZinWT], self.Y_List[idXYZinWT], self.Z_List[idXYZinWT] )

	def set_odor_stim(self):
		""" Function to fill self.stim_List with the odor used in each frame (1=='AIR', 2=='CO2' or 3=='PostCO2')
		"""

		self.stim_List= np.empty(len(self.ID_List), dtype=object)
		tmpAir= np.where((self.TS_List >= self.ts_1_StartExp) & (self.TS_List < self.ts_2_CO2))
		tmpCo2= np.where((self.TS_List >= self.ts_2_CO2) & (self.TS_List < self.ts_3_PostCO2))
		tmpPost= np.where((self.TS_List >= self.ts_3_PostCO2) & (self.TS_List <= self.ts_4_EndExp))
		if len(tmpAir[0]) + len(tmpCo2[0]) + len(tmpPost[0]) == len(self.stim_List):
			self.stim_List[tmpAir[0]]= 1
			self.stim_List[tmpCo2[0]]= 2
			self.stim_List[tmpPost[0]]= 3
		else:
			logger.ERROR('ERROR! indexes sizes pero each odor stim do not match the stim_list size')

	def generate_heatmap(self, option, metaData):
		# create heatmap
		if (option == 1): stim= 'AIR'
		elif (option == 2): stim='CO2'
		else: stim= 'PostCO2'
	
		i= np.where(self.stim_List == option)
		nbins= (600,200)
		heatmapXY, xedges, yedges= np.histogram2d(self.X_List[i], self.Y_List[i], bins=nbins)
		extentXY= [xedges[0], xedges[-1], yedges[-1], yedges[0]]
		heatmapXZ,xedges, yedges = np.histogram2d(self.X_List[i], self.Z_List[i], bins=nbins)
		extentXZ= [xedges[0], xedges[-1], yedges[-1], yedges[0]]
		
		# The height of each bar is the relative number of observations, 
		# (Number of observations in bin / Total number of observations). The sum of the bar heights is 1.
		topValNorm=0.0001
		normHeatmXY= np.empty(nbins, float)
		normHeatmXZ= np.empty(nbins, float)
		countsSumXY= np.sum(heatmapXY)
		countsSumXZ= np.sum(heatmapXZ)
		for i in range(nbins[0]):
			for j in range(nbins[1]):
				normHeatmXY[i][j] = float(heatmapXY[i][j]) / countsSumXY 
				normHeatmXZ[i][j] = float(heatmapXZ[i][j]) / countsSumXZ 
		normHeatmXY= np.transpose(normHeatmXY)
		normHeatmXZ= np.transpose(normHeatmXZ)
		
		#plot heatmap
		fig, hm= plt.subplots(nrows=2,ncols=1)
		hm[0].set_title('heatmap %s vs %s x-y axis with stim= %s'%(self.clrTEST, self.clrBASE, stim))
		hm[0].set_xlabel('X axis')
		hm[0].set_ylabel('Y axis')
		val= hm[0].imshow(normHeatmXY, vmin=0, vmax=topValNorm, extent= extentXY)
		hm[0].invert_yaxis()
		#hm[0].set_xlim([-LIM_X, LIM_X])
		#hm[0].set_ylim([-LIM_Y, LIM_Y])
		fig.colorbar(val, ax=hm[0])

		hm[1].set_title('heatmap %s vs %s x-z axis with stim= %s'%(self.clrTEST, self.clrBASE, stim))
		hm[1].set_xlabel('X axis')
		hm[1].set_ylabel('Z axis')
		val2= hm[1].imshow(normHeatmXZ, vmin=0, vmax=topValNorm,  extent= extentXZ)
		hm[1].invert_yaxis()
		hm[1].set_ylim([0,0.6])		
		fig.colorbar(val2, ax=hm[1])

		#If you want to show the image uncomment this line
		#plt.show()

		#Save figure
		#heatmaps file naming format: 'hm_date_bc_tc_{1-3}_od
		try:
			figName= 'hm_%s_%s_vs_%s_%s_%s.png'%(self.expDate, self.clrBASE,self.clrTEST, option, stim)
			outputPath= metaData['OUT_PATH']+'exp_%s_%s/heatmaps/python_heatmaps/'%(self.clrBASE, self.clrTEST)
			fig.savefig(outputPath+figName)
			logger.info('  -Heatmap: %s saved in path: %s'%(figName,outputPath))
		except:
			logger.exception('  -ERROR! while saving img: %s in path: %s'%(figName,outputPath))

		#CLose figure
		plt.close(fig)
