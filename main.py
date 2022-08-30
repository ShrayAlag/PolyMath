from flask import Flask, render_template, request, flash
from flask import request
import random
import requests
from bs4 import BeautifulSoup
import re
import xml
 
import transformers
from transformers import pipeline

app = Flask(__name__)
app.secret_key = "Polymath"



sub_topics = []
def remove_tags(text):
  clean = re.compile('<.*?>')
  return re.sub(clean, '', text)


def extract_article(topic):
  cleaned_topic = topic.replace('_', ' ')
  print("Currently scraping for ", cleaned_topic, " ...")
  url = 'https://en.wikipedia.org/wiki/' + topic
  page = requests.get(url)

  # scrape webpage
  soup = BeautifulSoup(page.content, 'html.parser')
  list(soup.children)
  text = str(soup.find_all('p'))

  content = remove_tags(text)

  """
  files = re.findall('href="/wiki/\w*"', text)
  lst = sorted(x for x in (files))

  for i in range(len(lst)):
    lst[i] = (lst[i][6:])[:-1]
    lst[i] = lst[i][6:]
  related_articles = lst

  """
  res = (topic, content)
  return res


def extract_init_topics(topic):
  url = 'https://en.wikipedia.org/wiki/' + topic
  page = requests.get(url)

  # scrape webpage
  soup = BeautifulSoup(page.content, 'html.parser')
  list(soup.children)
  text = str(soup.find_all('p'))

  content = remove_tags(text)

  files = re.findall('href="/wiki/\w*"', text)
  lst = sorted(x for x in (files))

  for i in range(len(lst)):
    lst[i] = (lst[i][6:])[:-1]
    lst[i] = lst[i][6:]

  related_articles = lst
  return related_articles

def get_subject_list():
  subjects = ['Cooking', 'Economics', 'biology', 'chemistry', 'physics', 'sports', 'tennis', 'basketball', 'countries', 'football', 'math', 'geography', 'literature', 'music', 'nature', 'movies', 'transportation', 'politics', 'philosophy', 'aeronautics', 'art', 'history', 'computer science', 'engineering', 'dance', 'neuroscience', 'law']
  return subjects

# This is the main one: 
def topic_information(topic_chosen):
  orig_topic = topic_chosen
  topic_chosen = topic_chosen.lower()
  output = ''
  if topic_chosen == 'r':
    topic_chosen = random.choice(get_subject_list())
    output = 'You selected: ' + topic_chosen
  else:
    output = 'You selected: ' + orig_topic
  flash(output)

  # sub_topic_chosen = request.args.get("sub_topic", "")
  
  ### SUMMARY CODE
  classifier = pipeline("summarization")
  str_result = ""
  tup = extract_article(topic_chosen)
  summarized = classifier((tup[1])[:2048])
  cleaned_topic = topic_chosen.replace('_', ' ')
  str_result += "Here's some info about: " + cleaned_topic + " ... "
  str_result += (summarized[0])['summary_text']
  flash(str_result)

  cleaned_sample = []
  sub_topics_str = " "

  related_topics = random.sample(extract_init_topics(topic_chosen), 6)

  for i in range(len(related_topics)):
    new = ''
    for ch in related_topics[i]:
      if ch == '_':
        new += ' '
      else:
        new += ch
    sub_topics_str += str(i + 1) + ". " + new + " "
    # UNCOMMENT if want line space break halfway in the list
    # if i == 2:
    #   sub_topics_str += "<br/>"
    cleaned_sample.append(new)
  
  sub_topics = cleaned_sample

  
  #if topic_chosen not in get_subject_list() and topic_chosen not in sub_topics:
   # return "Not Found. Please try entering one of the subjects above."
  # yay, we found the next thingy
  final_out = 'Here are some concepts related to your chosen topic: '
  for i in range(len(sub_topics)):
    if i != len(sub_topics)-1:
      final_out += sub_topics[i]
      final_out += ', '
    else:
      final_out += sub_topics[i]
  return final_out

## To-Dos: continue styling + use fonts, add a way to check that the article does have a wiki. Add a learn more about this 


def check_topic_in_wiki():
  return NotImplementedError()





def info_abt_sub_topic():
  sub_topic_chosen = request.args.get("sub_topic", "") 
  if sub_topic_chosen: #if not none
    return sub_topic_information(sub_topic_chosen)
  else:
    return ""

def sub_topic_information(topic):
  classifier = pipeline("summarization")
  str_result = ""
  tup = extract_article(topic)
  summarized = classifier((tup[1])[:2048])
  cleaned_topic = topic.replace('_', ' ')
  str_result += "Here's some info about:" + cleaned_topic
  str_result += (summarized[0])['summary_text']
  str_result += " Here are some articles related to" + topic

  sub_sample = random.sample(tup[2], 6)
  cleaned_sample = []
  for i in range(len(sub_sample)):
    new = ''
    for ch in sub_sample[i]:
      if ch == '_':
        new += ' '
      else:
        new += ch
    cleaned_sample.append(new)
  counter = 1
  for item in cleaned_sample:
    str_result += {counter} + " " + {item}
    counter += 1
  str_result += " "
  str_result += "Enter above to explore any subtopic"
  str_result += "Thanks for using Polymath!"
  return str_result

def print_topics():
  subjects = get_subject_list()
  str_build_up = ""
  for topic in subjects:
    upper_case_topic = topic[0].upper() + topic[1:]
    str_build_up += upper_case_topic + ", "
  return str_build_up[:len(str_build_up) - 2]

def info_abt_topic():
  topic_chosen = request.args.get("topic", "") 
  sub_topic_chosen = request.args.get("sub_topic", "") 
  if topic_chosen or sub_topic_chosen: #if not none
    return topic_information(topic_chosen) + """<form action="" method="get">
            Which topic would you like to keep exploring (enter topic name):  <input type="text" name="sub_topic">
            <input type="submit" value="Get Summary">
        </form>"""
  else:
    return ""
    
@app.route("/home")
def index():
    flash(print_topics())
    return render_template('home.html')

@app.route("/information", methods=["POST", "GET"])
def information():
  topic = request.form['topic']
  flash(topic_information(topic))
  return render_template('search.html')

# topic_information: should give summarization and sub_topics

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8090, debug=True)


# def client():
#   classifier = pipeline("summarization")
#   print("Hi, welcome to Polymath!")
#   # option for random info (any subject) or explore particular subject

#   subjects = ['cooking', 'economics', 'biology', 'chemistry', 'physics', 'sports', 'tennis', 'basketball', 'countries', 'football', 'math', 'geography', 'literature', 'music', 'nature', 'movies', 'transportation', 'politics', 'philosophy', 'aeronautics', 'art', 'history', 'computer_science', 'engineering', 'dance', 'neuroscience', 'law']
#   print("Polymath is a curiosity network that lets you learn about new ideas and topics by exploring the web.")
#   print()
#   print("Here are some common topics!: ", subjects)
#   init_topic = input("Pick one to get started or type in 'r' to explore a random one: ")
#   if init_topic == 'r':
#     init_topic = random.choice(subjects)
#   related_topics = random.sample(extract_init_topics(init_topic), 6)

#   cleaned_sample = []
#   for i in range(len(related_topics)):
#     new = ''
#     for ch in related_topics[i]:
#       if ch == '_':
#         new += ' '
#       else:
#         new += ch
#     cleaned_sample.append(new)

#   print("Here are some related topics to start exploring for the category of: ", init_topic)
#   counter = 1
#   for item in cleaned_sample:
#     print(counter, item)
#     counter += 1
#   print()
#   user_next = input("Which topic would you like to keep exploring (enter a number or enter nothing to quit): ")
#   topic = ''
#   if user_next != "":
#     topic = related_topics[int(user_next)-1]
#   else:
#     quit()

#   while True:
#     tup = extract_article(topic)
#     summarized = classifier((tup[1])[:1024])
#     cleaned_topic = topic.replace('_', ' ')
#     print("Here's some info about: ", cleaned_topic)
#     print((summarized[0])['summary_text'])
#     print("Here are some related articles: ")
#     sub_sample = random.sample(tup[2], 6)
#     cleaned_sample = []
#     for i in range(len(sub_sample)):
#       new = ''
#       for ch in sub_sample[i]:
#         if ch == '_':
#           new += ' '
#         else:
#           new += ch
#       cleaned_sample.append(new)
#     counter = 1
#     for item in cleaned_sample:
#       print(counter, item)
#       counter += 1
#     print()
#     user_next = input("Which topic would you like to keep exploring (enter a number or enter nothing to quit): ")
#     if user_next != "":
#       topic = sub_sample[int(user_next)-1]
#     else:
#       break

#   print("Thanks for using Polymath!")

# def print_topics():
#   subjects = get_subject_list()
#   str_build_up = ""
#   for topic in subjects:
#     upper_case_topic = topic[0].upper() + topic[1:]
#     str_build_up += upper_case_topic + ", "
#   return str_build_up[:len(str_build_up) - 2]

# def info_abt_topic():
#   topic_chosen = request.args.get("topic", "") 
#   if topic_chosen: #if not none
#     return topic_information(topic_chosen) + """<form action="" method="get">
#             Which topic would you like to keep exploring (enter topic name):  <input type="text" name="sub_topic">
#             <input type="submit" value="Get Summary">
#         </form>"""
#   else:
#     return ""


# def fahrenheit_from(celsius):
#     """Convert Celsius to Fahrenheit degrees."""
#     try:
#         fahrenheit = float(celsius) * 9 / 5 + 32
#         fahrenheit = round(fahrenheit, 3)  # Round to three decimal places
#         return str(fahrenheit)
#     except ValueError:
#         return "invalid input"


# @app.route("/")
# def index():
#     celsius = request.args.get("celsius", "")
#     if celsius:
#         fahrenheit = fahrenheit_from(celsius)
#     else:
#         fahrenheit = ""
#     return (
#         """<form action="" method="get">
#                 Celsius temperature: <input type="text" name="celsius">
#                 <input type="submit" value="Convert to Fahrenheit">
#             </form>"""
#         + "Fahrenheit: "
#         + fahrenheit
#     )


# if __name__ == "__main__":
#     app.run(host="127.0.0.1", port=8080, debug=True)

#####################################################################

# from flask import Flask

# app = Flask(__name__)
