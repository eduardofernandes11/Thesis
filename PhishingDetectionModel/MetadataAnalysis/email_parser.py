# PARSE THE EMAILS IN THE FOLDER AND EXTRACT THE REQUIRED DETAILS TO email_details.json

import os
from email import policy
from email.parser import BytesParser
import json

header_dict = {
    'subjects': 'Subject',
    'from_addresses': 'From',
    'to_addresses': 'To',
    'dates': 'Date',
    'message_ids': 'Message-ID',
    'return_paths': 'Return-Path'
}

email_details = {
    'subjects': [], 
    'from_addresses': [],
    'to_addresses': [],
    'dates': [],
    'message_ids': [],
    'return_paths': []
    }

def parse_real_emails(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith('.eml'):
            with open(os.path.join(folder_path, filename), 'rb') as f:
                msg = BytesParser(policy=policy.default).parse(f)
                for key in header_dict:
                    if msg[header_dict[key]] not in email_details[key]:
                        email_details[key].append(msg[header_dict[key]])
    
    # Save the extracted details to a JSON file for later use
    with open('email_details.json', 'w') as outfile:
        json.dump(email_details, outfile)

if __name__ == '__main__':
    parse_real_emails('../../EmailsHeaders')
