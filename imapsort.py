import imaplib


class Imapsort(object):
    def __init__(self, server, user, password, rules):
        imap = imaplib.IMAP4(server)
        imap.login(user, password)
        imap.select()
        self.imap = imap
        self.rules = rules
        self.walk()

    def walk(self):
        for rule in self.rules:
            command = rule.keys()[0]
            param = rule[rule.keys()[0]]
            self.run(command, param)

    def run(self, command, param):
        method_name = 'email_%s' % command
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            method(param)
        else:
            self.error()

    def error(self):
        print 'Error!'

    def prepare_result(self, response):
        self.result = ','.join(response.split(' '))

    def email_from(self, email):
        typ, [response] = self.imap.search(None, '(FROM "%s")' % email)
        if typ != 'OK':
            raise RuntimeError(response)
        self.prepare_result(response)
            
    def email_subject(self, string):
        print string

    def email_action(self, action):
        self.run(action.keys()[0], action[action.keys()[0]])
        
    def email_move(self, path):
        self.imap.copy(self.result, path)
        self.imap.store(self.result, '+FLAGS', r'(\Deleted)')
        self.imap.expunge()
