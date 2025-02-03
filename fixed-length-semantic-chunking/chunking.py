
from typing import Any

import json
import cohere
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path ="../.env", override=True)

co = cohere.Client( os.getenv("COHERE_TOKEN"))  # This is your trial API key

MAX_TOKEN = 512-50 #Buffer


def token_in_range(calculated_token):
    return calculated_token < MAX_TOKEN



def get_token_count(sentence):
    response = co.tokenize(text=sentence, model="command")
    return len(response.tokens)


def process_json_file(elements: Any):

    newlist = []

    initial_token = 0

    for ins in elements:
        if len(newlist) == 0 or (ins['type'] == 'Header' and ins['text'] != newlist[-1]['header']):
            entry = {'header': ins['text'], 'context': []}
            newlist.append(entry)
            print("Header token   "+ str(initial_token))
            initial_token = get_token_count(ins['text'])
        else:
            last_entry = newlist[-1]

            if ins['type'] == 'Title':
                if ins['text'] == 'ORACLE':
                    continue

                initial_token += get_token_count(ins['text'])

                new_title = {'title': ins['text'], 'body':[]}

                if not token_in_range(initial_token):
                    #print('Splitting from title')
                    new_entry = {'header': last_entry['header'], 'context': [new_title]}
                    newlist.append(new_entry)


                    #initial_token = 0
                    initial_token = get_token_count(new_entry['header'])  + get_token_count(new_title['title'])
                else:
                    print("initial token  "+ str(initial_token))
                    last_entry['context'].append(new_title)
                    #print(ins['text'])

            if ins['type'] in ['NarrativeText', 'ListItem', 'Table']:

                initial_token += get_token_count(ins['text'])
                last_context = last_entry['context'][-1]
                if not token_in_range(initial_token):
                    #print('Splitting from body')
                    new_body = {'title': last_context['title'], 'body':[ins['text']]}
                    new_entry = {'header': last_entry['header'], 'context': [new_body]}
                    newlist.append(new_entry)

                    initial_token = get_token_count(new_entry['header'])  + get_token_count(new_body['title']) + get_token_count(ins['text'])
                else:
                    print("table token  "+ str(initial_token))
                    last_body = last_context['body']
                    last_body.append(ins['text'])

            if ins['type'] == 'Header':
                if ins['text'] == last_entry['header']:
                    continue

    return newlist


filename = os.getenv("FILE_NAME")


f = open(filename)
data = json.load(f)

processed_data = process_json_file(data)

# print(processed_data)

save_file = open(os.getenv("PROCESSED_FILE_NAME"), "w")
json.dump(processed_data, save_file, indent=4)
save_file.close()





