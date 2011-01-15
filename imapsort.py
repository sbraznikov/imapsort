import imaplib


class Imapsort(object):
    def __init__(self, server, user, password, rules):
        self.init_imap(server, user, password)
        self.init_rules(rules)

    def init_imap(self, server, user, password):
        imap = imaplib.IMAP4(server)
        imap.login(user, password)
        imap.select()
        self.imap = imap

    def init_rules(self, rules):
        self.rules = rules
        self.walk()

    def walk(self):
        [self.run(rule[0], rule[1]) for rule in self.rules]

    def run(self, command, param):
        method_name = 'email_%s' % command
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            method(param)
        else:
            self.error(command)

    def error(self, command):
        print 'Imapsort: command not found: %s' % command

    def prepare_result(self, response):
        self.result = ','.join(response.split(' '))

    def search(self, key, pattern, is_header=False):
        if not is_header:
            search = '(%s "%s")' % (key, pattern)
        else:
            search = '(%s %s)' % (key, pattern)
        typ, [response] = self.imap.search(None, search)
        if typ != 'OK':
            raise RuntimeError(response)
        self.prepare_result(response)

    def email_from(self, email):
        self.search('FROM', email)

    def email_to(self, email):
        self.search('TO', email)

    def email_cc(self, email):
        self.search('CC', email)

    def email_subject(self, string):
        self.search('SUBJECT', string)

    def email_body(self, string):
        self.search('BODY', string)

    def email_header(self, string):
        self.search('HEADER', string, is_header=True)

    def email_action(self, action):
        self.run(action[0], action[1])

    def email_mark(self, flag):
        self.imap.store(self.result, '+FLAGS', r'(\%s)' % flag)

    def email_move(self, path):
        self.imap.copy(self.result, path)
        self.imap.store(self.result, '+FLAGS', r'(\Deleted)')
        self.imap.expunge()
