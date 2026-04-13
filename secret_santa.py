import yaml
import re
import random
import smtplib
import datetime
import pytz
import time
import socket
import sys
import argparse
import os

REQRD = (
    'SMTP_SERVER',
    'SMTP_PORT',
    'USERNAME',
    'TIMEZONE',
    'PARTICIPANTS',
    'FROM',
    'SUBJECT',
    'MESSAGE',
)

EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')

HEADER = """Date: {date}
Content-Type: text/plain; charset="utf-8"
Message-Id: {message_id}
From: {frm}
To: {to}
Subject: {subject}

"""

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.yml')

def sanitize_header(value):
    """Remove newlines to prevent SMTP header injection."""
    return re.sub(r'[\r\n]', '', str(value))

class Person:
    def __init__(self, name, email, invalid_matches, wishlist):
        self.name = name
        self.email = email
        self.invalid_matches = invalid_matches
        self.wishlist = wishlist
    
    def __str__(self):
        return "{} <{}>".format(self.name, self.email)

class Pair:
    def __init__(self, giver, receiver):
        self.giver = giver
        self.receiver = receiver
    
    def __str__(self):
        return "{} ---> {}".format(self.giver.name, self.receiver.name)

def parse_yaml(yaml_path=CONFIG_PATH):
    with open(yaml_path) as f:
        return yaml.load(f, yaml.Loader)

def choose_receiver(giver, receivers):
    valid = [r for r in receivers
             if r.name != giver.name and r.name not in giver.invalid_matches]
    if not valid:
        raise Exception('No valid receiver for {}'.format(giver.name))
    return random.choice(valid)

MAX_ATTEMPTS = 1000

def create_pairs(g, r, attempt=0):
    if attempt >= MAX_ATTEMPTS:
        raise Exception(
            'Could not find valid pairings after {} attempts. '
            'Check your DONT-PAIR constraints.'.format(MAX_ATTEMPTS))
    givers = g[:]
    receivers = r[:]
    pairs = []
    for giver in givers:
        try:
            receiver = choose_receiver(giver, receivers)
            receivers.remove(receiver)
            pairs.append(Pair(giver, receiver))
        except Exception:
            return create_pairs(g, r, attempt + 1)
    return pairs


def main(argv=None):
    parser = argparse.ArgumentParser(
        description='Assign and email Secret Santa pairings.')
    parser.add_argument(
        '-s', '--send', action='store_true',
        help='Send emails to participants (default: dry-run)')
    args = parser.parse_args(argv)
    send = args.send

    try:
        config = parse_yaml()
        for key in REQRD:
            if key not in config:
                raise Exception(
                    'Required parameter {} not in yaml config file!'.format(key))

        # Support PASSWORD from environment variable or config
        if 'PASSWORD' not in config:
            config['PASSWORD'] = os.environ.get('SECRET_SANTA_PASSWORD')
        if not config.get('PASSWORD'):
            raise Exception(
                'PASSWORD must be set in config.yml or via the '
                'SECRET_SANTA_PASSWORD environment variable.')

        participants = config['PARTICIPANTS']
        dont_pair = config.get('DONT-PAIR', [])
        if len(participants) < 2:
            raise Exception('Not enough participants specified.')
        
        givers = []
        for person in participants:
            parts = person.split(None, 2)
            if len(parts) < 2:
                raise Exception(
                    'Invalid participant entry: "{}". '
                    'Expected "Name email [wishlist]".'.format(person))
            name = parts[0].strip()
            email = parts[1].strip()
            wishlist = parts[2].strip() if len(parts) > 2 else ''
            if not EMAIL_RE.match(email):
                raise Exception(
                    'Invalid email address for {}: "{}"'.format(name, email))
            invalid_matches = []
            for pair in dont_pair:
                names = [n.strip() for n in pair.split(',')]
                if name in names:
                    # is part of this pair
                    for member in names:
                        if name != member:
                            invalid_matches.append(member)
            person = Person(name, email, invalid_matches, wishlist)
            givers.append(person)
        
        receivers = givers[:]
        pairs = create_pairs(givers, receivers)
        if not send:
            print("""
Test pairings:
                
{}
                
To send out emails with new pairings,
call with the --send argument:

    $ python secret_santa.py --send
            
            """.format("\n".join([str(p) for p in pairs])))
        
        if send:
            server = smtplib.SMTP(config['SMTP_SERVER'], config['SMTP_PORT'])
            server.starttls()
            server.login(config['USERNAME'], config['PASSWORD'])
            try:
                for pair in pairs:
                    zone = pytz.timezone(config['TIMEZONE'])
                    now = zone.localize(datetime.datetime.now())
                    date = now.strftime('%a, %d %b %Y %H:%M:%S %Z')
                    message_id = '<{}@{}>'.format(
                        str(time.time()) + str(random.random()),
                        socket.gethostname())
                    frm = sanitize_header(config['FROM'])
                    to = sanitize_header(pair.giver.email)
                    subject = sanitize_header(
                        config['SUBJECT'].format(
                            santa=pair.giver.name,
                            santee=pair.receiver.name))
                    body = (HEADER + config['MESSAGE']).format(
                        date=date,
                        message_id=message_id,
                        frm=frm,
                        to=to,
                        subject=subject,
                        santa=pair.giver.name,
                        santee=pair.receiver.name,
                        gifts_suggestions=pair.receiver.wishlist,
                    )
                    server.sendmail(frm, [to], body.encode('utf-8'))
                    print("Emailed {} <{}>".format(pair.giver.name, to))
            finally:
                server.quit()
        
    except Exception as err:
        print("Error: {}".format(err), file=sys.stderr)
        return 1


if __name__ == "__main__":
    main()