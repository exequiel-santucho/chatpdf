import requests
import easygui
import os
from dotenv import load_dotenv


load_dotenv()
API_KEY = os.environ['chatPDF_api_key']

# Input file and get filename info 
inp_file_path = easygui.fileopenbox()

inp_filename_without_ext = os.path.splitext(os.path.basename(inp_file_path))[0]
filename_ext = os.path.splitext(os.path.basename(inp_file_path))[1]
file = inp_filename_without_ext+filename_ext

out_filename = inp_filename_without_ext + '_QA.txt'
out_file_path = './' + out_filename

files = [
    ('file', ('file', open(inp_file_path, 'rb'), 'application/octet-stream'))
]
headers = {
    'x-api-key': API_KEY
}

response = requests.post(
    'https://api.chatpdf.com/v1/sources/add-file', headers=headers, files=files)

if response.status_code == 200:
    # print('Source ID:', response.json()['sourceId'])
    print('\nFile loaded:', file)
else:
    print('Status:', response.status_code)
    print('Error:', response.text)

# Chat with PDF
headers = {
    'x-api-key': API_KEY,
    "Content-Type": "application/json",
}

records = []
listening = True
while listening:
    try:
        question = input('\nPlease enter your question [for EXIT, press 0]: ')
        if question == '0':
            listening = False
            print('\nClosed connection.')
        else:
            data = {
                'referenceSources': True, # references to the PDF pages
                'sourceId': response.json()['sourceId'],
                'messages': [
                    {
                        'role': "user",
                        'content': question,
                    }
                ]
            }

            response = requests.post(
                'https://api.chatpdf.com/v1/chats/message', headers=headers, json=data)

            if response.status_code == 200:
                answer = response.json()['content']
                print('\nAnswer:', answer)
            else:
                print('Status:', response.status_code)
                print('Error:', response.text)

            q_and_a = {'Question': question, 'Answer': answer}
            records.append(q_and_a)
    except:
        print('Please enter a valid question.')

# Save records
if not os.path.isfile(out_filename):
    with open(out_filename, 'a+') as f:
        f.write('File: %s\n' % file)
        f.write('Path: %s\n' % inp_file_path)
        f.write('-'*(len(inp_file_path)+6)+'\n')

for i, record in enumerate(records):
    with open(out_filename, 'a+') as f:
        for key, value in records[i].items(): 
            f.write('%s: %s\n' % (key, value))
        f.write('\n')