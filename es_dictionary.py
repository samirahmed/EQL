import json, requests, yaml
from datetime import datetime,timedelta

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
    def __init__(self, nlq): 
        recipients = nlq.recipients
        sender = nlq.sender
        start_time = None
        end_time = None
        body_terms = []

        if nlq.date_is_parsed:
            if nlq.date_comparator == "before":
                end_time = nlq.date
            elif nlq.date_comparator == "after":
                start_time = nlq.date
            elif nlq.date_comparator == None:
                if nlq.scope == "day":
                    start_time = nlq.date
                    endDate = datetime.strptime(nlq.date, "%Y-%m-%dT%H:%M:%S-07:00") + timedelta(days=1)
                    end_time = endDate.strftime("%Y-%m-%dT%H:%M:%S-07:00")


        if nlq.first_text:
            body_terms.append(nlq.first_text)
        if nlq.second_text:
            body_terms.append(nlq.second_text)
        
        boolDict={}
        shouldList = []
        mustList = []

        if recipients:
            mustList.append(self.makeTerm("recipients", recipients))
        if sender:
            mustList.append(self.makeTerm("sender", sender))
        if body_terms:
            for i in range (0, len(body_terms)):
                mustList.append(self.makeTerm("subject_body",body_terms[i]))

        if nlq.has_attachments is not None:
            mustList.append(self.makeTerm("has_attachment", nlq.has_attachments))
        if nlq.attachments:
            mustList.append(self.makeMatch("attachments", nlq.attachments))

        if nlq.has_links is not None:
            mustList.append(self.makeTerm("has_links", nlq.has_links))
        if nlq.link:
            mustList.append(self.makeMatch("links", nlq.link))

        if start_time or end_time:
            mustList.append(self.makeRange(start_time, end_time))

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
        term[name]["value"] = str(value).lower()
        return {"term": term}

    def makeRange(self, start, end):
        range = {}
        range["sent_time"] = {}
        if start is not None:
            range["sent_time"]["from"] = start
        if end is not None:
            range["sent_time"]["to"] = end
        return {"range": range}

    def makeMatch(self, name, value):
        match = {}
        match[name]={}
        match[name]["query"] = str(value).lower()
        return {"match": match}

    def extract(self, hits):
      return json.loads(hits["_source"]["raw_data"])

    def sendQuery(self):
        payload = self.json()
        print GetConfig()["emailDbUrl"]
        print payload
        
        r = requests.post(GetConfig()["emailDbUrl"], data = payload)
        
        try:
          body = json.loads(r.content)
          print json.dumps(body, indent=2)
          return [self.extract(item) for item in body["hits"]["hits"]]
        except Exception,e: 
          print str(e)
          return []
