""" Filling a Google Analytics property with custom dimensions using the Management API."""

import argparse
import config
import sys 
from apiclient.discovery import build

import httplib2
from oauth2client import client
from oauth2client import file
from oauth2client import tools


def get_service(api_name, api_version, scope, client_secrets_path, dirname, read_only='yes' ):
	"""Get a service that communicates to a Google API.

	Args:
		api_name: string The name of the api to connect to.
		api_version: string The api version to connect to.
		scope: A list of strings r epresenting the auth scopes to authorize for the
			connection.
		client_secrets_path: string A path to a valid client secrets file.

	Returns:
		A service that is connected to the specified API.
	"""
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
def progress(count, total, suffix=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', suffix))
    sys.stdout.flush()
    
def main():
  # Define the auth scopes to request.
  scope = ['https://www.googleapis.com/auth/analytics.readonly']

  # Refer to the config.py settings file for credentials
  key_file_location = config.apiSettings['key_file_location']
  gaDir = config.apiSettings['gaDir']
  analytics = get_service('analytics', 'v3', scope, key_file_location, gaDir)

  
  accountID='146029107'  
  filterID = ''

  try:
      filters = analytics.management().filters().list(
              accountId = accountID).execute()
      if filters.get('items'):
          for fltr in filters.get('items',[]):
              if fltr.get('name') == 'testing':
                  filterID = fltr.get('id')
          print("Filter id :" , filterID)
          filters = analytics.management().filters().get(
                  accountId = accountID,
                  filterId = filterID).execute()
          print('Filter : ', filters)
          
  except TypeError as error:
      print(error)
  
    
    
if __name__ == '__main__':
  main()
