from django.core.validators import RegexValidator

class ShortNameValidator(RegexValidator):
    regex=r'^[0-9A-Za-z_-]{3,20}$'
    message='3 - 20 латинских букв, цифр, -, _'

    def __init__(self):
        super(ShortNameValidator, self).__init__(regex=self.regex)
