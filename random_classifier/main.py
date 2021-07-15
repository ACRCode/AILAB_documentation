import numpy as np
import argparse
import pydicom
import pandas as pd
import logging
from datetime import datetime
import json
import requests
import torch
import sys
import os
import pylibjpeg

### Define log file and begin logging ###
startTime = datetime.now().timestamp()
modelName = 'randomClassification'
logFilepath = '/output/' + modelName + '_' + str(startTime) + '.log'
file_handler = logging.FileHandler(filename=logFilepath)
stdout_handler = logging.StreamHandler(sys.stdout)
handlers = [file_handler, stdout_handler]
logging.basicConfig(
    level=logging.DEBUG, 
    handlers=handlers
)
logging.info('Started: %s', startTime)

torch.cuda.is_available()

def getEnvVarOrDefault(var, default):
	envVar = os.environ.get(var)
	if(envVar is None):
		return default
	return envVar

### Define and load arguments ###
parser = argparse.ArgumentParser()
parser.add_argument("--gpu", default=getEnvVarOrDefault('gpu', None), help="int indicating which gpu to utilize", type=int)
parser.add_argument("--reportUrl", default= getEnvVarOrDefault('report_url', 'https://foo.bar'),help="url to report back progress", type=str)
parser.add_argument("--jobId", default =getEnvVarOrDefault('job_id', 'job0'),help="unique jobid to use in progress messages", type=str)	
args = parser.parse_args()

# specify device
if args.gpu is None:
	device = torch.device('cpu')
else:
	device = torch.device('cuda:' + str(args.gpu))
	
# number of classes for this particular data element model will predict
num_classes = torch.tensor(4, device = device) 

	

### Load input csv ###
try:
	inputFilepath = "/input/input.csv"
	data = pd.read_csv(inputFilepath)
	studies = np.unique(data['studyInstanceUID'].to_numpy()) #list of unique studyinstanceuids
	logging.info('Loaded %s', inputFilepath)
	num_studies = len(studies)
	logging.info('Loaded %s unique studyinstanceuids', num_studies)
except Exception as e:
	logging.error('Failed to load input csv %s', datetime.now().timestamp())
	logging.error(e, exc_info=True)

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
			dcm = pydicom.dcmread('/input/' + file) # load each image file

			image = (255*(dcm.pixel_array.astype(float)/((2**dcm.BitsStored)-1))).astype(np.uint8)
			
			# move image data to device
			image = torch.from_numpy(image).float().to(device)
			# generate a new prediction for each image
			prediction.append(torch.rand(num_classes))

		# normalize prediction
		prediction = sum(prediction)/(sum(sum(prediction)))
		prediction = prediction.numpy().astype(np.float64)

		# save study prediction in JSON format	
		predictions_list.append({
			"studyInstanceUID": str(study),
			"classificationOutput": [{
				"key": "rde_341", # breast density classification key
				"output": {
					"1" : prediction[0],
					"2" : prediction[1],
					"3" : prediction[2],
					"4" : prediction[3],
				}
			}]
		})
		
		# send progress message via url
		i+=1
		progress = round(i/num_studies*100) # progress is an integer 0-100
		progress_json = {'jobId':args.jobId, 'jobStatus':'running', 'jobProgress':progress}
		# requests.post(args.reportUrl, data=progress_json)
		
		logging.info('Processed study %s', study)
		
	except Exception as e:
		logging.error('Failed to generate prediction for study %s, time: %s', study, datetime.now().timestamp())
		logging.error(e, exc_info=True)
		

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

json_filepath = '/output/output.json'

try:
	with open(json_filepath, 'w') as fp:
		json.dump(output_json, fp)
	logging.info('Saved output to %s', json_filepath)
except Exception as e:
	logging.error('Failed to save output to %s at %s',json_filepath, datetime.now().timestamp())
	logging.error(e, exc_info=True)


### Send complete job status and finish ###
complete_json = {'jobId':args.jobId, 'jobStatus':'complete'}
# requests.post(args.reportUrl, data=progress_json)

endTime = datetime.now().timestamp()
logging.info('Completed: %s', endTime)
logging.info('Elapsed time: %s', endTime-startTime)
