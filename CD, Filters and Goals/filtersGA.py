""" Filling a Google Analytics property with custom dimensions using the Management API."""

import argparse
import config
import sys 
from apiclient.discovery import build
import xlrd
import httplib2
from oauth2client import client
from oauth2client import file
from oauth2client import tools


def get_service(api_name, api_version, scope, client_secrets_path, dirname, read_only='yes' ):
	"""Get a service that communicates to a Google API."""
	parser = argparse.ArgumentParser(
			formatter_class=argparse.RawDescriptionHelpFormatter,
			parents=[tools.argparser])
	flags = parser.parse_args([])
	flow = client.flow_from_clientsecrets(
			client_secrets_path, scope=scope,
			message=tools.message_if_missing(client_secrets_path))

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
def progress(count, total, suffix=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', suffix))
    sys.stdout.flush()
    

def checkIfFilterExists(analytics,accountID,filterName):
    filterID = '' 
    
    try:
      filters = analytics.management().filters().list(
              accountId = accountID).execute()
      if filters.get('items'):
          for fltr in filters.get('items',[]):
              if fltr.get('name') == filterName:
                  filterID = fltr.get('id')

          return filterID
    except TypeError as error:
        print(error)

def createFilter(analytics,accountId,body):
    try:
      response = analytics.management().filters().insert(
          accountId=accountId,
          body=body
      ).execute()
 
    except TypeError as error:
       print(error)
    return response
        
def checkIfProfileFilterLinkExists(analytics,accountId,propertyId,viewId,filterId):
  response = ''
  linkId = '' 
   
  try:
      response = analytics.management().profileFilterLinks().list(
              accountId = accountId,
              webPropertyId= propertyId,
              profileId = viewId
              ).execute()
      if response.get('items'):
           for link in response.get('items',[]):
               filterRef = link.get('filterRef',{})
               filterRefId = filterRef.get('id')
               if filterRefId == filterId:
                   linkId = link.get('id')
               return linkId        
          
  except TypeError as error:
      print(error)

def updateFilter(analytics,accountId,propertyId,filterId,body):
    response = '' 
    try:
        response = analytics.management().filters().update(
                accountId = accountId,
                filterId = filterId,
                body=body
                ).execute()
        
    except TypeError as error:
        print(error)
    return response

def createProfileFilterlink(analytics, accountId, propertiId, viewId, body):
    response =  '' 
    try:
	    response = analytics.management().profileFilterLinks().insert(
			    accountId=accountId,
			    webPropertyId=propertiId,
				profileId=viewId,		  
			    body=body
			  ).execute()
    except TypeError as error:
    	  print(error) 
    return response


def updateFilterLink(analytics, accountId, propertiId, profileId, linkId, body):
    response = ''
    try:
	    response = analytics.management().profileFilterLinks().update(
					    accountId=accountId,
					    webPropertyId=propertiId,
						profileId=profileId,
						linkId=linkId,
					    body=body
					  ).execute()
    
    except TypeError as error:
        print (error)
    return response  
        
def main():
  scope = ['https://www.googleapis.com/auth/analytics.readonly']
  scope2 = ['https://www.googleapis.com/auth/analytics.edit']
  key_file_location = config.apiSettings['key_file_location']
  gaDir = config.apiSettings['gaDir']
  
  analytics = get_service('analytics', 'v3', scope, key_file_location, gaDir)
  service = get_service('analytics', 'v3', scope2, key_file_location, gaDir,read_only=None)
  
  wb = xlrd.open_workbook('filterDetails_updated.xls') 
  sheet = wb.sheet_by_index(0)
  
  for i in range(1,sheet.nrows):
      accountId = str(int(sheet.cell_value(i,0)))
      propertyId = str(sheet.cell_value(i,1))
      viewId = str(int(sheet.cell_value(i,2)))
      filterName = str(sheet.cell_value(i,3))
      filterType =  str(sheet.cell_value(i,4))
      filterField = 'GEO_IP_ADDRESS'
      caseSensitive = str(sheet.cell_value(i,5))
      filterPattern = str(sheet.cell_value(i,6))
      body = {}
      details = {}
      body['name'] = filterName
      body['type'] = filterType
      
      details['field'] = filterField
      details['expressionValue'] = filterPattern
      details['caseSensitive']=caseSensitive
      
      body['excludeDetails']=details
      
      print("Checking if ",filterName," exists")
      filterId = checkIfFilterExists(analytics,accountId,filterName)
      if filterId != '' and filterId != None:
          print("Filter named ",filterName," exists with filter Id: ", filterId)
          body['id'] = filterId
          print("Updating ",filterName)
          response = updateFilter(service, accountId, propertyId,filterId,body)
          if type(response) == dict:
              body = {}
              details = {}
              if response.get('id'):
                  details['id'] = str(response.get('id'))
                  body['filterRef'] = details
                  print("Checking if Filter is linked with a View (profile)")
                  linkId = checkIfProfileFilterLinkExists(analytics,accountId,propertyId,viewId,filterId)
                  if linkId != '' and linkId != None:
                      print("Updating Filter View Link")
                      response = updateFilterLink(service,accountId,propertyId,viewId,linkId,body)
                  else: 
                      print("Creating a Filter View Link")
                      response = createProfileFilterlink(service,accountId,propertyId,viewId,body)          
         
      elif filterId == '' or filterId ==None :
          print("Creating ",filterName," for accountId", accountId)
          response = createFilter(service,accountId,body)
          if type(response) == dict:
              body={}
              details={}
              if response.get('id'):
                  details['id'] = str(response.get('id'))   
                  body['filterRef'] = details
                  linkId = checkIfProfileFilterLinkExists(analytics,accountId,propertyId,viewId,filterId)
                  if linkId != '' and linkId != None:
                      print("Updating Filter View Link")
                      response = updateFilterLink(service,accountId,propertyId,viewId,linkId,body)
                  else: 
                      print("Creating a Filter View Link")
                      response = createProfileFilterlink(service,accountId,propertyId,viewId,body) 
                 
    
                  
    
if __name__ == '__main__':
  main()
