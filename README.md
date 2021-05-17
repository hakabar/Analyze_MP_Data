# Analyze_MP_Data
Program to analyze the data from Flydra for mosquito project
 
There are 2 python scripts in this folder:
- generate_hm_grpExp.py
- align_heatmaps.py

generate_ht_grpExp.py:
 - This script load the different experiments to group and group them without any additional process in the data. 
 - To be used when we don't want to align the data (for example, when grouping experiments with AIR as odor stimulus)
 - How does it work:
  - Load common metadata (ExpMetaData.yaml) for all experiments in group
  - For each experiment:
    - Load exp metadata from yaml file.
    - Load exp data from h5 file.
    - If Test cue position is not in the same Y axis region (positive (Pve) or negative (Nve)) as specified in ExpMetaData.yaml (GROUP_BY value) then:
      - Mirror the positions in the Y axis (exp.Y_List[0:end]*(-1)).
    - Select the data related to the odor stimulus specified in ExpMetaData.yaml (ODOR value: 1= AIR, 2= CO2, 3= PostCO2).
    - Generate the heatmaps WITHOUT user interface for the given odor.
    - Save single experiment heatmap.
  - Group all the X,Y,Z values and generate the heatmap for the group.
  - Save heatmap for the group.


align_heatmaps.py:
 - This scripts creates the heatmap for each single experiment, allowing the user to select the position where the test cue is visible in the heatmap to align its data with the other experiments. If the cue is not visible in the heatmap, the user can select a point outside the heatmap to keep the test position as specified in the experiments yaml file.
 - To be used when the data need some additional work (mirror it to keep all the test cue in the same Y axis position or to align test X and Y positions over several experiments).
 - How does it work:
  - Load common metadata (ExpMetaData.yaml) for all experiments in group.
  - For each experiment:
    - Load exp metadata from yaml file.
    - Load exp data from h5 file.
    - If Test cue position is not in the same Y axis region (positive (Pve) or negative (Nve)) as specified in ExpMetaData.yaml (GROUP_BY value) then:
      - Mirror the positions in the Y axis (exp.Y_List[0:end]*(-1)).
    - Select the data related to the odor stimulus specified in ExpMetaData.yaml (ODOR value: 1= AIR, 2= CO2, 3= PostCO2).
    - Generate the heatmaps WITH user interface for the given odor:
      - If the test cue's contour is visible in the heatmap, the user can use the left click to select the center of the cue contour to align it with the others experiments.
      - If the test cue's contour is not visible in the heatmap, the user must do a left click in the image, but outside of the heatmaps, to close the UI (the position of the test cue will be the one specified in the exp metada file).
    - Save single experiment heatmap.
  - Align the data from each experiment with the new test cue position selected by the user. If the user didn't select any position in the heatmap, the position of the test cue will be the one specified in the exp metada file. 
  - Group all the X, Y, Z values and generate the heatmap for the group.
  - Save heatmap for the group.



NOTE: To run these scripts you need the following:

1. CONFIGURATION FILES:
	 - ExpMetaData.yaml: Yaml file with the following information as constants:
		  - BASE_COLOR: Color use as base cue
		  - IN_PATH: path to the experiment data. Each experiment must have the following files:
			    - Flydra .h5 file
			    - .yaml file with the timestamps, test color used and cues’ (visual/odor) positions
		  - OUT_PATH: Path in local computer where the heatmaps must be stored (it must exist in the local computer)
		  - OUT_FOLDER: Name of the folder where we want to store the heatmaps
		  - DATASET: Dataset from the Flydra .h5 file to work with
		  - LIM_X, LIM_Y, and LIM_Z: wind tunnel dimension limits
		  - ODOR: integer to specify which part of the experiment we want to plot in the heatmap (Possible values: 1= AIR, 2= CO2, or 3= PostCO2)
		  - NORM: Value to use in the heatmap normalization
		  - GRP_BY: Position of the test cue we want to use to align heatmaps (Possible values: ‘Nve’= Negative Y axis or ‘Pve’= Positive Y axis). 
		            The script will only work with the experiments that have the test cue in the same Y axis side.
		  - HM_GRP_NAME: Name to use for the final image grouping several heatmaps into 1

	- logConfig.yaml: File logging configuration. It can be modified if you want to plot more or less information in the .log file.

2. INPUT FILES: Each experiment must have the following files in a computer’s folder: 
 - Experiment metadata as .yaml (timestamps, test color used, and cues’ (visual/odor) positions) 
 - Flydra file for the experiment as .h5 file

and It will generate the following OUTPUT FILES:
 - A heatmap for each of the single experiment used and for an odor stimuli in particular (AIR/CO2/PostCO2)
 - A heatmap grouping the data of all the single experiment selected.
