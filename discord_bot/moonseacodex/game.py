import re

from datetime import datetime

re_name = r"\*\*Adventure:\*\*\s*(.*?)\n"
re_module = r"\*\*Module Code:\*\*\s*(.*?)\n"
re_dm = r"\*\*DM:\*\*\s<@(.*?)>"
re_date = r"\*\*Date:\*\*\s*<t:(.*?):F>"

re_gold = r"\*\*Gold per player\*\*:\s*(.*?)\n"
re_downtime = r"You also receive (.*?) days of downtime"


class Game:
    dm: str = None
    name: str = ""
    module: str = ""
    date: datetime = None
    gold: int = 0
    downtime: int = 10
    items: list = []
    consumables: list = []

    def __init__(self, raw_string):
        try:
            self.name = re.search(re_name, raw_string).group(1).strip()
            self.module = re.search(re_module, raw_string).group(1).strip()
            self.dm = re.search(re_dm, raw_string).group(1).strip()
            date_string = re.search(re_date, raw_string).group(1).strip()
            self.date = datetime.fromtimestamp(int(date_string))

            try:
                self.gold = int(re.search(re_gold, raw_string).group(1).strip())
            except Exception as e:
                self.gold = 0
            try:
                self.downtime = int(re.search(re_downtime, raw_string).group(1).strip())
            except Exception as e:
                self.downtime = 10
        except Exception as e:
            print(e)
            return None
        if not self.dm or not self.name or not self.module or not self.date:
            return None
