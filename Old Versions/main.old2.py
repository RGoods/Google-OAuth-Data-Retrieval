def main():


    choice1 = input("Do you have the Access Token? Type Y or N: ")

    if choice1 == 'Y':
        access_token = input("Enter your Google Access Token: ")  # This is taking the users input
        choice2 = input("Is this for Profile or Email download? Type P or E:  ")

    elif choice1 == 'N':
        print('You will now be asked to obtain Client ID and Client Secret from the Mobile Device App.')
        print('If you do not have this, quit now\n')
        generate_access_token()

    else:
        print('Entered incorrect option. If correct, try in all caps.')
        main()

    if choice2 == 'P':
        user_response = query_profile_api(access_token)
        write_files(user_response)

    elif choice2 == 'E':
        user_response = query_email_api(access_token)
        write_files(user_response)

    # This is taking the data obtained by using the Access Token,
    # and placing it into its own variable. Then we're deciding what we're going to perform today.
    # It would've been nice to differ between Access & Refresh tokens, but there's no defined spec.
    # See: https://tools.ietf.org/html/rfc6750, the max length is generally 255...


def generate_access_token():

    from oauth2client.client import OAuth2WebServerFlow
    from oauth2client.tools import run_flow
    from oauth2client.file import Storage

    client_id = input('Input Client ID from App: ')             # Client ID found in the app, linked to Google
    client_secret = input('Input Client Secret from App: ')     # Client Secret found in the app, linked to Google

    flow = OAuth2WebServerFlow(client_id=client_id,
                               client_secret=client_secret,
                               scope='https://www.googleapis.com/userinfo/v2/me, https://www.googleapis.com/gmail/v1/users/me/messages',
                               redirect_uri='http://localhost:8080')

    storage = Storage('credits.data')

    credentials = run_flow(flow, storage)

    print("access_token: %s" % credentials.access_token)
    print("Use Access Token that has just been generated, to re-run the script. :) ")


    # Credit to https://gist.github.com/burnash/6771295#file-get_oauth2_token-py-L23


def query_email_api(access_token):
    # Queries the Email Messages in a Gmail account
    scope = "https://www.googleapis.com/gmail/v1/users/me/messages"

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
                json.dump(user_response, outfile)


if __name__ == '__main__':
    main()
