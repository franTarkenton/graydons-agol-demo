import requests
import re
import json
from bs4 import BeautifulSoup
from requests_ntlm import HttpNtlmAuth

class Utilities:
    def __init__(self) -> None:
        pass


    def get_agol_token(client_id:str, client_secret:str, username:str, password:str) -> str:

        parameters = {'client_id': client_id,
                      'response_type': 'code',
                      'expiration': 60,
                      'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob'
        }
        # Ask the portal to authorize us
        url = 'https://governmentofbc.maps.arcgis.com/sharing/rest/oauth2/authorize'
 
        response = requests.get(url, params=parameters)
        content = response.text

        pattern = re.compile('var oAuthInfo = ({.*?})', re.DOTALL)
 
        soup = BeautifulSoup(content, 'html.parser')
        for script in soup.find_all('script'):
            script_code = str(script.string).strip()
            matches = pattern.search(script_code)
            if not matches is None:
                js_object = '{0}}}'.format(matches.groups()[0])
                oAuthInfo = json.loads(js_object)
                break

        post_data = {
            'oauth_state': oAuthInfo['oauth_state']
        }
 
        credentials = HttpNtlmAuth('gshevche', 'Winter_22$')
        response = requests.post(oAuthInfo['federationInfo']['idpAuthorizeUrl'], data = post_data, allow_redirects = True, auth=credentials)
        response_one = requests.post(response.url, data={'user':'gshevche', 'password':'Winter_22$'},)
        soup = BeautifulSoup(response_one.content)
        code = soup.find('input', {'id': 'code'}).get('value')
        # Exchange the code for an access token
        post_data = {
            'client_id': client_id,
            'code': code,
            'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob',
            'grant_type': 'authorization_code'
        }
 
        url = 'https://governmentofbc.maps.arcgis.com/sharing/rest/oauth2/token'

        response = requests.post(url, data = post_data)
        token_response = json.loads(response.text)
        access_token = token_response['access_token']

        # Dump out the content for this account, just to prove things are working
        parameters = {
            'token': access_token,
            'f': 'json'
        }

        url = 'https://governmentofbc.maps.arcgis.com/sharing/rest/portals/self'
        response = requests.get(url, params=parameters)
        query_result = json.loads(response.text)

        print
        print("Portal Name:", query_result['name'])
        print("Who am I?:  ", query_result['user']['fullName'])
        
        return access_token