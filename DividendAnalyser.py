import requests
import json
import pandas
from datetime import datetime

def split_into_sublists(list, sublist_length):
    return [list[i:i+sublist_length] for i in range(0, len(list), sublist_length)]

# Read config from JSON file
with open('config.json') as file:
    config = json.load(file)

# Read symbols from the JSON file
with open('symbols.txt') as file:
    allSymbols = file.read().split('\n')

# Divide the list of symbols into a list of lists, with a size of 4
allSymbolsSplit = split_into_sublists(allSymbols, 4)

result = {}
currentTime = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
fields = config["fields"]
headers = {
    'X-RapidAPI-Key': config['apiKey'],
    'X-RapidAPI-Host': 'seeking-alpha.p.rapidapi.com'
}

for symbols in allSymbolsSplit:
    # Prepare the request parameters
    params = {
        'symbols': ",".join(symbols)
    }

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
