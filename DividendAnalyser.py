import requests
import json
import pandas
from datetime import datetime

# Read symbols from the JSON file
with open('symbols.txt') as file:
    symbols = file.read().split('\n')

# Read config from JSON file
with open('config.json') as file:
    config = json.load(file)

# Prepare the request parameters
params = {
    'symbols': ",".join(symbols)
}

headers = {
    'X-RapidAPI-Key': config['apiKey'],
    'X-RapidAPI-Host': 'seeking-alpha.p.rapidapi.com'
}

fields = config["fields"]
result = {}
currentTime = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")

# Iterate over field keys which are the api endpoints to fetch data from
for apiEndpoint in fields:
    # Make the API request
    response = requests.get(config['url'] + apiEndpoint, params=params, headers=headers)

    # Check if the request was successful
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        exit()

    # Parse the response JSON
    data = json.loads(response.text)["data"]

    # Process the data
    for symbolData in data:
        symbolId = symbolData['id']
        if symbolId not in result:
            result[symbolId] = { 'Fetch Time': currentTime }

        for keyDisplayName in fields[apiEndpoint]:
            keyHierarchy = fields[apiEndpoint][keyDisplayName]
            keys = keyHierarchy.split(':')
            
            objectData = symbolData['attributes']
            for key in keys:
                if objectData is None:
                    break
                objectData = objectData[key]
                if type(objectData) == list:
                    objectData = objectData[0]
            
            result[symbolId][keyDisplayName] = objectData

dataFrame = pandas.DataFrame.from_dict(result, orient='index')

outputFileName = config['outputFile']
dataFrame.to_excel(outputFileName, index=True)
