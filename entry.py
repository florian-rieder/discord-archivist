from dataclasses import dataclass

@dataclass
class MessageEntry:
    message_id: str
    channel_name: str
    author_name: str
    timestamp: str
    url: str
    message_content: str
    jump_url: str
    
    def to_row(self):
        return [
                self.message_id,
                self.channel_name,
                self.author_name,
                self.timestamp,
                self.url,
                self.message_content,
                self.jump_url
            ]
