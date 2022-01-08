###################################
###  Name: Jiawen Zhang         ###
###  UMID: 67753497             ###
###  e-mail: jiawenz@umich.edu  ###
###  updated date: 12/8/2021    ###
###################################

#import packages
from functools import cache
from os import stat
import requests
import json
import sys
import webbrowser

import requests_oauthlib
# import final_secrets
# import final_newsapi
import time
from requests_oauthlib import OAuth1
from requests_oauthlib import OAuth2Session
from geopy.geocoders import Nominatim

import requests
from requests.auth import HTTPBasicAuth
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

#request info
headers = {
    "User-Agent": "UMSI 507 Course Project - Python Scraping",
    "From": "jiawenz@umich.edu",
    "Course-Info": "https://si.umich.edu/programs/courses/507"
}

#API
#clientKey = final_secrets.KROGER_CLIENT_ID
#clientSecret = final_secrets.KROGER_CLIENT_SECRET
#Redirect = final_secrets.REDIRECT_URL

clientKey = "jiawenzhang-8a5f94b6ab72a32f0764988af8fc54ac5327040114974585999"
clientSecret = "umftmKynHfq8bHStoah2l39Kj3U1h3wO2HsYFWub"
Redirect = "myapp://callback2//"

#cache contents of Kroger shopping system
CACHE_KROGER_LOC = "cache_kroger_location.json"
CACHE_DICT_LOC = {}

CACHE_FILE_NAME = "cache_recipes.json"
CACHE_DICT = {}

CACHE_FILE_KROGER = "cache_kroger.json"
CACHE_DICT_KROGER = {}

CACHE_FILE_SECRET = "cache_secret.json"
CACHE_DICT_SECRET = {}

oauth = OAuth1(clientKey,clientSecret,resources_owner_key=access_token,resource_owner_secret=access_token_secret)

#global functions


## Part I. Caching ##

### open the cache file, and loads it into a json format if it exists. Otherwise, a new cache dictionary
### will be created if it is not.
def load_Cache(cacheFile):
    try:
        cache_file = open(cacheFile,"r")
        cache_fileContents = cache_file.read()
        cache = json.loads(cache_fileContents)
        cache_file.close()
    except:
        cache = {}
    return cache

### save the current status of the cache to the disk
def save_Cache(cache,cacheFile):
    cache_file = open(cacheFile,"w")
    writtenContents = json.dumps(cache)
    cache_file.write(writtenContents)
    cache_file.close()
    time.sleep(.2)

### check the cacge file to see whether the saved result serves a url or not. Return the result if it is
### found; otherwise, a new request will be sent, and then the response results will be saved and returned
def makeCache_URLrequest(url,cache,cacheFile):
    if (url in cache.keys()):
        return cache[url]
    else:
        response = requests.get(url)
        cache[url] = response.text
        save_Cache(cache,cacheFile)
        return cache[url]


## Part II. Web APIs & Authentication ##

### construct the unique key to guarantee identify an API request via its base-url and params.
def construct_uniKey(baseURL, params):
    formatted_strings = []
    connector ='_'
    for index in params.keys():
        formatted_strings.append("{}={}".format(index, params[index]))
    formatted_strings.sort()
    uni_key = baseURL + connector + connector.join(formatted_strings)
    return uni_key

### save an authorization token into the secret cache, it is a helper function for the below <>
def token_saver(token):
    CACHE_DICT_SECRET["token"] = token
    with open(CACHE_DICT_SECRET, "w") as outfile:
        outfile.write(json.dumps(CACHE_DICT_SECRET, indent=2))
    outfile.close()

###acquire the location info about the Kroger shopping mall via my location
def acquire_mall_locationid(zipCode):
    # acquire the data about the latitude and longitude of the Kroger location via the address
    ### loc = Nominatim(user_agent="GetLoc")
    ### getLoc = loc.geocode("2641 Plymouth Rd, Ann Arbor")
    ### Krogerlatitude = location.latitude
    ### Krogerlongitude = location.longitude

    location_url = "https://api.kroger.com/v1/locations"
    params = {
        "filter.zipCode.near": zipCode,
        "filter.limit": 1,# only show one item
        "filter.chain": "Kroger"
    }
    request_key = construct_uniKey(location_url, params)

    responses = []
    new_response = oauth.get(request_key)
    CACHE_DICT_LOC[request_key] = new_response.json()
    with open(CACHE_DICT_LOC, "w") as outfile:
        outfile.write(json.dumps(CACHE_DICT_LOC, indent=2))
    outfile.close()
    response = CACHE_DICT_LOC[request_key]
    responses.append(response)

    return responses

### use OAuth2 to authorize and add recipe ingredients to Kroger cart
def acquire_KrogerAuth(location_info):
    CACHE_DICT_SECRET = load_Cache(CACHE_FILE_SECRET)

    kroger_auth_url = "https://api.kroger.com/v1/connect/oauth2/authorize"
    kroger_token_url = "https://api.kroger.com/v1/connect/oauth2/token"

    scopes =["profile.compact", "product.compact", "art.basic:write"]
    extra_info ={"client_id": clientKey, "client_secret":clientSecret}

    if "token" in CACHE_DICT_SECRET.keys():
        token = CACHE_DICT_SECRET["token"]
        oauth = OAuth2Session(client_id=clientKey, token=token, auto_refresh_url=kroger_token_url,
                              auto_refresh_kwargs=extra_info, token_updater=token_saver)

    ### create refreshable token and save it to cache ###
    else:
        oauth = OAuth2Session(client_id=clientKey,edirect_uri=Redirect,scope=scopes)
        authorization_url, state = oauth.authorization_url(kroger_auth_url)

        flag_launch = True
        while flag_launch == True:
            input_notice = "Enter launch (L) to launch authentication in a browser -- or exit (E) to exit the program: "
            launch_input = input(input_notice)

            if (launch_input.lower() == "exit" or launch_input.lower() == "e"):
                print("Goodbye.")
                sys.exit()
            elif (launch_input == "launch" or launch_input == "l"):
                flag_launch = False # break out of loop
                break
            elif (
                launch_input != "exit" and launch_input != "e" and
                launch_input != "launch" and launch_input != "l"
            ):
                print(f"[Error] Please enter valid input launch (L) or exit (E)")

        webbrowser.open(authorization_url, new=2, autoraise=True)
        print()
        # user will enter full redirect URI
        callback = input("Please input the full callback URL from the browser: ")
        token = oauth.fetch_token(kroger_token_url, authorization_response=callback, client_secret=clientSecret)
        # negative required for refreshing
        token["expires_in"] = -300
        token_saver(token)

    ### product information from kroger ###
    baseurl_products = "https://api.kroger.com/v1/products"
    params = {}
    params["filter.term"] = input("Please input your target")
    params["filter.locationId"] = location_info[0]["data"][0]["locationId"]
    params["filter.brand"] = "Kroger"
    params["filter.fulfillment"] = "sth"
    params["filter.limit"] = 1000 # only show one item
    responses = []
    
    request_key = construct_uniKey(baseurl_products, params)
    if request_key in CACHE_DICT_KROGER.keys():
        response = CACHE_DICT_KROGER[request_key]
    else:
        new_response = oauth.get(request_key)
        CACHE_DICT_KROGER[request_key] = new_response.json()
        with open(CACHE_FILE_KROGER, "w") as outfile:
            outfile.write(json.dumps(CACHE_DICT_KROGER, indent=2))
        outfile.close()
        response = CACHE_DICT_KROGER[request_key]

    responses.append(response)

    return responses

## Part III. the construction of Kroger products in different types ##

## the construction of the tree construction of different types of products

def user_input_info(productID=None,productName=None,productType=None,productPrice=None,Storage=None,Delivery=None):
    result = {
        "product_id": productID,
        "product_name": productName,
        "product_type": productType,
        "product_price": productPrice,
        "product_storage": Storage,
        "product_delivery": Delivery
    }
    return result

class shopping_TreeNode:

    def __init__(self,productId=None,productName=None,productType=None,productPrice=None,productFulfillment=None,productDelivery=None,left=None,right=None,parent=None):
        self.ID = productId
        self.Name = productName
        self.Type = productType
        self.Price = productPrice
        self.Fulfillment = productFulfillment
        self.Delivery = productDelivery

        self.leftChild = left
        self.rightChild = right
        self.parent = parent

    def hasLeftChild(self):
        return self.leftChild

    def hasRightChild(self):
        return self.rightChild

    def hasAnyChildren(self):
        return (self.leftChild or self.rightChild)

    def hasBothChildren(self):
        return (self.leftChild and self.rightChild)

    def isLeftChild(self):
        return (self.parent and self.parent.leftChild == self)

    def isRightChild(self):
        return (self.parent and self.parent.rightChild == self)

    def isRoot(self):
        return not self.parent

    def isLeaf(self):
        return not (self.rightChild or self.leftChild)

    def shift_NodeInfo(self,productId,leftchild,rightchild):
        self.ID = productId
        self.leftChild = leftchild
        self.rightChild = rightchild
        if self.hasLeftChild():
            self.leftChild.parent = self
        if self.hasRightChild():
            self.rightChild.parent = self

class construct_BinaryTree(shopping_TreeNode):

    def __init__(self,productId=None,productName=None,productType=None,productPrice=None,productFulfillment=None,productDelivery=None,left=None,right=None,parent=None,targetDict={}):
        super().__init__(productId,productName,productType,productPrice,productFulfillment,productDelivery,left,right,parent)
        self.Root = None
        self.Size = 0

    def length(self):
        return self.Size

    # print out the size 
    def __len__(self):
        return self.Size#specially used for object-oriented programming

    def __iter__(self):
        return self.Root.__iter__() #?

    def insertNode(self,productId,targetDict={}):
        if self.Root:
            self.insertNode_helper(self.Root,targetDict=targetDict)
        else:
            self.Root = shopping_TreeNode(
                productId=targetDict["productId"],
                productName=targetDict["description"],
                productType=targetDict["product_type"],
                productPrice=targetDict["product_price"],
                productFulfillment=targetDict["product_storage"],
                productDelivery=targetDict["product_delivery"],
                left=None,
                right=None,
                parent=None
            )
        self.Size += 1


    def insertNode_helper(self,currentNode=None,targetDict={}):
        ID = targetDict["productId"]
        name = targetDict["description"]
        category = targetDict["product_type"]
        price = targetDict["product_price"]
        fulfillment = targetDict["product_storage"]
        delivery = targetDict["product_delivery"]

        if price <= currentNode.Price:
            #deep search in the sub-left tree
            if currentNode.hasLeftChild():
                self.insertNode_helper(currentNode=self.leftChild,targetDict=targetDict)
            #insert the left leaf node
            else:
                currentNode.leftChild = shopping_TreeNode(     
                    productId=ID,              
                    productName=name,
                    productType=category,
                    productPrice=price,
                    productFulfillment=fulfillment,
                    productDelivery=delivery,
                    left=None,
                    right=None,
                    parent=currentNode
                )
        else:
            #deep search in the sub-right tree
            if currentNode.hasRightChild():
                self.insertNode_helper(currentNode=self.rightChild,targetDict=targetDict)
            #insert the right leaf node
            else:
                currentNode.rightChild = shopping_TreeNode(
                    productId=ID,
                    productName=name,
                    productType=category,
                    productPrice=price,
                    productFulfillment=fulfillment,
                    productDelivery=delivery,
                    left=None,
                    right=None,
                    parent=currentNode
                )

    def extractNode(self,productId):
        if self.Root:
            response = self.extractNode_helper(currentNode=self.Root,targetDict={})
            if response:
                return response.payload #?
            else:
                return None
        else:
            return None

    def extractNode_helper(self,currentNode=None,targetDict={}):
        ID = targetDict["productId"]
        name = targetDict["description"]
        category = targetDict["product_type"]
        price = targetDict["product_price"]
        fulfillment = targetDict["product_storage"]
        delivery = targetDict["product_delivery"]

        if not currentNode:
            return None
        elif (ID == currentNode.productId and 
              name == currentNode.productName and
              category == currentNode.productType and
              price == currentNode.productPrice and
              fulfillment == currentNode.productFulfillment and
              delivery == currentNode.productDelivery
        ):
            return currentNode
        else:
            if price <= currentNode.productPrice:
                return self.extractNode_helper(currentNode=self.leftChild,targetDict=targetDict)
            else:
                return self.extractNode_helper(currentNode=self.rightChild,targetDict=targetDict)

    def __getitem__(self,productId):
        return self.get(productId)

class searchBST(shopping_TreeNode):

    def __init__(self,productId=None,productName=None,productType=None,productPrice=None,productFulfillment=None,productDelivery=None,left=None,right=None,parent=None,targetDict={}):
        super().__init__(productId,productName,productType,productPrice,productFulfillment,productDelivery,left,right,parent)

    def check_Existence(self,targetDict):
        if (self.ID == targetDict["product_id"] and
            self.Name == targetDict["product_name"] and
            self.Type == targetDict["product_type"] and
            self.Price == targetDict["product_price"] and
            self.Fulfillment == targetDict["product_storage"] and
            self.Delivery == targetDict["product_delivery"]
        ):
            ExistenceStatus = True
        else:
            ExistenceStatus = False

        return ExistenceStatus

    def tell_existenceStatus(self):
        if (self.check_Existence):
            status = "exists"
        else:
            status = "does not exist"

        return f"Customer's target product {status} in the online Kroger shopping system."

    def design_PriceOrder(self):
        status = True
        output_result = None
        user_input = input("Please input your perferred searching strategy via price. Choose find alternative via a cheapest one or a expensive one. If the first one, enter the integer <1>, if the second one, enter <2>")
        while status:
            if user_input == 1:
                output_result = "cheap"
                status = False
            elif user_input == 2:
                output_result = "expensive"
                status = False
            else:
                user_input = input("Your input does meet the requirements. Choose find alternative via a cheapest one or a expensive one. If the first one, enter the integer <1>, if the second one, enter <2>")

        return output_result

    # locate the target node in the tree structure
    #def find_Alter_or_Origin(self,targetDict={}):
        #selected_product = None
        #if (self.check_Existence):
        #    selected_product = targetDict
        #else:
        #    target_type = targetDict["product_type"]
        #    target_price = targetDict["product_price"]
        #    price_order = self.design_PriceOrder
        #    if price_order == "cheap":
        #        decision_status = self.hasAnyChildren
        #        while decision_status:
        #            # current product is more expensive than target price
        #            if self.Price >= target_price:
        #                currentNode = self.leftChild
                    #current product is less expensive than target price
        #            elif self.Price < target_price:
        #                if self.hasLeftChild:
        #                    currentNode = self.leftChild
        #                elif self.hasRightChild:
        #                    currentNode = self.rightChild
        #     elif price_order == "expensive":
        #         while self.hasAnyChildren:
        #             if self.Price >= target_price:
        #                 currentNode = self.



if __name__ == "__main__":
    # Load the cache, save in global variable
    CACHE_DICT_LOC = load_Cache(CACHE_KROGER_LOC)
    CACHE_DICT_KROGER = load_Cache(CACHE_FILE_KROGER)

    ## the acquisition of all the related info about one Kroger site
    check_status = True
    input_zipCode = input("Please input a zipcode. It helps us locate a nearby Kroger Mall.")
    while check_status:
        if (type(input_zipCode) == str and input_zipCode.isnumeric()):
            input_zipCode = int(input_zipCode)
        elif (type(input_zipCode) == int and len(input_zipCode) == 5):
            check_status = False
            break
        else:
            input_zipCode = input("Your input zipcode is not valid, please try another 5-interger zipcode.")
    
    location_info = acquire_mall_locationid(input_zipCode)

    ## the acquisition of 1000 products in the target Kroger site
    product_info = acquire_KrogerAuth(location_info)
    # Notice: <product_info_header> is a list
    product_info_header = product_info["data"]
    temp_classification = {}
    for single_product in product_info_header:
        type_names = single_product["categories"]
        for type_name in type_names:
            if type_name not in temp_classification.keys():
                temp_classification[type_name] = []
                temp_classification[type_name].append(single_product)
            else:
                temp_classification[type_name].append(single_product)
    
    product_classification = {}
    for category in temp_classification.keys():
        if category not in product_classification.keys():
            product_classification[category] = []
        else:
            for product in temp_classification[category]:
                single_product_info = user_input_info(productName=product["description"],
                                                      productType=category,
                                                      productPrice=product["items"][0]["price"]["regular"],
                                                      Storage = product["aisleLocations"][0]["number"],
                                                      Delivery=product["items"][0]["fulfillment"]["delivery"]
                )
            product_classification[category].append(single_product_info)

    ## the construction of different product types' binary tree structure