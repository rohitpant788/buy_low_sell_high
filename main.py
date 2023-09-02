from nsepy import get_history
from datetime import date

icicibank = get_history(symbol='ICICIBANK',
                        start=date(2017, 1, 1),
                        end=date.today())

icicibank.head()