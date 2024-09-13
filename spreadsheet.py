import gspread

from entry import MessageEntry


class Spreadsheet:
    def __init__(self, filename):
        self._gc = gspread.service_account()
        self.filename = filename


    def _sheet(self):
        return self._gc.open(self.filename).sheet1

    def create_headers(self):
        """
        Create the headers for the spreadsheet.
        """
        headers = ["Message ID", "Channel", "Author", "Timestamp", "URL", "Message Content", "Jump URL"]
        self._sheet().insert_row(headers, 1)

    def write(self, cell: str, content: str):
        self._sheet().update_acell(cell, content)

    def purge(self):
        """
        Delete all rows in the spreadsheet and regenerate the header row.
        """
        # Clear all rows
        self._sheet().clear()
        # Regenerate headers
        self.create_headers()

    def get(self, cell: str):
        return self._sheet().get(cell)

    def append_row(self, entry: MessageEntry):
        """
        Append a single row representing the message entry.
        The channel name will be a clickable link (HYPERLINK function).
        """

        # Convert the dataclass instance into a list
        row = entry.to_row()
        self._sheet().append_row(row)
    
    def append_rows(self, entries: list[MessageEntry]):
        """
        Append multiple rows representing message entries.
        Each channel name will be a clickable link (HYPERLINK function).
        """
        rows = [e.to_row() for e in entries]

        self._sheet().append_rows(rows)

    def get_archived_message_ids(self):
        """
        Retrieve all the archived message IDs from the spreadsheet.
        We assume that message IDs are stored in the first column.
        """
        message_ids = self._sheet().col_values(1)  # Assume message IDs are in the first column
        return set(message_ids)  # Return as a set for fast lookup

if __name__ == '__main__':
    entry = MessageEntry(
        message_id='message id',
        channel_name='channel name',
        author_name='author name',
        timestamp='timestamp',
        url='https://example.com',
        message_content='blabla',
        jump_url='https://example.com'
    )

    sh = Spreadsheet('Test archiviste')
    sh.append_row(entry)