Secret Santa
============

**secret-santa** can help you manage a list of secret santa participants by randomly assigning pairings and sending emails.

It can avoid pairing couples to their significant other, allows the addition of each participant's suggestions for gifts, and supports custom email messages.

This is a fork of [underbluewaters/secret-santa](https://github.com/underbluewaters/secret-santa).

Dependencies
------------

- Python 3
- pytz
- pyyaml

Install dependencies with:

    pip install -r requirements.txt

Usage
-----

Copy `config.yml.template` to `config.yml` and enter in the connection details
for your outgoing mail server. Modify the participants and couples lists and
the email message if you wish.

    cd secret-santa/
    cp config.yml.template config.yml

Here is the example configuration unchanged:

    # Required to connect to your outgoing mail server. Example for using gmail:
    SMTP_SERVER: smtp.gmail.com
    SMTP_PORT: 587
    USERNAME: your_email@mail.com
    # PASSWORD can be set here or via the SECRET_SANTA_PASSWORD environment variable
    PASSWORD: "your_password"

    TIMEZONE: 'Europe/Dublin'

    PARTICIPANTS:
      - Chad chad@somewhere.net Chad's suggestions
      - Jen jen@gmail.net Jen's suggestions
      - Bill Bill@somedomain.net Bill's suggestions
      - Sharon Sharon@hi.org Sharon's suggestions

    # Optional -- omit if no pairing constraints are needed
    DONT-PAIR:
      - Chad, Jen    # Chad and Jen are married
      - Chad, Bill   # Chad and Bill are best friends
      - Bill, Sharon

    # From address should be the organizer in case participants have any questions
    FROM: You <you@gmail.net>

    # Both SUBJECT and MESSAGE can include variable substitution for the
    # "santa" and "santee"
    SUBJECT: Your secret santa recipient is {santee}
    MESSAGE:
      Dear {santa},

      This year you are {santee}'s Secret Santa. Ho Ho Ho!

      Don't forget that the maximum spending limit is EUR 25, and that {santee} left below a few suggestions to help you pick the perfect Christmas present.

      {gifts_suggestions}

      This message was automagically generated from a computer. Merry Christmas!

      The algorithm that made this all possible is available at https://codeberg.org/gadonias/secret-santa

### Password configuration

You can provide the SMTP password in two ways:

1. Directly in `config.yml` via the `PASSWORD` field.
2. Via the `SECRET_SANTA_PASSWORD` environment variable (recommended for security):

       export SECRET_SANTA_PASSWORD="your_password"

### Participant format

Each participant entry follows the format:

    Name email [wishlist]

The wishlist is optional. Email addresses are validated on startup.

### Running

Once configured, call secret-santa:

    python3 secret_santa.py

Calling secret-santa without arguments will output a test pairing of
participants.

        Test pairings:

        Chad ---> Bill
        Jen ---> Sharon
        Bill ---> Chad
        Sharon ---> Jen

        To send out emails with new pairings,
        call with the --send argument:

            $ python3 secret_santa.py --send

To send the emails, call using the `--send` argument:

    python3 secret_santa.py --send

Changelog
---------

### 0.3.0

- Fix file handle leak in YAML config parsing
- Fix trailing whitespace in email header/body separator
- Replace recursive `choose_receiver()` with iterative filter approach
- Fix `try/finally` scope — no longer risks `NameError` in dry-run mode
- Remove unused `result` variable from `sendmail` call
- Remove spurious `-c` flag from CLI options
- Replace legacy `getopt` with `argparse` for better help and error output
- Make `DONT-PAIR` config optional (defaults to no constraints)
- Add `__pycache__/` and `*.pyc` to `.gitignore`

### 0.2.0

- Fix Python 2 `print >>` syntax for Python 3 compatibility
- Fix bare `except` clause to allow KeyboardInterrupt to propagate
- Add attempt limit to pairing algorithm to prevent infinite recursion
- Fix SMTP connection leak — server is now properly closed on errors
- Replace non-portable `%T` date format with `%H:%M:%S`
- Add `requirements.txt` for dependency management
- Validate email addresses during participant parsing
- Make participant wishlist optional
- Support SMTP password via `SECRET_SANTA_PASSWORD` environment variable
- Sanitize email headers to prevent SMTP header injection

### 0.1.0

- Initial fork from [underbluewaters/secret-santa](https://github.com/underbluewaters/secret-santa)
- Support for wishlists
- Python 3 string formatting compatibility

License
-------

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
