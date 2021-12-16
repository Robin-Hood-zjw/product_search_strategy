# Product_Search_Strategy
This program originates from the final project of  the class SI507.

This repo was created for the the program about searching a targte product within the online Kroger shopping environment. This repo entails the following files to guarantee the running status of the program:

1.final_project.py

2.final_secrets.py

3.swagger.json

# Acquiring Keys from Kroger API
The API keys of Kroger online develper website can be acquired from the link: https://developer.kroger.com/. A specified redirect URI is required since it offers an authorization code during API authorization. Moreover, users need to request location, products permission in the environments: https://api.kroger.com/v1/ . As for the API authorization, the OAuth2 protocol is required by Kroger via the authorization code, clinet credentials and refresh token grant types. More reference can be found via this link: https://developer.kroger.com/reference/.

# Secrets
Personal API keys and redirect URI is stored in a file called <final_secrets.py>. This file needs to be imported into main program <final_project_experiment.py>. The following format and enter your own keys and redirect URI:

KROGER_CLIENT_ID= ""

KROGER_CLIENT_SECRET=""

REDIRECT_URI = ""
