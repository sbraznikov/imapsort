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
  
  def move path
    @result.each do |message_id|
      @imap.copy(message_id, path)
      @imap.store(message_id, '+FLAGS', [:Deleted])
    end
    @imap.expunge
  end

  def remove
    @result.each do |message_id|
      @imap.store(message_id, '+FLAGS', [:Deleted])
    end
    @imap.expunge
  end
end
