require 'net/imap'
require 'logger'

class Imapsort
    def initialize &block
        @log = Logger.new(STDOUT)
        instance_eval &block
        @imap.logout
        # @imap.disconnect
    end

    def login account
        imap = Net::IMAP.new(account[:server])
        imap.authenticate('LOGIN', account[:user], account[:pass])
        imap.select('INBOX')
        @imap = imap
    end
  
    def from email
        @result = @imap.search(['FROM', email])
        # @log.info("from #{email}")
    end

    def to email
        @result = @imap.search(['TO', email])
        @log.info("to #{email}")
    end

    def subject string
        @result = @imap.search(['SUBJECT', string])
        @log.info("subject #{string}")
    end
    
    def body string
        @result = @imap.search(['BODY', string])
        @log.info("body #{string}")
    end

    def cc email
        @result = @imap.search(['CC', email])
        @log.info("from #{email}")
    end
    
    def move path
        @result.each do |message_id|
            @imap.copy(message_id, path)
            @imap.store(message_id, '+FLAGS', [:Deleted])
            @log.info("move #{message_id}")
        end
        @imap.expunge
    end

    def remove
        mark('Deleted')
        @imap.expunge
    end

    def mark flag
        flags = [:"#{flag}"]
        @result.each do |message_id|
            @imap.store(message_id, '+FLAGS', flags)
            @log.info("mark #{message_id}")
        end
    end
end
