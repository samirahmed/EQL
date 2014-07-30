from faker import Factory
from datetime import datetime
import marisa_trie as trie

faker = Factory.create()
all_contacts = trie.Trie(set(open("./contacts.txt",'r').readlines()))

def fake_contact_resolution(prefix):
  global all_contacts
  return str(all_contacts.keys(unicode(prefix)))

def fake_contact(times):
  global faker
  contacts = []
  for times in range(times):
    contacts.append({
      "name" : faker.first_name() + " " + faker.last_name(),
      "email" : faker.email()
    });
  return contacts

def fake_search():
  global faker
  text = faker.text()
  search = {} 
  emails = []
  for times in range(len(faker.text()) % 5):
    emails.append({
    "to": fake_contact(2),
    "cc": fake_contact(4),
    "from": fake_contact(1)[0],
    "body": text,
    "subject": faker.sentence(),
    "body_preview": " ".join(text.split()[:10]),
    "has_attachment" : len(text) % 2 == 0,
    "has_links" : False,
    "sent_time" : datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
    "deeplink" : "outlook://125125kj12kj124124125"
    });
  result = { 
    "parse_success": True, 
    "duration" : 0.2, 
    "count" : len(emails)
  }

  search["result"] = result
  search["emails"] = emails
  return search
