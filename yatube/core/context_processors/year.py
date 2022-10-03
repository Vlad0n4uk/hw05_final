import datetime as dt


def year(request):
    return {
        'year': dt.date.today().year
    }
