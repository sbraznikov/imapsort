import imaplib
import yaml


CONFIG_PATH = 'imapsort.rc'


class Imapsort(object):
    def __init__(self):
        self.init_config()
        self.init_imap()
        self.init_rules()

    def init_config(self):
        config_path = open(CONFIG_PATH)
        self.config = yaml.load(config_path)
        config_path.close()

    def init_imap(self):
        config = self.config.pop('imap', None)
        if config['ssl'] is True:
            imap = imaplib.IMAP4_SSL(config['server'], config['port'])
        else:
            imap = imaplib.IMAP4(config['server'])
        imap.login(config['user'], config['password'])
        imap.select()
        self.imap = imap

    def init_rules(self):
        rules = self.config
        [self.run(rule) for rule in rules.iteritems()]

    def run(self, rule):
        commands = []
        commands.insert(0, rule[1]['conditions'])
        commands.insert(1, rule[1]['actions'])
        for command in commands:
            for command, param in command.iteritems():
                method_name = 'email_%s' % command
                if hasattr(self, method_name):
                    method = getattr(self, method_name)
                    method(param)
                else:
                    self.error(command)

    def error(self, command):
        print 'Imapsort: command not found: %s' % command

    def search(self, key, pattern, is_header=False):
        if not is_header:
            search = '(%s "%s")' % (key, pattern)
        else:
            search = '(%s %s)' % (key, pattern)
        typ, [response] = self.imap.search(None, search)
        if typ != 'OK':
            raise RuntimeError(response)
        self.result = ','.join(response.split(' '))

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

    def email_mark(self, flag):
        if len(self.result) <= 0:
            return
        self.imap.store(self.result, '+FLAGS', r'(\%s)' % flag)

    def email_move(self, path):
        if len(self.result) <= 0:
            return
        self.imap.copy(self.result, path)
        self.imap.store(self.result, '+FLAGS', r'(\Deleted)')
        self.imap.expunge()

Imapsort()
