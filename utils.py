import re

def extract_urls(message_content):
    url_regex = r'(https?://\S+)'
    return re.findall(url_regex, message_content)
