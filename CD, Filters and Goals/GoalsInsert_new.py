import argparse
import config
import xlrd
import sys 
from apiclient.discovery import build
import httplib2
from oauth2client import client
from oauth2client import file
from oauth2client import tools


def get_service(api_name, api_version, scope, client_secrets_path, dirname, read_only= None):
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
	service = build(api_name, api_version, http=http)
	return service

def progress(count, total, suffix=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))
    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)
    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', suffix))
    sys.stdout.flush()
    
def main():
  scope = ['https://www.googleapis.com/auth/analytics.edit']
  key_file_location = config.apiSettings['key_file_location']
  gaDir = config.apiSettings['gaDir']
  
  service = get_service('analytics', 'v3', scope, key_file_location, gaDir)

  wb = xlrd.open_workbook('New_Goals.xls') 
  sheet = wb.sheet_by_index(0)
  
  for j in range(1,2):
      accountId = str(int(sheet.cell_value(j,0)))
      propertyId = str(sheet.cell_value(j,1))
      profileId = str(int(sheet.cell_value(j,2)))
      print(accountId,"  ",propertyId,"  ",profileId)
      
      for i in range(1,sheet.nrows):
          goalName = str(sheet.cell_value(i,3))
          goalType = str(sheet.cell_value(i,4))
          goalId = str(int(sheet.cell_value(i,5)))
          eventActionComparison = str(sheet.cell_value(i,8))
          eventAction = str(sheet.cell_value(i,9))
         # eventActionInt=int(sheet.cell_value(i,9))
          
          print("Inserting Goal: ",goalId,goalName,goalType,eventActionComparison,eventAction)
          if goalType=="EVENT":
              print("Inserting an event ", )
              try:
                  service.management().goals().insert(
                  accountId=accountId,
                  webPropertyId=propertyId,
                  profileId=profileId,
                  body={
                      'id': goalId,
                      'active': True,
                      'name': goalName,
                      'type': goalType,
                      'eventDetails': {
                          'useEventValue': 'True',
                          'eventConditions': [
                                  {
                                  'type': 'ACTION',
                                  'matchType': eventActionComparison,
                                  'expression': eventAction
                                  }
                                  ]
                          }
                  }
              ).execute()
            
              except TypeError as error:
                      print( 'There was an error in constructing your query : %s' % error)
              
          elif goalType == "VISIT_TIME_ON_SITE":
              print("Insert a Duration:")
              try:
                  service.management().goals().insert(
                  accountId=accountId,
                  webPropertyId=propertyId,
                  profileId=profileId,
                  body={
                      'id': goalId,
                      'active': True,
                      'name': goalName,
                      'type': goalType,
                      "visitTimeOnSiteDetails": {
                            "comparisonType": eventActionComparison,
                            "comparisonValue": int(sheet.cell_value(i,9))
                          }
                  }
              ).execute()
            
              except TypeError as error:
                      print( 'There was an error in constructing your query : %s' % error)
                      
          elif goalType == "VISIT_NUM_PAGES":
              print("Insert a Page Per Session:")
              try:
                  service.management().goals().insert(
                  accountId=accountId,
                  webPropertyId=propertyId,
                  profileId=profileId,
                  body={
                      'id': goalId,
                      'active': True,
                      'name': goalName,
                      'type': goalType,
                      "visitNumPagesDetails": {
                              "comparisonType": eventActionComparison,
                              "comparisonValue": int(sheet.cell_value(i,9))
                              }
                      }
              ).execute()
            
              except TypeError as error:
                      print( 'There was an error in constructing your query : %s' % error)
#                      
                      
      print("Updating the pre-existing goal : 3" )
      goalName = str(sheet.cell_value(3,3))
      goalType = str(sheet.cell_value(3,4))
      goalId = str(int(sheet.cell_value(3,5)))
      eventCategoryComparison = str(sheet.cell_value(3,6))
      eventCategory = str(sheet.cell_value(3,7))
      eventLabelComparison = str(sheet.cell_value(3,10))
      eventLabel = str(sheet.cell_value(3,11))
      service.management().goals().update(
      accountId=accountId,
      webPropertyId=propertyId,
      profileId=profileId,
      goalId=goalId,
      body={
          'active': True,
          'name': goalName,
          'type': goalType,
          'eventDetails': {
              'useEventValue': 'True',
              'eventConditions': [
                      {
                              'type':'CATEGORY',
                              'matchType':eventCategoryComparison,
                              'expression':eventCategory
                      },
                              {
                                      'type':'LABEL',
                                      'matchType': eventLabelComparison,
                                      'expression':eventLabel
                                      }
                    
                      ]
                  }
              }
              ).execute()    
if __name__ == '__main__':
  main()

