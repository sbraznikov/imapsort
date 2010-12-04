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

    def email_from(self, email):
        self.search('FROM', email)

    def email_to(self, email):
        self.search('TO', email)
        print self.result

    def search(self, header, pattern):
        typ, [response] = self.imap.search(None, '(%s "%s")' % (header, pattern))
        if typ != 'OK':
            raise RuntimeError(response)
        self.prepare_result(response)

    def email_action(self, action):
        self.run(action[0], action[1])

    def email_move(self, path):
        self.imap.copy(self.result, path)
        self.imap.store(self.result, '+FLAGS', r'(\Deleted)')
        self.imap.expunge()
