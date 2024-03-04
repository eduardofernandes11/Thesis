import random
import os, shutil
from email.generator import Generator
from email.mime.multipart import MIMEMultipart
from faker import Faker  # package that generates fake data

fake = Faker()  # create a fake data generator instance

required_headers = [
    'From',
    'To',
    'Subject',
    'Date',
    'Message-ID',
    'Return-Path'
]

fake_institutions = [
    "noreply@bankofamerica.com", 
    "support@apple.com",
    "service@paypal.com"
]

subjects = [
    "Urgent: Unusual Sign-in Activity Detected!",
    "Action Required: Your Account Will Be Closed!",
    "Warning: Payment Declined - Update Billing Information Now!"
]

def generate_phishing_headers():
    headers = {}
    for header_name in required_headers:
        if header_name == 'From':
            # spoofed "From" address lookin like legitimate institutions
            headers[header_name] = random.choice(fake_institutions)
        elif header_name == 'To':
            headers[header_name] = fake.email()
        elif header_name == 'Subject':
            # urgent or alarming subject lines
            headers[header_name] = random.choice(subjects)
        elif header_name == 'Date':
            # implausible dates or timestamps (e.g., future dates)
            future_date = fake.date_time_between(start_date="now", end_date="+30d").strftime("%a, %d %b %Y %H:%M:%S %z")
            headers[header_name] = future_date
        elif header_name == 'Message-ID':
            # use a format that might look legitimate but is random
            headers[header_name] = f"<{fake.uuid4()}@{fake.free_email_domain()}>"
        elif header_name == 'Return-Path':
            # spoofed "Return-Path" similar to "From" but can be different
            headers[header_name] = fake.email()
    return headers

if __name__ == '__main__':
    N = 1  # number of emails to generate

    # delete all files in the folder before generating new ones
    folder = 'SyntheticEmailHeaders'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

    # generate N emails
    for i in range(1, N+1):
        msg = MIMEMultipart()
        headers = generate_phishing_headers()
        for header, value in headers.items():
            msg[header] = value

        # if there is non-text parts it is necessary to use binary mode
        with open('SyntheticEmailHeaders/generated_email_{}.eml'.format(i), 'w') as f:
            generator = Generator(f)
            generator.flatten(msg)