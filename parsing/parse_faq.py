import pandas as pd
from bs4 import BeautifulSoup
import requests
with open('links_faq.txt') as f:
    global_urls = f.read().splitlines()

questions = []
answers = []
topics = []
ids = []
id = 0
for i in range(len(global_urls)):
    url = global_urls[i]
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")

    topic = soup.find('span', class_='referenceable').get_text()

    all_questions = soup.findAll('div', class_='question_title referenceable')
    if all_questions == []:
        all_questions = soup.findAll('div', class_='question_title _active referenceable')

    all_answers = soup.findAll('div', class_='additional-text-block')
    for k in range(len(all_answers)):
        questions.append(all_questions[k].get_text())
        answers.append(all_answers[k].get_text())
        topics.append(topic)
        ids.append(id)
        id+=1


pd.DataFrame(data={'id': ids, 'topic': topics, 'question': questions, 'answer': answers}).to_csv('faq_bank.csv')
    #print(len(all_answers), len(all_questions))
    #all_answers[0].get_text()
    #print(all_questions)
    #print(i)
    #if i == 0 and
    #print(all_questions[0].get_text())