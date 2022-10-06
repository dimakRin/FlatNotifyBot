class Error(Exception):
    pass


class WithoutDash(Error):
    pass
#отсуствие тире


class WrongOrder(Error):
    pass
#Первое число больше второго