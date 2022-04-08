from datetime import date


def year(request):
    """Функция year возвращающая текущий год,
    отображается в подвале страницы.
    """

    a = date.today()
    a = str(a)[0:4]
    a = int(a)
    d = dict()
    d[a] = a
    return {'year': a}
