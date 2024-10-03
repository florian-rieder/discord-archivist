from datetime import datetime
import logging

import gspread

from entry import MessageEntry

logger = logging.getLogger(__name__)


class Spreadsheet:
    def __init__(self, filename):
        self._gc = gspread.service_account()
        self.filename = filename

    @property
    def spreadsheet(self):
        # Open the spreadsheet connection. If we only do this once, the connection can drop.
        return self._gc.open(self.filename)

    def update_time(self):
        """
        Updates the "Last update" field in the spreadsheet. Represents the time
        of the last archival.
        """
        try:
            sheet2 = self.spreadsheet.get_worksheet(1)
        except gspread.exceptions.WorksheetNotFound:
            sheet2 = self.spreadsheet.add_worksheet('Meta', None, None)

        sheet2.update_acell('A1', 'Last update')
        sheet2.update_acell('B1', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def create_headers(self):
        """
        Create the headers for the spreadsheet.
        """
        headers = ["Message ID", "Channel", "Author",
                   "Timestamp", "URL", "Message Content", "Jump URL"]
        self.spreadsheet.sheet1.insert_row(headers, 1)

    def write(self, cell: str, content: str):
        self.spreadsheet.sheet1.update_acell(cell, content)

    def purge(self):
        """
        Delete all rows in the spreadsheet and regenerate the header row.
        """
        # Clear all rows
        self.spreadsheet.sheet1.clear()
        # Regenerate headers
        self.create_headers()
        logger.info(f'Spreadsheet {self.filename} purged !')

    def get(self, cell: str, sheet_index: int = 0):
        try:
            sheet = self.spreadsheet.get_worksheet(sheet_index)
        except gspread.exceptions.WorksheetNotFound:
            return None

        return sheet.get(cell)

    def append_row(self, entry: MessageEntry):
        """
        Append a single row representing the message entry.
        """

        # Convert the dataclass instance into a list
        row = entry.to_row()
        self.spreadsheet.sheet1.append_row(row)
        self.update_time()
        logger.info(f'Appended row to spreadsheet {self.filename}!')

    def append_rows(self, entries: list[MessageEntry]):
        """
        Append multiple rows representing message entries.
        """
        rows = [e.to_row() for e in entries]

        self.spreadsheet.sheet1.append_rows(rows)
        self.update_time()
        logger.info(f'Appended rows to spreadsheet {self.filename}!')

    def get_archived_message_ids(self):
        """
        Retrieve all the archived message IDs from the spreadsheet.
        We assume that message IDs are stored in the first column.
        """
        message_ids = self.spreadsheet.sheet1.col_values(1)
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
    # sh.purge()
    sh.append_row(entry)
