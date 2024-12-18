import email
from email import policy
from email.parser import BytesParser
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np
import dns.resolver

parser = BytesParser(policy=policy.default)
columns = ['received1',
'received2',
'received3',
'received4',
'received5',
'received6',
'received7',
'received8',
'received9',
'received10',
'received11',
'hops',
'subject',
'date',
'message-id',
'from',
'return-path',
'to',
'content-type',
'mime-version',
'content-transfer-encoding',
'content-length',
'delivered-to',
'sender',
'reply-to',
'references',
'in-reply-to',
'cc',
'received-spf',
'content-disposition',
'mailing-list',
'domainkey-signature',
'importance',
'label']

# Function to parse email and extract headers and body
def parse_eml_file(file_path):
    print(file_path)
    with open(file_path, 'rb') as f:
        msg = parser.parse(f)

    # Initialize the row dictionary
    row_dict = {}

    # Parse the email content
    h = msg

    # Parse recieved field
    received_list = h.get_all('received')
    hops = 0
    if received_list is not None:
        hops = len(received_list)
        col_name_recieved = 'received'

        for inx, received_field in enumerate(received_list):
            col = col_name_recieved + str(inx+1)
            row_dict[col] = received_field

    # Make everything lowercase to avoid issues
    features_lower_case = [x.lower() for x in h.keys()]

    # Parse everything else
    new_row = dict(zip(features_lower_case, h.values()))
    new_row['hops'] = hops

    for key, value in new_row.items():
        if key in columns:
            row_dict[key] = value

    # Extract the body (plain text or HTML)
    body = None
    if msg.is_multipart():
        for part in msg.iter_parts():
            cdispo = str(part.get('Content-Disposition'))
            if part.get_content_type() == "text/plain" and 'attachment' not in cdispo:
                charset = part.get_content_charset() or 'utf-8'  # Fallback to 'utf-8' if charset is None
                try:
                    body = part.get_payload(decode=True).decode(charset, errors='replace')
                except LookupError:
                    # If the charset is not recognized, fallback to 'utf-8'
                    body = part.get_payload(decode=True).decode('utf-8', errors='replace')
            elif part.get_content_type() == "text/html" and 'attachment' not in cdispo:
                charset = part.get_content_charset() or 'utf-8'  # Fallback to 'utf-8' if charset is None
                try:
                    html_body = part.get_payload(decode=True).decode(charset, errors='replace')
                except LookupError:
                    # If the charset is not recognized, fallback to 'utf-8'
                    html_body = part.get_payload(decode=True).decode('utf-8', errors='replace')
                body = BeautifulSoup(html_body, 'html.parser').get_text()
    else:
        charset = msg.get_content_charset() or 'utf-8'  # Fallback to 'utf-8' if charset is None
        try:
            body = msg.get_payload(decode=True).decode(charset, errors='replace')
        except LookupError:
            # If the charset is not recognized, fallback to 'utf-8'
            body = msg.get_payload(decode=True).decode('utf-8', errors='replace')

    # Add the body to the row dictionary
    row_dict['body'] = body
    
    return row_dict

def check_received_forged(row):
  num_iters = row['hops']
  col_name_base = 'received'

  for i in range(1, num_iters+1):
    curr_val = row[col_name_base + str(i)]
    if 'forged' in curr_val:
      return 1
    else:
      continue
  return 0

def count_chars(field_names, new_col_names, df):
    for field_name, new_col_name in zip(field_names, new_col_names):
        df[new_col_name] = df[field_name].str.len()

    return new_col_names

def extract_num_replies(row):
  if 'references' not in row:
    return 0
  references_val = row['references']
  all = re.findall(r'<([a-zA-Z0-9+._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)>', 
                  references_val)
  return len(all)

# Function to get the last non-empty 'received' field in each row
def get_last_received(row):
    # Loop through the columns from the last to the first
    for i in range(row['hops']-1, 0, -1):
        if row['received'+str(i)] != '':  # Check if the value is not an empty string
            return row['received'+str(i)]
    return ''  # Return empty string if all fields are empty

def date_received_date_comp(row):
  date_date = row['date']
  date_received = row['last_received_date']

  d1 = email.utils.parsedate_tz(date_date)
  d2 = email.utils.parsedate_tz(date_received)

  if d1 is None or d2 is None:
    return -1

  try:
    val1 = email.utils.mktime_tz(d1)
    val2 = email.utils.mktime_tz(d2)
  except:
    return -1

  return (email.utils.mktime_tz(d2)) - (email.utils.mktime_tz(d1))

# emails in brackets '<>' are matched first, and if none, then other emails are matched
def extract_emails(row, col_name):

  if col_name not in row:
    return []

  in_brackets = re.findall(r'<([a-zA-Z0-9+._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)>', row[col_name])

  if len(in_brackets) == 0:
    not_in_brackets = re.findall(r'([a-zA-Z0-9+._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)', row[col_name])
    if len(not_in_brackets) == 0:
      return []
    else:
      return not_in_brackets
  else:
    return in_brackets

def extract_domains(row, col_name):
  
  if col_name not in row:
    return []

  emails_list = row[col_name]

  if len(emails_list) == 0:
    return []
  else:
    domains_list = []
    for email in emails_list:
      if len(email.split('.')) < 2:
        continue
      else:
        main_domain = email.split('@')[-1]
        main_domain = main_domain.split('.')[-2:]
        main_domain = main_domain[0] + '.' + re.sub('\W+','', main_domain[1])
        domains_list.append(main_domain.lower())
    return domains_list
  
def email_same_check(row, first_col, second_col):
  vals1 = row[first_col]
  vals2 = row[second_col]
  if second_col == 'return-path':
    print(str(vals1) + ' - ' + str(vals2))

  for val1 in vals1:
    for val2 in vals2:
      if val1 == val2:
        return 1

  return 0

# Returns 0 if no matches, 1 if at least one match
def domain_match_check(row, first_col, second_col):

  first_domain_list = row[first_col]
  second_domain_list = row[second_col]
  if second_col == 'return-path_domains':
    print(str(first_domain_list) + ' - ' + str(second_domain_list))

  if len(first_domain_list) == 0 or len(second_domain_list) == 0:
    return 0
  else:
    for d1 in first_domain_list:
      for d2 in second_domain_list:
        if d1 == d2:
          return 1
    return 0
  
# Function to extract IP addresses from the 'Received' fields of a single row (email)
def extract_ips_from_row(row):
    # Regular expression to capture IP addresses in Received headers
    ip_regex = re.compile(r'\[(\d{1,3}(?:\.\d{1,3}){3})\]')

    # List to hold all extracted IPs
    ips = []

    # Iterate over the received columns for the row
    for col in row.index:
        if 'received' in col:
            # Extract IPs from the current 'received' field
            ips += ip_regex.findall(str(row[col]))

    # Remove duplicates
    return list(set(ips))

# Function to check if any IP in a row is blacklisted
def check_row_for_blacklist(row):
    ips = extract_ips_from_row(row)
    
    if not ips:
        return 0

    servers_blacklisted = 0
    
    # Check each IP and return 1 if any IP is blacklisted
    for ip in ips:
        if check_ip_spamhaus(ip):
            servers_blacklisted += 1

    return servers_blacklisted

def extract_host_ip(row):
    # Regular expression to capture IP addresses in Received headers
    ip_regex = re.compile(r'\[(\d{1,3}(?:\.\d{1,3}){3})\]')

    host = row['received1']
    # Extract IP from the host 'received' field
    host_ip = ip_regex.findall(str(host))
    return host_ip

# Function to check if any IP in a row is blacklisted
def check_host_ip(row):
    host_ip = extract_host_ip(row)
    
    if not host_ip:
        return 0
    
    # Check each IP and return 1 if IP is blacklisted
    if check_ip_spamhaus(host_ip[0]):
        return 1
    return 0

# Function to check if an IP is blacklisted using Spamhaus DNSBL
def check_ip_spamhaus(ip):
    reverse_ip = '.'.join(reversed(ip.split('.')))
    query = f"{reverse_ip}.zen.spamhaus.org"
    
    try:
        # Perform a DNS query to check if the IP is blacklisted
        answers = dns.resolver.resolve(query, 'A')
        print(f"IP {ip} is blacklisted by Spamhaus.")
        return True
    except dns.resolver.NXDOMAIN:
        print(f"IP {ip} is NOT blacklisted by Spamhaus.")
        return False
    except Exception as e:
        print(f"Error querying Spamhaus for IP {ip}: {str(e)}")
        return False
    
def clean_text(text):
    if text is None:
        return None
    
    # Remove the '=' sign used in quoted-printable encoding
    text = text.replace('=\n', '')  # Handle the soft line breaks (encoded as =\n)
    text = text.replace('=', '')    # Remove remaining '='

    # Remove &nbsp; and replace with a regular space
    text = text.replace('&nbsp;', ' ')

    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)

    # Fallback to remove HTML tags if any
    text = re.sub(r'<[^>]+>', '', text)
    
    # Strip leading and trailing whitespace
    text = text.strip()
    
    return text   


def parse_and_preprocessing_email_content(email_path: str):
    email_data = []
    parsed_email = parse_eml_file(email_path)
    email_data.append(parsed_email)
    df = pd.DataFrame(email_data)

    df = df.replace(np.nan, '', regex=True)

    final_features_list = []

    # Check if the received field contains the word 'forged'
    df['received_str_forged'] = df.apply(check_received_forged, axis=1)
    final_features_list.append('received_str_forged')

    # Count the number of characters in the 'from' field
    fields_to_find_lengths = ['from']
    new_col_names_lengths = []

    for val in fields_to_find_lengths:
        new_col_names_lengths.append('length_' + val)

    new_col_names = count_chars(fields_to_find_lengths, new_col_names_lengths, df)

    final_features_list.extend(new_col_names)

    # Count the number of recipients in the 'to' field
    df['num_recipients_to'] = df.apply(lambda x: len(re.findall(
        r'([a-zA-Z0-9+._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)', x.get('to', ''))), axis=1)

    # Count the number of recipients in the 'cc' field
    df['num_recipients_cc'] = df.apply(lambda x: len(re.findall(
        r'([a-zA-Z0-9+._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)', x.get('cc', ''))), axis=1)

    # Count the number of recipients in the 'from' field
    df['num_recipients_from'] = df.apply(lambda x: len(re.findall(
        r'([a-zA-Z0-9+._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)', x.get('from', ''))), axis=1)

    # Count the number of recipients in the 'reply-to' field
    df['number_replies'] = df.apply(extract_num_replies, axis=1)

    # Get the last 'received' field
    df['last_received'] = df.apply(get_last_received, axis=1)

    # Extract the date from the 'last_received' field
    df['last_received_date'] = df['last_received'].str.replace('\n\t', ';').str.split(r';').str[-1]

    # Compare the date and the 'last_received' date
    df['date_comp_date_received'] = df.apply(date_received_date_comp, axis=1)

    emails_from = df.apply(extract_emails, col_name='from', axis=1)
    emails_message_id = df.apply(extract_emails, col_name='message-id', axis=1)
    emails_return_path = df.apply(extract_emails, col_name='return-path', axis=1)
    emails_reply_to = df.apply(extract_emails, col_name='reply-to', axis=1)
    #emails_errors_to = df_combined.apply(extract_emails, col_name='errors-to', axis=1)
    emails_in_reply_to = df.apply(extract_emails, col_name='in-reply-to', axis=1)
    emails_references = df.apply(extract_emails, col_name='references', axis=1)
    emails_to = df.apply(extract_emails, col_name='to', axis=1)
    emails_cc = df.apply(extract_emails, col_name='cc', axis=1)
    emails_sender = df.apply(extract_emails, col_name='sender', axis=1)

    emails_df = pd.concat([emails_from, emails_message_id, emails_return_path, 
                            emails_reply_to, emails_in_reply_to, 
                            emails_references, emails_to, emails_cc, emails_sender], axis=1)

    emails_df.columns = ['from', 'message-id', 'return-path', 'reply-to',
                        'in-reply-to', 'references', 'to', 'cc', 'sender']

    domains_from = emails_df.apply(extract_domains, col_name='from', axis=1)
    domains_message_id = emails_df.apply(extract_domains, col_name='message-id', axis=1)
    domains_return_path = emails_df.apply(extract_domains, col_name='return-path', axis=1)
    domains_reply_to = emails_df.apply(extract_domains, col_name='reply-to', axis=1)
    #domains_errors_to = emails_df.apply(extract_domains, col_name='errors-to', axis=1)
    domains_in_reply_to = emails_df.apply(extract_domains, col_name='in-reply-to', axis=1)
    domains_references = emails_df.apply(extract_domains, col_name='references', axis=1)
    domains_to = emails_df.apply(extract_domains, col_name='to', axis=1)
    domains_cc = emails_df.apply(extract_domains, col_name='cc', axis=1)
    domains_sender = emails_df.apply(extract_domains, col_name='sender', axis=1)

    domains_df = pd.concat([domains_from, domains_message_id, domains_return_path, 
                            domains_reply_to, domains_in_reply_to, 
                            domains_references, domains_to, domains_cc, domains_sender], axis=1)

    domains_df.columns = ['from_domains', 'message-id_domains', 'return-path_domains', 'reply-to_domains',
                     'in-reply-to_domains', 'references_domains', 'to_domains', 'cc_domains', 'sender_domains']
    
    emails_to_check = [('from', 'reply-to'), ('from', 'return-path'),]

    for val in emails_to_check:
        first_field = val[0]
        second_field = val[1]
        new_col_name = 'email_match_' + first_field + '_' + second_field

        df[new_col_name] = emails_df.apply(email_same_check, first_col=first_field, 
                        second_col=second_field, axis=1)
        final_features_list.append(new_col_name)

    domain_fields_to_check = [('message-id_domains', 'from_domains'), ('from_domains', 'return-path_domains'), ('message-id_domains', 'return-path_domains'), ('message-id_domains', 'sender_domains'), ('message-id_domains', 'reply-to_domains'),
                          ('return-path_domains', 'reply-to_domains'), ('reply-to_domains', 'to_domains'), ('to_domains', 'in-reply-to_domains'), ('sender_domains', 'from_domains'), ('references_domains', 'reply-to_domains'), ('references_domains', 'in-reply-to_domains'), ('references_domains', 'to_domains'), ('from_domains', 'reply-to_domains'),
                          ('to_domains', 'from_domains'), ('to_domains', 'message-id_domains')]

    for val in domain_fields_to_check:
        first_field = val[0].replace('_domains', '')
        second_field = val[1].replace('_domains', '')
        new_col_name = 'domain_match_' + first_field + '_' + second_field 

        df[new_col_name] = domains_df.apply(domain_match_check, first_col = val[0], 
                                    second_col= val[1], axis=1)
        final_features_list.append(new_col_name)

    # Apply the blacklist check for each row (email) and store the result in a new column
    df['num_servers_blacklisted'] = df.apply(lambda row: check_row_for_blacklist(row), axis=1)

    df['host_blacklisted'] = df.apply(lambda row: check_host_ip(row), axis=1)

    df['body'] = df['body'].apply(clean_text)

    final_features_list = ['received_str_forged', 'length_from', 'num_recipients_to',
       'num_recipients_cc', 'num_recipients_from', 'number_replies',
       'date_comp_date_received', 'email_match_from_reply-to',
       'email_match_from_return-path', 'domain_match_message-id_from',
       'domain_match_from_return-path', 'domain_match_message-id_return-path',
       'domain_match_message-id_sender', 'domain_match_message-id_reply-to',
       'domain_match_return-path_reply-to', 'domain_match_reply-to_to',
       'domain_match_to_in-reply-to', 'domain_match_sender_from',
       'domain_match_references_reply-to',
       'domain_match_references_in-reply-to', 'domain_match_references_to',
       'domain_match_from_reply-to', 'domain_match_to_from',
       'domain_match_to_message-id', 'num_servers_blacklisted',
       'host_blacklisted', 'body']
    
    df = df[final_features_list]

    email_body = df['body']  # Extract the body text
    email_headers = df[final_features_list[:-1]]  # Extract all header features

    return email_body, email_headers
    



