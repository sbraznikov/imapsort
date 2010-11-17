require 'net/imap'

class Imapsort
    def initialize &block
        instance_eval &block
    end

    def login account
        imap = Net::IMAP.new(account[:server])
        imap.authenticate('LOGIN', account[:user], account[:pass])
        imap.select('INBOX')
        @imap = imap
    end
  
    def from email
        @result = @imap.search(['FROM', email])
    end

    def to email
        @result = @imap.search(['TO', email])
    end

    def subject string
        @result = @imap.search(['SUBJECT', string])
    end
    
    def body string
        @result = @imap.search(['BODY', string])
    end

    def cc string
        @result = @imap.search(['CC', string])
    end
    
    def move path
        @result.each do |message_id|
            @imap.copy(message_id, path)
            @imap.store(message_id, '+FLAGS', [:Deleted])
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
        end
    end
end
