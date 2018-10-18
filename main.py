import httplib2
import requests
import self as self
import simplejson as json
import google.oauth2.credentials
from googleapiclient import errors
from oauth2client import client
from oauth2client.tools import run_flow
from oauth2client.file import Storage
from googleapiclient.discovery import build
from googleapiclient.http import BatchHttpRequest


def print_menu():
    print("""
        ******************************
        * Google Cloud Data Recovery *
        ******************************

        1. Input Google Access Token (Profile Data)
        2. Input Google Access Token (Email Data)
        3. Create Google Access Token (No App Data)
        4. Create Google Access Token (Supplied by App)
        5. Quit
            """)


def main():
    user_response = None
    print_menu()
    choice = input("Type number option you require: ")
    if choice == "1":
        access_token = input("(PROFILE) Enter your Google Access Token: ")
        user_response = query_profile_api(access_token)
    elif choice == "2":
        access_token = input("(EMAIL) Enter your Google Access Token: ")
        query_email_api(access_token)
    elif choice == "3":
        user_request_access_token()
    elif choice == "4":
        generate_access_token()
    elif choice == "5":
        exit()
    else:
        print("\nInvalid choice, try again")
    if user_response is not None:
        write_files(user_response)
    main()


def user_request_access_token():
    """
    Generates an OAuth access token by having the user give access to their account (WARNING: USER PERMISSION REQUIRED)
    """
    client_id = '280174354411-s5ss17k6bb39ql04nf472fjlteh9nqmv.apps.googleusercontent.com'
    client_secret = 'h0gtTSge5BmtHxHOzf83cRdC'

    flow = client.OAuth2WebServerFlow(
        client_id=client_id,
        client_secret=client_secret,
        scope='https://www.googleapis.com/auth/userinfo.profile '
              'https://www.googleapis.com/auth/gmail.readonly',
        redirect_uri='http://localhost:8080')

    storage = Storage('token.data')

    credentials = run_flow(flow, storage)

    print("Access Token: %s" % credentials.access_token)
    print("Refresh Token: %s" % credentials.refresh_token)
    return


def generate_access_token():
    """
    Generates an OAuth access token given a client_id, client_secret and refresh_token stored within an app.
    """
    client_id = input('Input Client ID from App: ')  # Client ID found in the app, linked to Google
    client_secret = input('Input Client Secret from App: ')  # Client Secret found in the app, linked to Google
    refresh_token = input('Input Refresh Token from App: ')

    cred = client.GoogleCredentials(
        access_token=None,
        client_id=client_id,
        client_secret=client_secret,
        refresh_token=refresh_token,
        token_expiry=None,
        token_uri='https://accounts.google.com/o/oauth2/token',
        user_agent='Python client library',
        revoke_uri='https://accounts.google.com/o/oauth2/revoke')
    http = cred.authorize(httplib2.Http())
    cred.refresh(http)
    self.gmail_service = build('gmail', 'v1', credentials=cred)
    print("Access Token: %s" % cred.access_token)
    return


def query_email_api(access_token):
    """
    this queries the Gmail Batch API for Gmail messages.
    param access_token: an oauth access token
    return:
    """
    f = open("emaildata.json", "w+")
    f.close()

    def callback(response):
        """
        generic callback function used to deal with the responses from the Batch API.
        """
        with open('emaildata.json', 'a') as outfile:
            json.dump(response, outfile, indent=4, sort_keys=True)
        return

    credentials = google.oauth2.credentials.Credentials(access_token)
    GMAIL = build('gmail', 'v1', credentials=credentials)
    message_ids = GMAIL.users().messages().list(userId='me', ).execute()

    try:
        messages = []
        count = 0
        if 'messages' in message_ids:
            messages.extend(message_ids['messages'])

        while 'nextPageToken' in message_ids:
            page_token = message_ids['nextPageToken']
            message_ids = GMAIL.users().messages().list(userId='me', pageToken=page_token).execute()
            messages.extend(message_ids['messages'])
            count += 1

        message_estimate = count * 100
    except errors.HttpError as error:
        print('An error occurred: %s' % error)

    choice = input("%d Pages of Messages have been found on this account. It is estimated that"
                   "would be %d Messages.\nWould you like to continue? Type Y to Proceed, otherwise type any key: " % (
                       count, message_estimate))
    if choice == "Y":
        message_ids_sorted = ([message_id['id'] for message_id in messages])
        batch = BatchHttpRequest()
        for msg_id in message_ids_sorted:
            batch.add(GMAIL.users().messages().get(userId='me', id=msg_id, format='minimal'), callback=callback)
            batch.execute()
        return
    else:
        return


def query_profile_api(access_token):
    """
    This function queries the Google Profile API for OAuth and returns name and details.
    param access_token: OAuth access token.
    return data: Returns the response from the Profile API and passes it through to the Json file.
    """
    scope = "https://www.googleapis.com/userinfo/v2/me"

    headers = {
        'cache-control': "no-cache",
        'Authorization': 'Bearer ' + access_token
    }
    response = requests.request("GET", scope, headers=headers)
    response.raise_for_status()
    data = response.json()
    return data


def write_files(user_response):
    """
    Writes generic json blobs to disk
    param user_response: Generic json blob
    return:
    """
    with open('data.json', 'w') as outfile:
        json.dump(user_response, outfile, indent=4, sort_keys=True)
    return


if __name__ == '__main__':
    main()
