
""" Filling a Google Analytics property with custom dimensions using the Management API."""

import argparse
import config
import xlrd
import time
from apiclient.discovery import build
import httplib2
from oauth2client import client
from oauth2client import file
from oauth2client import tools

accounts = []
properties = []
dims = []
status = []
#totaldims = []

def get_service(api_name, api_version, scope, client_secrets_path, dirname, read_only ):
	
	# Parse command-line arguments.
	parser = argparse.ArgumentParser(
			formatter_class=argparse.RawDescriptionHelpFormatter,
			parents=[tools.argparser])
	flags = parser.parse_args([])

	# Set up a Flow object to be used if we need to authenticate.
	flow = client.flow_from_clientsecrets(
			client_secrets_path, scope=scope,
			message=tools.message_if_missing(client_secrets_path))

	# Prepare credentials, and authorize HTTP object with them.
	# If the credentials don't exist or are invalid run through the native client
	# flow. The Storage object will ensure that if successful the good
	# credentials will get written back to a file.
	if read_only != None:
		filename = api_name + read_only
	else : filename = api_name
	print ('dirname : ', dirname)
	print ('filename : ', filename)
	storage = file.Storage(dirname + '/' + filename + '.dat')
	credentials = storage.get()
	if credentials is None or credentials.invalid:
		credentials = tools.run_flow(flow, storage, flags)
	http = credentials.authorize(httplib2.Http())

	# Build the service object.
	service = build(api_name, api_version, http=http)

	return service

    
def main():
  # Define the auth scopes to request.
  scope_edit= ['https://www.googleapis.com/auth/analytics.edit']
  scope_read = ['https://www.googleapis.com/auth/analytics.readonly']

  # Refer to the config.py settings file for credentials
  key_file_location = config.apiSettings['key_file_location']
  gaDir = config.apiSettings['gaDir']
  
  # Authenticate and construct service.
  print("Connecting to Google Analytics API for authentication")
  service_edit = get_service('analytics', 'v3', scope_edit, key_file_location, gaDir, read_only = None)
  service_read = get_service('analytics', 'v3', scope_read, key_file_location, gaDir,read_only='yes')
  
#  loc = ("customDimensionanand.xlsx") 
  
  wb = xlrd.open_workbook("customDimensionDetails_master.xls")  
  
  sheet = wb.sheet_by_index(0)
  
    #accountId and PropertyId...... 
#  sheet.cell_value(0,0)
#looping the XL sheet 1st line after header, modify this when more rows are there.
  for i in range(1,2):
#      print ("Values in : ",i)
      accountId=str(int(sheet.cell_value(i,0)))
      propertyId=str(sheet.cell_value(i,1))
      print("For : Account Id: ",accountId," and Property Id:  ",propertyId, " : ", i, "\n") 
      accounts.append(accountId)
      properties.append(propertyId)
      #checking for the dimensions
      print("Pulling dimensions")
      dimensions = service_read.management().customDimensions().list(
              accountId=accountId,
              webPropertyId=propertyId
              ).execute()
  
      time.sleep(10)  
      nbDims = dimensions.get("totalResults")
#      dims.append(nbDims)
      print("Found " + str(nbDims) + " custom dims"+"\n")
      count=nbDims + 1 
      if nbDims < 200:
          nbNewDims = 200 - nbDims
#          totaldims.append(nbNewDims)
          print("Creating " + str(nbNewDims) + " custom dimensions")
      
                
            #custom dimension values
#      sheet.cell_value(1, 2) 
      for i in range(count,201):
    #          print(sheet.cell_value(i, 2)," ",int(sheet.cell_value(i, 3))," ",sheet.cell_value(i, 4)," ",sheet.cell_value(i, 5))
    #          print("\n")   
          name=sheet.cell_value(i, 2)
          #dimensionIndex=str(int(sheet.cell_value(i,3)))
          dimensionscope= sheet.cell_value(i, 4)
          status=sheet.cell_value(i, 5)
          active=False
          if status=="Active":
              active=True
          elif status=="Inactive":
              active=False
        
      #Insert the new Custom dimensions..
          print("Inserting custom dimension ",i)    
                                  
          try:
             service_edit.management().customDimensions().insert(
             accountId=accountId,
             webPropertyId=propertyId,
             body={
                     'name':name,
                     'scope': dimensionscope,
                     'active': active
                     }            
             ).execute()
             #nbDims+=1
          except TypeError as error:
             print('There was a error: %s' % error)
          print('Done!!!!')
#          status.append('Done')
if __name__ == '__main__':
  main()
