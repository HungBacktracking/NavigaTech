from datetime import datetime


class DateFormater:
    @staticmethod
    def format_date(d: str):
        if not d:
            return None
        return datetime.strptime(d, "%d-%m-%Y").date()