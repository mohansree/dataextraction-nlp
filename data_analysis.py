#import required libraries
import nltk
nltk.download('punkt')
nltk.download('stopwords')

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from bs4 import BeautifulSoup

import os
import pandas as pd
import requests
import re
import string

#extract title and article from urls
input = pd.read_excel("Input.xlsx")
for index, row in input.iterrows():
  urls = row['URL']
  url_id = row['URL_ID']

  headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0"}

  #make request to url
  try:
    response = requests.get(urls,headers=headers)
  except:
    print("can't get response of {}".format(url_id))

  #make beatifulsoup object
  try:
    soup = BeautifulSoup(response.content, "lxml")
  except:
    print("can't get page of {}".format(url_id))

  #find title of each page
  try:
    title = soup.find('h1').get_text()
  except:
    print("can't get title of {}".format(url_id))
    continue
  print(title)

  #get content of pages
  article = ""

  try:
    blacklist = [
    '[document]',
    'noscript',
    'header',
    'html',
    'meta',
    'head', 
    'input',
    'script',
    'footer',
    'td-header-template-wrap',
    'td-full-screen-header-image-wrap'
    ]
    for p in soup.find_all(name="article"):
      if p.parent.name not in blacklist:
        article += p.get_text()
  except:
    print("can't get text of {}".format(url_id))
  
  article = article.translate(str.maketrans('', '', string.punctuation))

  #save the title and article into text files 
  file_name = "/gdrive/MyDrive/Blackoffer-TestAssignment/TestAssignment/text_file" + str(url_id) + '.txt'
  with open(file_name, 'w') as file:
    file.write(title + '\n' + article)

#Tokenization
text_dir = "/content/drive/MyDrive/intern_project/TestAssignment/TitleArticle"
stopwords_dir = "/content/drive/MyDrive/intern_project/StopWords"
posandneg_dir = "/content/drive/MyDrive/intern_project/MasterDictionary"

for text_file in os.listdir(text_dir):
  with open(os.path.join(text_dir,text_file),'r') as f:
    text = f.read()
    #tokenize the given text file
    word_tokens = word_tokenize(text)

#cleaning text using stopwords
for files in os.listdir(stopwords_dir):
  with open(os.path.join(stopwords_dir,files),'r', encoding='ISO-8859-1') as f:
    stop_words = f.read()
    stop_words = set(stopwords.words('english'))
    filtered_sentence = [word for word in word_tokens if word.lower() not in stop_words]
filtered_sentence = []
for word in word_tokens:
  if word not in stop_words:
    filtered_sentence.append(word)

#store positive and negative words from posandneg_dir
for files in os.listdir(posandneg_dir):
  if files == "positive-words.txt":
    #positive words
    with open(os.path.join(posandneg_dir, files), 'r', encoding='ISO-8859-1') as f:
      pos_words = f.read().splitlines()
      pos_count = " ".join ([w for w in filtered_sentence if w.lower() in pos_words])
      pos_count = pos_count.split(" ")
      positive_score = len(pos_count)
  else:
    #negative words
    with open(os.path.join(posandneg_dir, files), 'r', encoding='ISO-8859-1') as f:
      neg_words = f.read().splitlines()
      neg_count = " ".join ([w for w in filtered_sentence if w.lower() in neg_words])
      neg_count = neg_count.split(" ")
      negative_score = len(neg_count)

polarity_score = (positive_score - negative_score) / ((positive_score + negative_score) + 0.000001)
subjectivity_score = (positive_score + negative_score) / ((len(filtered_sentence)) + 0.000001)

#analysis of readabilty
AVG_SENTENCE_LENGTH = []
PER_OF_COMPLEX_WORDS = []
FOG_INDEX = []
SYLLABLE_PER_WORD = []
COMPLEX_WORD_COUNT = []

def analysis(file):
  with open(os.path.join(text_dir, file), 'r') as f:
    texts = f.read()
    texts = re.sub(r'[^\w\s.]','',texts)
    sentences = texts.split(".")
    words = [word  for word in text.split() if word.lower() not in stop_words ]
    number_of_sentences = len(sentences)
    number_of_words = len(words)

    complex_words = []
    for word in words:
      vowels = 'aeiou'
      syllable_count_word = sum( 1 for letter in word if letter.lower() in vowels)
      if syllable_count_word > 2:
        complex_words.append(word)

    syllable_count = 0
    syllable_words =[]
    for word in words:
      if word.endswith('es'):
        word = word[:-2]
      elif word.endswith('ed'):
        word = word[:-2]
      vowels = 'aeiou'
      syllable_count_word = sum( 1 for letter in word if letter.lower() in vowels)
      if syllable_count_word >= 1:
        syllable_words.append(word)
        syllable_count += syllable_count_word

    AVG_SENTENCE_LENGTH = number_of_words / number_of_sentences
    PER_OF_COMPLEX_WORDS = len(complex_words) / number_of_words
    FOG_INDEX = 0.4 * (AVG_SENTENCE_LENGTH + PER_OF_COMPLEX_WORDS)
    SYLLABLE_PER_WORD = syllable_count / len(syllable_words)

    return AVG_SENTENCE_LENGTH, PER_OF_COMPLEX_WORDS, FOG_INDEX, len(complex_words), SYLLABLE_PER_WORD

for file in os.listdir(text_dir):
  s, p, f, c, a = analysis(file)
  AVG_SENTENCE_LENGTH.append(s)
  PER_OF_COMPLEX_WORDS.append(p)
  FOG_INDEX.append(f)
  COMPLEX_WORD_COUNT.append(c)
  SYLLABLE_PER_WORD.append(a)

def cleaned_words(file):
  with open(os.path.join(text_dir,file), 'r') as f:
    text = f.read()
    text = re.sub(r'[^\w\s]', '' , text)
    words = [word  for word in text.split() if word.lower() not in stop_words]
    length = sum(len(word) for word in words)
    AVG_WORD_LENGTH = length / len(words)
  return len(words),AVG_WORD_LENGTH

WORD_COUNT = []
AVG_WORD_LENGTH = []
for file in os.listdir(text_dir):
  x, y = cleaned_words(file)
  WORD_COUNT.append(x)
  AVG_WORD_LENGTH.append(y)

def count_personal_pronouns(file):
  with open(os.path.join(text_dir,file), 'r') as f:
    text = f.read()
    personal_pronouns = ["I", "we", "my", "ours", "us"]
    count = 0
    for pronoun in personal_pronouns:
      count += len(re.findall(r"\b" + pronoun + r"\b", text)) # \b is used to match word boundaries
  return count

PERSONAL_PRONOUNS_COUNT = []
for file in os.listdir(text_dir):
  x = count_personal_pronouns(file)
  PERSONAL_PRONOUNS_COUNT.append(x)

#read output data structure
output = pd.read_excel("Output Data Structure.xlsx")

#drop rows of page does't exist
output.drop([44-37,57-37,144-37], axis = 0, inplace=True)

variables = [positive_score,
             negative_score,
             polarity_score,
             subjectivity_score,
             AVG_SENTENCE_LENGTH,
             PER_OF_COMPLEX_WORDS,
             FOG_INDEX,
             AVG_SENTENCE_LENGTH,
             COMPLEX_WORD_COUNT,
             WORD_COUNT,
             SYLLABLE_PER_WORD,
             PERSONAL_PRONOUNS_COUNT,
             AVG_WORD_LENGTH
             ]

# write the values to the dataframe
for i, var in enumerate(variables):
  output.iloc[:,i+2] = var

#save output
output.to_csv('Output_Data.csv')
