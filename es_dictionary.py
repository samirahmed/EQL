import json, requests, yaml, calendar, re
from datetime import datetime,timedelta,date

config = None

def GetConfig():
    global config
    if config is None:
        config = yaml.load(open("config.yaml"))
    return config

class ElasticSearchQuery:
    user_query = None
    query = {}
    suggestionQuery = {}
    config = None
    body_terms = None

    # create your query. Pass null for any unused values
    def __init__(self, nlq):
        self.user_query = nlq.query
        recipients = nlq.recipients
        sender = nlq.sender
        start_time = None
        end_time = None
        min_should_match = 0
        body_terms = []

        if nlq.date_is_parsed:
            if nlq.date_comparator == "before":
                end_time = nlq.date
            else:
                start_time = nlq.date
                if not "after" == nlq.date_comparator:
                    if nlq.scope == "day":
                        endDate = datetime.strptime(nlq.date, "%Y-%m-%dT%H:%M:%S-07:00") + timedelta(days=1)
                        end_time = endDate.strftime("%Y-%m-%dT%H:%M:%S-07:00")
                    elif nlq.scope == "month":
                        endDate = add_months(datetime.strptime(nlq.date, "%Y-%m-%dT%H:%M:%S-07:00"), 1)
                        end_time = endDate.strftime("%Y-%m-%dT%H:%M:%S-07:00")

        if nlq.first_text:
            body_terms.append(nlq.first_text)
        if nlq.second_text:
            body_terms.append(nlq.second_text)
        
        boolDict={}
        shouldList = []
        mustList = []

        if recipients:
            mustList.append(self.makeMatch("recipients", recipients, True))
            self.suggestionQuery["recipients"] = self.makeSuggestion("recipients", recipients)
        if sender:
            mustList.append(self.makeMatch("sender", sender, True))
            self.suggestionQuery["sender"] = self.makeSuggestion("sender", sender)
        if body_terms:
            for i in range (0, len(body_terms)):
                mustList.append(self.makeMatch("subject_body",body_terms[i],False))
                self.suggestionQuery["subject_body" + str(i)] = self.makeSuggestion("subject_body",body_terms[i])

        if nlq.has_attachments is not None:
            mustList.append(self.makeTerm("has_attachment", nlq.has_attachments))
        if nlq.attachments:
            mustList.append(self.makeMatch("attachments", nlq.attachments,False))
            self.suggestionQuery["attachments"] = self.makeSuggestion("attachments", nlq.attachments)
        if nlq.has_links is not None:
            mustList.append(self.makeTerm("has_links", nlq.has_links))
        if nlq.link:
            mustList.append(self.makeMatch("links", nlq.link,False))
            self.suggestionQuery["links"] = self.makeSuggestion("links", nlq.link)
        if start_time or end_time:
            mustList.append(self.makeRange(start_time, end_time))

        boolDict["should"] = shouldList
        boolDict["must"] = mustList
        boolDict["minimum_should_match"] = min_should_match
        self.query["bool"] = boolDict
        self.body_terms = body_terms

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

    def makeMatch(self, name, value, useAnd):
        match = {}
        match[name]={}
        match[name]["query"] = str(value).lower()
        match[name]["fuzziness"] = 1
        match[name]["prefix_length"] = 1
        if useAnd:
            match[name]["operator"] = "and"
        return {"match": match}

    def makeSuggestion(self, name, value):
        suggestion = {}
        suggestion["text"] = value
        term = {}
        term["field"] = name
        suggestion["term"] = term
        return suggestion

    def extract(self, hits):
      parsed = json.loads(hits["_source"]["raw_data"])
      body = parsed["body"]

      processed = body
      words = processed.split()

      modified = []

      for term in self.body_terms:
        regex = re.compile("(%s)" % term, re.IGNORECASE)
        for index in range(len(words)):
          if re.match(regex, words[index]):
            words[index] = "<em>" + words[index]  + "</em>"
            modified.append(index)


      if len(modified) < 1:
        return parsed

      first_index = modified[0]
      # welcome to E-the hotel of E_the best place in E-the world
      start = max(first_index-10,0)
      end = min(first_index+10,len(words))

      preview = "..." +  " ".join(words[start:end]) + '...'

      body = " ".join(words)

      parsed["body"] = body
      parsed["body_preview"] = preview
      return parsed

    def getSuggestion(self, suggestion):
        if len(suggestion["options"]) > 0:
            return suggestion["options"][0]
        else:
            return None

    def sendSuggestQuery(self):
        
        suggest = requests.post(GetConfig()["suggestUrl"], data = json.dumps(self.suggestionQuery, indent=2))
        suggestions = []
        suggest_body = json.loads(suggest.content)
        new_query = self.user_query
        terms = []
        for item in suggest_body:
            print item
            if not item == "_shards":
                print suggest_body[item][0]
                if len(suggest_body[item][0]["options"]) > 0:
                    #corrected
                    new_query = new_query.replace(suggest_body[item][0]["text"], suggest_body[item][0]["options"][0]["text"])

        suggestions.append(new_query)
        print suggestions
        return suggestions

    def sendQuery(self):
        payload = self.json()
        print GetConfig()["emailDbUrl"]
        print payload

        try:
          r = requests.post(GetConfig()["emailDbUrl"], data = payload)
          body = json.loads(r.content)
          print json.dumps(body, indent=2)
          total = body["hits"]["total"]
          emails =  [self.extract(item) for item in body["hits"]["hits"]]
          return emails, total
        except Exception,e: 
          print str(e)
          return [] , 0


def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month / 12
    month = month % 12 + 1
    day = min(sourcedate.day,calendar.monthrange(year,month)[1])
    return date(year,month,day)

def resolve_contact(prefix):
  if not prefix or len(prefix) <= 1: 
    return []

  try:
    url = GetConfig()["contactUrl"]
    payload = json.dumps({
      "senders" : 
        {
          "text" : str(prefix).lower(),
          "completion" : 
            {
              "field" : "contact_suggest",
              "fuzzy": False
            }
        }
    }, indent=2)
    
    print url
    print payload
    
    r = requests.post(url, data = payload)

    body = json.loads(r.content)
    options = body["senders"][0]["options"]
    names =  [str(option["text"]) for option in options]
    print names
    return names
  except Exception, e:
    print str(e)
    return []
