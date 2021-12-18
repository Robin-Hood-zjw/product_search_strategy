# This project is not totally complete because of some existing Oauth problems. You need to go to another branch called master to check files for this project.

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

# Requirements
Several packages are required to installed:

from functools import cache

from os import stat

import requests

import json

import sys

import webbrowser

import requests_oauthlib

import final_secrets

import final_newsapi

import time

from requests_oauthlib import OAuth1

from requests_oauthlib import OAuth2Session

from geopy.geocoders import Nominatim

import requests

from requests.auth import HTTPBasicAuth

from oauthlib.oauth2 import BackendApplicationClient

from requests_oauthlib import OAuth2Session

# Data Structure
Binary tree is the data structure that is deployed into the main program. Same product category is required for the construction of each binary tree structure. Each node represents a single product whose attributes consist of productId, productName, productType, productPrice, productFulfillment, productDelivery, left, right and parent. 

productId: a set of numbers that made up of several integers

productName: a set of descriptions about the features of same-type product

productType: the category of a product, whereas the category must be same within one binary tree

productPrice: the regular price of a product

productFulfillment: the current status of the product fulfillment, including the number of the products stored in the targte site

productDelivery: the condition whether the product can be delivered to home or not

left: the left-child node(product)

right:  the right-child node(product)

parent: the parent node(product)


