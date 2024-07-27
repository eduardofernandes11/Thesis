import re
import email
import urllib.parse
import html
import argparse

linksFoundList = []

def decodev1(rewrittenurl):
    match = re.search(r'u=(.+?)&k=', rewrittenurl)
    if match:
        urlencodedurl = match.group(1)
        htmlencodedurl = urllib.parse.unquote(urlencodedurl)
        url = html.unescape(htmlencodedurl)
        url = re.sub("http://", "", url)
        if url not in linksFoundList:
            linksFoundList.append(url)

def decodev2(rewrittenurl):
    match = re.search(r'u=(.+?)&[dc]=', rewrittenurl)
    if match:
        specialencodedurl = match.group(1)
        trans = str.maketrans('-_', '%/')
        urlencodedurl = specialencodedurl.translate(trans)
        htmlencodedurl = urllib.parse.unquote(urlencodedurl)
        url = html.unescape(htmlencodedurl)
        url = re.sub("http://", "", url)
        if url not in linksFoundList:
            linksFoundList.append(url)

def analyzePhish(file_path):
    try:
        # Use the 'email' library for .eml parsing
        with open(file_path, 'rb') as f:
            msg = email.message_from_binary_file(f)

    except Exception as e:
        print(f'Error Opening File: {e}')
        return

    print("\nExtracting Headers...")
    try:
        from_header = msg.get('From')
        to_header = msg.get('To')
        subject_header = msg.get('Subject')
        date_header = msg.get('Date')
        return_path_header = msg.get('Return-Path')
        print(f"   FROM: {from_header}")
        print(f"   TO: {to_header}")
        print(f"   SUBJECT: {subject_header}")
        print(f"   DATE: {date_header}")
        print(f"   RETURN PATH: {return_path_header}")
    except Exception as e:
        print(f'   Header Error: {e}')

    # Assuming the email body is plain text; adjust if dealing with multipart or HTML
    body = ''
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == 'text/plain':
                body = part.get_payload(decode=True).decode()
                break
    else:
        body = msg.get_payload(decode=True).decode()

    print("\nExtracting Links...")
    try:
        match = r"((www\.|http://|https://)(www\.)*.*?(?=(www\.|http://|https://|$)))"
        links = re.findall(match, body, re.M | re.I)
        for link in links:
            match = re.search(r'https://urldefense.proofpoint.com/(v[0-9])/', link[0])
            if match:
                if match.group(1) == 'v1':
                    decodev1(link[0])
                elif match.group(1) == 'v2':
                    decodev2(link[0])
            else:
                if link[0] not in linksFoundList:
                    linksFoundList.append(link[0])
        if not links:
            print('   No Links Found...')
    except Exception as e:
        print(f'   Links Error: {e}')

    for each in linksFoundList:
        print(f'   {each}')

    print("\nExtracting Email Addresses...")
    try:
        match = r'([\w0-9._-]+@[\w0-9._-]+\.[\w0-9_-]+)'
        emailList = re.findall(match, body, re.M | re.I)
        if emailList:
            for b in set(emailList):
                print(f"   {b}")
        else:
            print('   No Emails Found...')
    except Exception as e:
        print(f'   Emails Error: {e}')

    print("\nExtracting IPs...")
    try:
        ipList = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', body)
        if ipList:
            for each in set(ipList):
                print(f'   {each}')
        else:
            print('   No IP Addresses Found...')
    except Exception as e:
        print(f'   IP Error: {e}')

    # try:
    #     analyzeEmail(msg.SenderEmailAddress)
    # except:
    #     print('')

    # phishingMenu()
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Analyze an .eml file for phishing details.")
    parser.add_argument("file", help="Path to the .eml file to be analyzed")
    args = parser.parse_args()

    analyzePhish(args.file)
    print("\n\n")
    print("Links Found: ", linksFoundList)