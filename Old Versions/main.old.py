import requests
import simplejson as json
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run_flow
from oauth2client.file import Storage


def print_menu():

    print("""
            Cloud Data Recovery:
            ------------

            1. Input Google Access Token (Profile Data)
            2. Input Google Access Token (Email Data)
            3. Create Google Access Token (No App Data)
            4. Create Google Access Token (Supplied by App)
            5. Quit
            """)


def main():

    loop = True
    while loop:
        print_menu()
        choice = input("Type number of option you require: ")
        if choice == "1":
            access_token = input("(PROFILE) Enter your Google Access Token: ")
            user_response = query_profile_api(access_token)
            write_files(user_response)

        elif choice == "2":
            access_token = input("(EMAIL) Enter your Google Access Token: ")
            user_response = query_email_api(access_token)
            write_files(user_response)

        elif choice == "3":
            generate_access_token()

        elif choice == "4":
            generate_access_token2()

        elif choice == "5":
            print("\nGoodbye")
            loop = False
            exit()

        else:
            print("\nInvalid choice, try again")
            loop = True

    # This is taking the data obtained by using the Access Token,
    # and placing it into its own variable. Then we're deciding what we're going to perform today.
    # It would've been nice to differ between Access & Refresh tokens, but there's no defined spec.
    # See: https://tools.ietf.org/html/rfc6750, the max length is generally 255...


def generate_access_token():

    # Credit to https://gist.github.com/burnash/6771295#file-get_oauth2_token-py-L23

    client_id = '280174354411-s5ss17k6bb39ql04nf472fjlteh9nqmv.apps.googleusercontent.com'          # Client ID found in the app, linked to Google
    client_secret = 'h0gtTSge5BmtHxHOzf83cRdC'                                                      # Client Secret found in the app, linked to Google

    flow = OAuth2WebServerFlow(client_id=client_id,
                               client_secret=client_secret,
                               scope='https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/gmail.readonly',
                               redirect_uri='http://localhost:8080')

    storage = Storage('credits.data')

    credentials = run_flow(flow, storage)

    print("Access Token: %s" % credentials.access_token)
    print("Refresh Token: %s" % credentials.refresh_token)
    main()


def generate_access_token2():

    client_id = input('Input Client ID from App: ')             # Client ID found in the app, linked to Google
    client_secret = input('Input Client Secret from App: ')     # Client Secret found in the app, linked to Google

    flow = OAuth2WebServerFlow(client_id=client_id,
                               client_secret=client_secret,
                               scope='https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/gmail.readonly',
                               redirect_uri='http://localhost:8080')

    storage = Storage('token.data')

    credentials = run_flow(flow, storage)
    print("Access Token: %s" % credentials.access_token)
    print("Refresh Token: %s" % credentials.refresh_token)
    main()


def query_email_api(access_token):
    # Queries the Email Messages in a Gmail account
    print("This may take a moment...")

    scope = "https://www.googleapis.com/gmail/v1/users/me/messages"
    headers = {
        'cache-control': "no-cache",
        'Authorization': 'Bearer ' + access_token
    }

    response = requests.request("GET", scope, headers=headers)
    response.raise_for_status()                         # Error Checking
    data = response.json()                              # Checks whether the data is in JSON format
    dumped = json.dumps(data)                           # Converts response into string
    gmail_list = json.loads(dumped)                     # Converts string to object
    msg_count = (len(gmail_list['messages']))           # Counts the amount of message IDs recovered
    i = 0                                               # This is setting the variables
    s = 0                                               # In order to increment and stop when too far

    f = open("emaildata.json", "w")
    f.close()

    while msg_count != i:
        msg_id = gmail_list["messages"][s]["id"]
        s = s + 1
        msg_count = msg_count - 1
        scope = 'https://www.googleapis.com/gmail/v1/users/me/messages/' + msg_id
        headers = {
            'cache-control': "no-cache",
            'Authorization': 'Bearer ' + access_token
        }
        params = {
            'prettyPrint': "true",
            'format': "minimal"
        }
        response = requests.request("GET", scope, headers=headers, params=params)
        data = response.json()
        with open('emaildata.json', 'a+') as outfile:
            json.dump(data, outfile, indent=4, sort_keys=True)

    print("Successful!")

    main()


def query_profile_api(access_token):
    # Queries the Basic Info of Google
    scope = "https://www.googleapis.com/userinfo/v2/me"

    headers = {
        'cache-control': "no-cache",
        'Authorization': 'Bearer ' + access_token
    }
    response = requests.request("GET", scope, headers=headers)
    # Error Checking
    response.raise_for_status()
    # Checks whether the data is in JSON format
    data = response.json()
    return data


def write_files(user_response):
        with open('data.json', 'w') as outfile:
            json.dump(user_response, outfile, indent=4, sort_keys=True)


if __name__ == '__main__':
    main()