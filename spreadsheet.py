import gspread


class Spreadsheet:
    def __init__(self, filename):
        self._gc = gspread.service_account()
        self.filename = filename
        
    def _sheet(self):
        return self._gc.open(self.filename).sheet1
    
    def write(self, cell: str, content: str):
        self._sheet().update_acell(cell, content)
    
    def purge(self):
        # delete everything but the first line
        sheet = self._sheet()
        rows = sheet.get_all_values()  # Get all data from the sheet
        if len(rows) > 1:  # If there's more than just the header row
            sheet.delete_rows(2, len(rows))  # Delete all rows except the first

    
    def get(self, cell: str):
        return self._sh.get(cell)
    
    def append_row(self, row: list):
        self._sheet().append_row(row)
    
    def append_rows(self, rows: list):
        sheet = self._sheet()
        
        for row in rows:
            sheet.append_row(row)
    
    def get_archived_message_ids(self):
        """
        Retrieve all the archived message IDs from the spreadsheet.
        We assume that message IDs are stored in the first column.
        """
        message_ids = self._sheet().col_values(1)  # Assume message IDs are in the first column
        return set(message_ids)  # Return as a set for fast lookup

    def append_archive_entry(self, message_id: str, author: str, timestamp: str, url: str, message_content: str):
        """
        Append a new row to the spreadsheet containing the message ID, author, timestamp, URL, and message content.
        """
        self.append_row([message_id, author, timestamp, url, message_content])
