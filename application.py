from flask import Flask, render_template, request, flash, redirect, url_for
import random
import requests
from bs4 import BeautifulSoup
import re
import os
import xml
 
import transformers
from transformers import pipeline

application = app = Flask(__name__)
app.secret_key = "Polymath"


classifier = None
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

  files = re.findall('href="/wiki/\w*"', text)
  lst = sorted(x for x in (files))

  for i in range(len(lst)):
    lst[i] = (lst[i][6:])[:-1]
    lst[i] = lst[i][6:]
  related_articles = lst

  res = (topic, content, related_articles)
  return res


def get_subject_list():
  subjects = ['Cooking', 'Economics', 'biology', 'chemistry', 'physics', 'sports', 'tennis', 'basketball', 'countries', 'football', 'math', 'geography', 'literature', 'music', 'nature', 'movies', 'transportation', 'politics', 'philosophy', 'aeronautics', 'art', 'history', 'computer science', 'engineering', 'dance', 'neuroscience', 'law']
  return subjects

def fix_periods_issue(text):
  return text.replace(' .', '.')


def check_article_exists(topic):
  url = 'https://en.wikipedia.org/wiki/' + topic
  page = requests.get(url)

  # scrape webpage
  soup = BeautifulSoup(page.content, 'html.parser')
  list(soup.children)
  text = str(soup.find_all('p'))

  content = remove_tags(text)

  files = re.findall('href="/wiki/\w*"', text)
  lst = sorted(x for x in (files))

  if len(lst) == 0:
    return False
  else:
    return True


# This is the main one: 
def topic_information(topic_chosen):
  topic_chosen = "".join(topic_chosen.rstrip().lstrip())

  #topic_chosen = topic_chosen.lower()
  output = ''
  if topic_chosen == 'r':
    topic_chosen = random.choice(get_subject_list())
  output = 'You selected: ' + topic_chosen
  flash(output)

  if not check_article_exists(topic_chosen):
    flash("This is not a valid topic name. Try capitalizing proper nouns or entering a different valid topic.")
    return ''
  
  ### SUMMARY CODE
  str_result = ""
  tup = extract_article(topic_chosen)
  summarized = classifier((tup[1])[:850])
  cleaned_topic = topic_chosen.replace('_', ' ')
  str_result += "Here's some info about: " + cleaned_topic + " ... "
  str_result += fix_periods_issue((summarized[0])['summary_text'])
  flash(str_result)

  cleaned_sample = []
  sub_topics_str = " "

  related_topics = tup[2]
  if len(related_topics) > 6:
    related_topics = random.sample(related_topics, 6)

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



def print_topics():
  subjects = get_subject_list()
  str_build_up = ""
  for topic in subjects:
    upper_case_topic = topic[0].upper() + topic[1:]
    str_build_up += upper_case_topic + ", "
  return str_build_up[:len(str_build_up) - 2]
    
@app.route("/home")
def index():
    flash(print_topics())
    global classifier
    classifier = pipeline("summarization")
    return render_template('home.html')

@app.route("/information", methods=["POST", "GET"])
def information():
  topic = request.form['topic']
  flash(topic_information(topic))
  return render_template('search.html')

@app.route("/")
def redirectToHome():
  return redirect(url_for('index'))
  
# topic_information: should give summarization and sub_topics

if __name__ == "__main__":
    #port_choice = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=True)
