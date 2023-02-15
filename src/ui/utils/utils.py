## @file utils
# @author Vojtech Fiala <xfiala61>
#
# Soucast bakalarske prace Databaze Vysilani Ceskoslovenske Televize, 2022
#
# Pomocne funkce pro webove rozhrani

import datetime

## Funkce pro ziskani tydne z data
# 
# @param date Datum
# @return Cislo tydne, do jakeho datum patri
def getWeek(date):
    return date.isocalendar()[1]

## Funkce pro ziskani dne z data
# 
# @param date Datum
# @return Den z data
def getDay(date):
    date = str(date)
    date = date.split('-')
    return date[2][:2]

## Funkce pro ziskani mesice z data
# 
# @param date Datum
# @return Mesic z data
def getMonth(date):
    date = str(date)
    date = date.split('-')
    return date[1][:2]

## Funkce pro ziskani poctu dnu v mesici
# 
# @param month Mesic
# @param year Rok
# @return Pocet dnu v mesici
def daysMonth(month, year):
    if month in [1, 3, 5, 7, 8, 10, 12]:
        return 31
    if month == 2:
        if year % 4 == 0:   # prechodny unor
            return 29
        else:
            return 28
    return 30

## Funkce na zformatovani data
#
# @param date Datum
# @return Zformatovane datum
def formatDate(date):
    try:
        date = date.strftime("%d. %m. %Y")
    except:
        return "error!"
    return str(date)

## Funkce pro ziskani dne podle cisla
#
# @param i Hodnota dne
# @return Den odpovidajici hodnote, anglicky
def getDay(i):
    if i == 0:
        return "Monday"
    elif i == 1:
        return "Tuesday"
    elif i == 2:
        return "Wednesday"
    elif i == 3:
        return "Thursday"
    elif i == 4:
        return "Friday"
    elif i == 5:
        return "Saturday"
    elif i == 6:
        return "Sunday"

## Funkce na dodatecne serazeni podle casu (0:10 pr. ma byt na konci programu), sqlite radi 0:10 jako prvni
#
# @param series Seznam poradu
# @return Serazene porady podle casu
def sortTime(series):
    length = len(series)
    counter, i = 0, 0
    while counter < length:
        hour = int(series[i][3].timeAiring[:2])
        if hour < 5:    # Jestlize je mene nez 5 hodin, dam to nakonec
            tmp = series[i]
            series.pop(i)   # vyhodim porad
            series.append(tmp)  # vlozim porad na konec
            i -= 1
        counter += 1
        i += 1
    return series

## Funkce pro zjisteni, jestli je zadane datum ve zpracovanem rozmezi
#
# Jestlize neni, je zformatovano na nejvyssi nebo nejnizsi moznou hodnotu
#
# @param x Datum
# @return Pripadne opravena hodnota data
def dateInRange(x):
    min = datetime.datetime(1965, 12, 27)
    max = datetime.datetime(1992, 12, 31)
    if x > max:
        x = max  # kdyz nekdo prekroci, poslu ho na posledni
    if x < min:
        x = min  # a nebo na prvni
    str_x = x.strftime("%Y-%m-%d")
    return str_x

## Funkce co zajisti, ze nepujde napsat nevalidni datum
#
# V pripade prekroceni limitu nastavi na nejblizsi nejvyssi/nejnizsi moznou hodnotu
#
# @param spl Datum
# @param flag Vlajka urcujici format data (YYYY-MM-DD nebo DD-MM-YYYY), default YYYY...
# @return day Den
# @return month Mesic
# @return year Rok
def checkMaxDay(spl, flag=0):
    month, year, day = None, None, None
    if not flag:
        month = int(spl[1]); day = int(spl[2]); year = int(spl[0])
    else:
        month = int(spl[1]); day = int(spl[0]); year = int(spl[2])
    if month > 12:
        month = 12
    elif month <= 0:
        month = 1
    maxDay = daysMonth(month, year)   # zjisti max dnu v mesici
    if day > maxDay:
        day = maxDay
    elif day <= 0:
        day = 1
    if year <= 0:
        year = 1965
    elif year > 1992:
        year = 1992
    return day, month, year

## Funkce na kontrolu data
#
# @param date Zadane datum
# @return Pripadne opravena hodnota data
def checkDate(date):
    spl = date.split('.')   # lze splitnout bud teckou
    x = None
    if len(spl) != 3:
        spl = date.split('-')   # nebo pomlckou, to urcuje styl
        if len(spl) != 3:
            return False
        try:
            day, month, year = checkMaxDay(spl)
            x = datetime.datetime(year=year,month=month,day=day)
        except:
            return False

        return dateInRange(x)
        
    else:
        try:
            day, month, year = checkMaxDay(spl, flag=1)
            x = datetime.datetime(year=year,month=month,day=day)
        except:
            return False

        return dateInRange(x)

## Funkce pro konverzi data z pomlcek na tecky, z YYYY.. na DD-MM.
#
# @param date Datum
# @return date Zkonvertovane datum
def convertDate(date):
    date = date.split('-')
    date = date[2] + '.' + date[1] + '.' + date[0]  # Poprehazuj rok a den
    return date

## Funkce pro konverzi data z tecek na pomlcky
#
# @param date Datum
# @return Pripadne zformatovane datum
def convertDashDate(date):

    spl = date.split('-')
    if len(spl) == 3:   # uz je zformatovane
        return date
    else:
        spl = date.split('.')   
        try:    # kontrola validity data
            x = datetime.datetime(year=int(spl[2]),month=int(spl[1]),day=int(spl[0]))
        except:
            return False
        return spl[2] + '-' + spl[1] + '-' + spl[0]
        