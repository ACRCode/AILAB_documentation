import numpy as np
import argparse
import pydicom
import pandas as pd
import logging
from datetime import datetime
import json
import requests

### Define log file and begin logging ###
startTime = datetime.now().timestamp()
modelName = 'randomClassification'
logFilepath = 'output/' + modelName + '_' + str(startTime) + '.log'
logging.basicConfig(filename=logFilepath,level=logging.DEBUG)
logging.info('Started: %s', startTime)

num_classes = 4 # number of classes for this particular data element model will predict

### Define and load arguments ###
parser = argparse.ArgumentParser()
parser.add_argument("--gpu", help="int indicating which gpu to utilize",
                    type=int)
parser.add_argument("--reportUrl", help="url to report back progress",
                    type=str)
parser.add_argument("--jobId", help="unique jobid to use in progress messages",
                    type=str)	
args = parser.parse_args()


### Load input csv ###
try:
	inputFilepath = "input/input.csv"
	data = pd.read_csv(inputFilepath)
	studies = np.unique(data['studyInstanceUID'].to_numpy()) #list of unique studyinstanceuids
	logging.info('Loaded %s', inputFilepath)
	num_studies = len(studies)
	print(num_studies)
	logging.info('Loaded %s unique studyinstanceuids', num_studies)
except:
	logging.error('Failed to load input csv %s', datetime.now().timestamp())

predictions_list = [] # empty list of predictions
i=0 # number of successfully processed studies

### Generate predictions ###
for study in studies:
	# load study and create prediction
	try: 		
		# predictions are at a study level for this particular data element
		# for each studyinstanceUID, find all filepaths
		filesByStudy = data.loc[data['studyInstanceUID'] == study]['filepath'].to_numpy()
		prediction=[]
		for file in filesByStudy:
			try: 
				image = pydicom.dcmread(file) # load each image file
				prediction = np.random.rand(num_classes) # generate a new prediction for each image
				print(prediction)
			except:
				logging.error('Failed to load file %s, time: %s', file, datetime.now().timestamp())
		
		prediction_normalized = prediction/(np.sum(prediction))
		
		
		# save study prediction in JSON format	
		predictions_list.append({
			"studyInstanceUID": str(study),
			"classificationOutput": [{
				"key": "rde_341", # breast density classification key
				"output": {
					"1" : prediction_normalized[0],
					"2" : prediction_normalized[1],
					"3" : prediction_normalized[2],
					"4" : prediction_normalized[3],
				}
			}]
		})
		
		# send progress message via url
		i+=1
		progress = round(i/num_studies*100) # progress is an integer 0-100
		progress_json = {'jobId':args.jobId, 'jobStatus':'running', 'jobProgress':progress}
		# requests.post(args.reportUrl, data=progress_json)
		
		logging.info('Processed study %s', study)
		
	except:
		logging.error('Failed to generate prediction for study %s, time: %s', study, datetime.now().timestamp())
		

### Log count of successfully processed and failed studies ###
logging.info('Number of studies successfully processed: %s', i)
logging.info('Number of studies failed: %s', num_studies-i)


### Create JSON output ###
output_json = {
	"usecase": "breast_density",
	"modelname": "randomClassification",
	"studies": {
	}}

output_json["studies"]=predictions_list

print(output_json)

json_filepath = 'output/output.json'

try:
	with open(json_filepath, 'w') as fp:
		json.dump(output_json, fp)
	logging.info('Saved output to %s', json_filepath)
except:
	logging.error('Failed to save output to %s at %s',json_filepath, datetime.now().timestamp())


### Send complete job status and finish ###
complete_json = {'jobId':args.jobId, 'jobStatus':'complete'}
# requests.post(args.reportUrl, data=progress_json)

endTime = datetime.now().timestamp()
logging.info('Completed: %s', endTime)
logging.info('Elapsed time: %s', endTime-startTime)