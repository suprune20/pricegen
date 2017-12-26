from django.core.validators import RegexValidator
import decimal

class ShortNameValidator(RegexValidator):
    regex=r'^[0-9A-Za-z_-]{3,20}$'
    message='3 - 20 латинских букв, цифр, -, _'

    def __init__(self):
        super(ShortNameValidator, self).__init__(regex=self.regex)

def time_human(mins):
    """
    Время из минут в '?? час. ?? мин.'
    """
    mins_ = mins % 60
    hours_ = int(mins / 60)
    result = ''
    if hours_:
        result += '%s час.' % hours_
    if mins_ and hours_:
        result += ' '
    if mins_:
        result += '%s мин.' % mins_
    return result

def round_decimal(num, precision=0):
    """
    Округление числа, в т.ч. до сотни. Возвращает decimal.Decimal
    
    num :       число, может быть decimal, int, float
    precision:  сотые, -2, до 1: 0, до сотни: 2
    """
    DECPLACES = decimal.Decimal(10) ** precision
    if precision <= 0:
        return decimal.Decimal(num).quantize(DECPLACES, rounding=decimal.ROUND_HALF_UP)
    else:
        DECPLACES2 = DECPLACES/2
        return ((decimal.Decimal(num) + DECPLACES2) // DECPLACES) * DECPLACES
