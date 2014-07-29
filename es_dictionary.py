import json
import requests
import yaml

config = None

def GetConfig():
    global config
    if config is None:
        config = yaml.load(open("config.yaml"))
    return config

class ElasticSearchQuery:
    query = {}
    config = None

    # create your query. Pass null for any unused values
    def __init__(self, recipients, sender, sendTimeStart, sendTimeEnd, bodyTerms):
        boolDict={}
        shouldList = []
        mustList = []

        if recipients is not None:
            for i in range (0, len(recipients)):
                shouldList.append(self.makeTerm("recipients", recipients[i]))
        if sender is not None:
            shouldList.append(self.makeTerm("sender", sender))
        if bodyTerms is not None:
            for i in range (0, len(bodyTerms)):
                shouldList.append(self.makeTerm("body", bodyTerms[i]))
        if sendTimeStart is not None or sendTimeEnd is not None:
            mustList.append(self.makeRange(sendTimeStart, sendTimeEnd))

        boolDict["should"] = shouldList
        boolDict["must"] = mustList
        self.query["bool"] = boolDict

    def __str__(self):
        return str(self.properties())

    def properties(self):
        return {"query": self.query}

    # use this to generate the json payload for your query
    def json(self):
        return json.dumps(self.properties(), indent=2)

    def makeTerm(self, name, value):
        term = {}
        term[name]={}
        term[name]["value"] = value.lower()
        return {"term": term}

    def makeRange(self, start, end):
        range = {}
        range["dateSent"] = {}
        if start is not None:
            range["dateSent"]["from"] = start
        if end is not None:
            range["dateSent"]["to"] = end
        return {"range": range}

    def sendQuery(self):
        r = requests.post(GetConfig()["emailDbUrl"], data = self.json(), stream=True)
        return r.content