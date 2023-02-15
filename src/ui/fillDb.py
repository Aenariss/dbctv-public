## @file fillDb
# @author Vojtech Fiala <xfiala61>
#
# Soucast bakalarske prace Databaze Vysilani Ceskoslovenske Televize, 2022
#
# Slouzi k nacteni extrahovanych, uz upravenych, poradu do databaze.

import sqlalchemy
import sys
import re
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import datetime
import unidecode

Base = declarative_base()
engine = sqlalchemy.create_engine('sqlite:///db.sql')  # Pripojeni na sqlite db
connection = engine.connect()   # vytvoreni spojeni
Session = sessionmaker(bind=engine)() # vytvoreni aktualniho session

## Trida reprezentujici tabulku Person
class Person(Base):
    __tablename__ = 'Person'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    shadowName = Column(String)

## Trida reprezentujici tabulku Role
class Role(Base):
    __tablename__ = "Role"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)

## Trida reprezentujici tabulku Country
class Country(Base):
    __tablename__ = "Country"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)

## Trida reprezentujici tabulku Series
class Series(Base):
    __tablename__ = "Series"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    shadowName = Column(String)

## Trida reprezentujici tabulku Time
class Time(Base):
    __tablename__ = "Time"
    id = Column(Integer, primary_key=True, autoincrement=True)
    timeAiring = Column(String)

## Trida reprezentujici tabulku Date
class Date(Base):
    __tablename__ = "Date"
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(String)

## Trida reprezentujici tabulku Description
class Description(Base):
    __tablename__ = "Description"
    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String)

## Trida reprezentujici tabulku AiredAtTime
class AiredAtTime(Base):
    __tablename__ = "AiredAtTime"
    id = Column(Integer, primary_key=True, autoincrement=True)
    series_id = Column(Integer, ForeignKey("Series.id"))
    time_id = Column(Integer, ForeignKey("Time.id"))
    date_id = Column(Integer, ForeignKey("Date.id"))
    country_id = Column(Integer, ForeignKey("Country.id"))
    programme = Column(String)
    desc_id = Column(Integer, ForeignKey("Description.id"))
    #ForeignKeyConstraint(['day','month','year'],['Date.day', 'Date.month', 'Date.year'])   # constraint na vicenasobny cizi klic, uz neni relevantni

## Trida reprezentujici tabulku PersonPlays
class PersonPlays(Base):
    __tablename__ = "PersonPlays"
    id_person = Column(Integer, ForeignKey("Person.id"), primary_key=True)
    id_aired = Column(Integer, ForeignKey("AiredAtTime.id"), primary_key=True)
    id_role = Column(Integer, ForeignKey("Role.id"))

## Funkce na vypis napovedy
def printHelp(ex=0):
    print("Spusteni je: python ./fillDb.py <year> <soubor_s_porady>")
    exit(ex)

## Funkce na ziskani vlozeneho primarniho klice
# 
# Odstrani neporadek ktery k nemu sqlalchemy vklada
#
# @param key Ziskany primarni klic
# @return key Upraveny primarni klic
def getNormalKey(key):
    key = str(key)
    key = key.replace('(', '')
    key = key.replace(')', '')
    key = key.replace(',', '')
    key = key.replace('\'', '')
    return key

## Funkce na urceni, jestli muzou byt 2 slova jmeno
#
# @param name Jmeno
# @param surname Prijmeni
# @return Hodnota reprezentujici zda bylo nalezeno obycejne jmeno a nebo ma osoba titul
def isName(name, surname):
    split_dot = name.split('.') # Rozdel jmeno podle tecky (J. Dietl)
    if (len(split_dot) == 2):
        flag = 1
        for nm in split_dot:
            if not nm.isalpha():    # Jestlize jmeno obsahuje cisla, neni to jmeno
                flag = 0
        if flag:
            return 4

    if len(split_dot) == 3:
        if split_dot[2] == '':  # Pokud byl mezi jmeny prazdny string, dej to vedet
            return 4

    split_comma = name.split(',')   # Jestli se nepovedlo podle tecky, zkus carku (J, Dietl)
    if (len(split_comma) == 2):
        flag = 1
        for nm in split_comma:
            if not nm.isalpha():
                flag = 0
        if flag:
            return 4

    if (name[0] == name[0].upper() and surname[0] == surname[0].upper() and name[0].isalpha() and surname[0].isalpha()):
        return 1
    # Muzou taky ale tvorit titul zaslouzileho umelce/umelkyne
    if ("ZASL" in name.upper() and "UMĚL" in surname.upper()):
        return 2
    # muze mit clovek taky titul
    elif (re.search("^(ing)", name)):
        return 3
    return False

## Funkce na urceni klicovych slov v podobe roli
# 
# @param word Slovo ve kterem je role hledana
# @return Vysledek hledani
def isRole(word):
    word = word.upper()
    return re.search("(SCÉNA|KAMERA|REŽIE|UVÁDÍ|HUDBA|SCÉNÁŘ)", word)

# Funkce na zpracovani jmen v nactenem poradu
#
# @param line Popis poradu obsahujici pripadne jmena
# @return fixed_names Seznam s jmeny osob
# @return roles Role ziskanych osob
def personName(line):
    words = line.split()    # rozdel string na slova
    limit = len(words)
    position = 0

    names = []
    roles = []

    while position < limit:
        # Jestlize bylo nalezeno klicove slovo
        if (isRole(words[position])):
            # A je za nim mozne najit potencialni jmeno
            if (limit > position+2):
                # Vyhledej jmeno a zkontroluj, jestli neni zaslouzilym umelcem nebo nema titul
                tmp_res = isName(words[position+1], words[position+2])
                # Jestlize je zaslouzily umelec, vem to v potaz
                if (tmp_res == 2):
                    if (limit > position+4):
                        if isName(words[position+3], words[position+4]):
                            names.append(words[position+3] + ' ' + words[position+4])
                            roles.append(words[position])
                            position += 3   # o 1 se posune vzdy, takze zbyvaji 3
                # nema titul ani neni zaslouzily umelec
                elif (tmp_res == 1):
                    names.append(words[position+1] + ' ' + words[position+2])
                    roles.append(words[position])
                    position += 1
                # clovek ma titul, kontrola ze je jmeno za titulem validni
                elif (tmp_res == 3):
                    if (limit > position+3):
                        if isName(words[position+2], words[position+3]):
                            names.append(words[position+2] + ' ' + words[position+3])
                            roles.append(words[position])
                            position += 2
                elif (tmp_res == 4):
                    names.append(words[position+1])
                    roles.append(words[position])
        
        # Specialni case pro bezne herce, kterych muze byt psanych hodne
        elif ("HRAJÍ" in words[position].upper()):
            position += 1
            while position < limit:
                if limit > position+2:
                    tmp_res = isName(words[position], words[position+1])
                    if (tmp_res == 2):
                        if (limit > position+4):
                            if isName(words[position+2], words[position+3]):
                                names.append(words[position+2] + ' ' + words[position+3])
                                roles.append("Herec")
                                position += 3   # o 1 se posune vzdy, takze zbyvaji 3
                    elif (tmp_res == 1):
                        if (limit > position+2):
                            names.append(words[position] + ' ' + words[position+1])
                            roles.append("Herec")
                            position += 1
                    elif (tmp_res == 3):
                        if isName(words[position+1], words[position+2]):
                            names.append(words[position+1] + ' ' + words[position+2])
                            roles.append(words[position])
                            position += 2
                    else:
                        position -= 1
                        break
                position += 1

        position += 1
        
    # odstraneni tecek a carek co mohli zbyt
    fixed_names = []
    for name in names:
        if name[-1] == ',' or name[-1] == '.':
            fixed_names.append(name[:-1])
        else:
            fixed_names.append(name)
    return fixed_names, roles

## Funkce pro konverzi data do casoveho formatu pro sqlite
#
# Chteny format je YYYY-MM-DD
#
# @param day Den vysilani
# @param month Mesic vysilani
# @param year Rok vysilani
# @return date Zformatovane datum
def makeDate(day, month, year):
    month = str(month); year = str(year); day = str(day) # zkonvertuj na stringy
    if len(month) == 1:
        month = "0" + month
    if len(day) == 1:
        day = "0" + day
    date = year + '-' + month + '-' + day
    return date

## Funkce pro ziskani data vysilani
# 
# @param line Nacteny radek s poradem
# @return zformatovane datum
def getDate(line):
    time = re.match("^([0-9]+)\. ?([0-9]+)\. ?([0-9]+)", line)
    day = time.group(1); month = time.group(2); year = time.group(3)
    return makeDate(day, month, year)

## Funkce pro ziskani casu vysilani z radku
# 
# @param line Radek s poradem
# @return x Regex match
def getTime(line):
    x = re.match("^([0-9]{1,2}).*?\.([0-9]{1,2}).*?", line)
    return x

## Funkce pro ziskani cisla programu
# 
# @param line Nacteny radek
# @return x Regex s cislem programu
def getProgramme(line):
    x = re.match("^([1-3])\s+?.*?$", line)
    return x.group(1)

## Funkce pro editaci popisu poradu
#
# Slovenske porady nemivali zadny popis az do roku 90
# Presto se do nich mohl nacist viceradkovy nazev, tedy popis nesmi byt delsi nez 25 znaku
# Jinak take nebyval delsi nez cca 50 znaku
#
# @param desc Popis poradu
# @param country Zeme vysilani
# @param date Datum vysilani
# @return desc Zformatovany popis poradu
def editDesc(desc, country, date):
    if country == "SK":
        date = datetime.datetime.strptime(date, "%Y-%m-%d")
        svt_beginning = datetime.datetime(1990, 10, 1)  # pocatek vysilani slovenske televize (s1, stv)
        if date < svt_beginning:    # Pokud jsem pred pocatkem vysilani STV, popisy temer nebyly a mohl byt jen zbytek nazvu poradu
            if len(desc) > 25:
                desc = ''
        else:   # Jinak byly popisy jen velmi kratke
            if len(desc) > 50:
                desc = ''
    return desc

## Funkce pro zapsani prikazu do databaze
#
# Prikazem se rozumi insert statement
# 
# @param sql_cmd sqlalchemy verze sql prikazu, co ma byt zapsan
# @return pk Primarni klic vlozene veci
def compileStatement(sql_cmd):
    sql_cmd.compile()
    res = connection.execute(sql_cmd)
    pk = res.inserted_primary_key
    pk = getNormalKey(pk)
    return pk

## Funkce pro nahrani dat do databaze
def loadData():
    if "--help" in sys.argv or "-h" in sys.argv:
        printHelp()
    
    try:
        year = sys.argv[1]  # ziskej rok ktery se nahrava
        file = open('../series_edited/tv-series-' + year + "_improved.txt", 'r', encoding="utf-8")  # podle roku otevri soubor s vylepsenymi porady
    except:
        printHelp(ex=1)

    lines = file.readlines()
    date_pk, person_pk, role_pk, series_pk, time_pk, country_pk, aired_pk = None, None, None, None, None, None, None
    date = None
    programme = None
    expect_date, expect_programme = False, False
    country = ""
    line_n = 1
    all_lines = len(lines)
    for line in lines:
        print("parsin line " + str(line_n) + '/' + str(all_lines))
        line_n += 1

        # Jestlize ctu prazdny radek, pokracuju
        if re.search("^\s+$", line):
            continue
        
        # Nastaveni CZ nebo SK programu
        x = re.search("^(CZ|SK)\s*?$", line)
        if (x):
            country = x.group(1)
            country_pk = Session.query(Country).filter_by(name=country).first()
            if not country_pk:
                sql_cmd = sqlalchemy.insert(Country).values(name=country)
                country_pk = compileStatement(sql_cmd)
            else:
                country_pk = country_pk.id
            expect_date = True
            continue

        # Jestlize predchazela zeme, nasledovat bude datum
        if expect_date == True:
            date = getDate(line)
            expect_programme = True
            expect_date = False
            continue

        # Jestlize predchazelo datum, nasleduje cislo programu
        elif expect_programme == True:
            programme = getProgramme(line)
            expect_programme = False
            continue
        

        time = getTime(line)
        time_insert = str(time.group(1)) + ':' + str(time.group(2))
        line = line[time.span()[1]+1:]  # radek bez casu
        name_series = line[:re.search("NAZEVPORADU", line).span()[0]-1] # nazev poradu
        desc = line[re.search("NAZEVPORADU", line).span()[1]+1:] # popis poradu
        desc = editDesc(desc, country, date)  # editace pripadneho neplatneho popisu

        names, roles = personName(desc)
        
        # prazdny desc vkladej jako empty string, None dela problemy pri zobrazovani (vypisuje se literally jako None)

        # vkladani popisu
        desc_pk = Session.query(Description).filter_by(description=desc).first()
        if not desc_pk:
            sql_cmd = sqlalchemy.insert(Description).values(description=desc)
            desc_pk = compileStatement(sql_cmd)
        else:
            desc_pk = desc_pk.id

        # vkladani datumu
        date_pk = Session.query(Date).filter_by(date=date).first()
        if not date_pk:
            sql_cmd = sqlalchemy.insert(Date).values(date=date)
            date_pk = compileStatement(sql_cmd)
        else:
            date_pk = date_pk.id

        # vkladani poradu
        series_pk = Session.query(Series).filter_by(name=name_series).first()
        if not series_pk:
            sql_cmd = sqlalchemy.insert(Series).values(name=name_series, shadowName=unidecode.unidecode(name_series))
            series_pk = compileStatement(sql_cmd)
        else:
            series_pk = series_pk.id
        
        # vkladani casu
        time_pk = Session.query(Time).filter_by(timeAiring=time_insert).first()
        if not (time_pk):
            sql_cmd = sqlalchemy.insert(Time).values(timeAiring=time_insert)
            time_pk = compileStatement(sql_cmd)
        else:
            time_pk = time_pk.id

        # vkladani kombinace vseho
        already_in = Session.query(AiredAtTime).filter_by(series_id=series_pk, time_id=time_pk, date_id=date_pk, country_id=country_pk, programme=programme, desc_id=desc_pk).first()
        if not (already_in):
            sql_cmd = sqlalchemy.insert(AiredAtTime).values(series_id=series_pk, time_id=time_pk, date_id=date_pk, country_id=country_pk, programme=programme, desc_id=desc_pk)
            aired_pk = compileStatement(sql_cmd)
        else:
            aired_pk = already_in.id

        # vkladani osob a jejich roli
        if (names != []):
            index_tmp = 0
            for name in names:
                person_pk = Session.query(Person).filter_by(name=name).first()
                role_pk = Session.query(Role).filter_by(name=roles[index_tmp]).first()
                if not (person_pk):
                    sql_cmd = sqlalchemy.insert(Person).values(name=name, shadowName=unidecode.unidecode(name))
                    person_pk = compileStatement(sql_cmd)
                else:
                    person_pk = person_pk.id
                if not role_pk:
                    sql_cmd = sqlalchemy.insert(Role).values(name=roles[index_tmp])
                    role_pk = compileStatement(sql_cmd)
                else:
                    role_pk = role_pk.id
                index_tmp += 1

                person_plays = Session.query(PersonPlays).filter_by(id_person=person_pk, id_aired=aired_pk).first()
                if not (person_plays):
                    sql_cmd = sqlalchemy.insert(PersonPlays).values(id_person=person_pk, id_role=role_pk, id_aired=aired_pk)
                    sql_cmd.compile()
                    connection.execute(sql_cmd)

if __name__ == "__main__":
    loadData()
