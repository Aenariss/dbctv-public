## @file app
# @author Vojtech Fiala <xfiala61>
#
# Soucast bakalarske prace Databaze Vysilani Ceskoslovenske Televize, 2022
#
# Backend weboveho rozhrani.

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import datetime
import json
from utils.utils import *
import unidecode

# vytvoreni flask app
app = Flask(__name__)
# config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sql'  # muze byt nutne nahrat databaze do instance/db.sql...
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# vytvoreni rozhrani nad db
db = SQLAlchemy(app)

## Vychozi datum
DEFAULT_DATE = '1992-12-24'
## Vychozi datum v ceskem formatu
DEFAULT_DATE_CZ = '24.12.1992'

## Trida reprezentujici tabulku Person
class Person(db.Model):
    __tablename__ = 'Person'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    name = db.Column(db.String())
    shadowName = db.Column(db.String())

## Trida reprezentujici tabulku Role
class Role(db.Model):
    __tablename__ = "Role"
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    name = db.Column(db.String())

## Trida reprezentujici tabulku Series
class Series(db.Model):
    __tablename__ = "Series"
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    name = db.Column(db.String())
    shadowName = db.Column(db.String())

## Trida reprezentujici tabulku Time
class Time(db.Model):
    __tablename__ = "Time"
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    timeAiring = db.Column(db.String(), primary_key=True)

## Trida reprezentujici tabulku Date
class Date(db.Model):
    __tablename__ = "Date"
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    date = db.Column(db.String(), primary_key=True)

## Trida reprezentujici tabulku Description
class Description(db.Model):
    __tablename__ = "Description"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.String())

## Trida reprezentujici tabulku Country
class Country(db.Model):
    __tablename__ = "Country"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String())

## Trida reprezentujici tabulku AiredAtTime
class AiredAtTime(db.Model):
    __tablename__ = "AiredAtTime"
    id = db.Column(db.Integer(), primary_key=True)
    series_id = db.Column(db.Integer(), db.ForeignKey("Series.id"))
    time_id = db.Column(db.Integer(), db.ForeignKey("Time.id"))
    date_id = db.Column(db.Integer(), db.ForeignKey("Date.id"))
    country_id = db.Column(db.Integer(), db.ForeignKey("Country.id"))
    programme = db.Column(db.Integer())
    desc_id = db.Column(db.Integer(), db.ForeignKey("Description.id"))

## Trida reprezentujici tabulku PersonPlays
class PersonPlays(db.Model):
    __tablename__ = "PersonPlays"
    id_person = db.Column(db.Integer(), db.ForeignKey("Person.id"), primary_key=True)
    id_aired = db.Column(db.Integer(), db.ForeignKey("AiredAtTime.id"), primary_key=True)
    id_role = db.Column(db.Integer(), db.ForeignKey("Role.id"))

## Funkce na nacteni data z pripadneho GETu
# Pokud bylo datum zadano, zpracuje jej -- jinak nastavi default
# @return arg Datum jako string
def getDate():
    arg = request.args.get('date')  # Nacti datum z kalendare
    # kdyz jsem nemel zadny argument z getu (prvni pristup na stranku), nastavim default
    if (arg == None or arg == ''):
        arg = DEFAULT_DATE
    else:
        arg = checkDate(arg)
        if arg == False:
            arg = DEFAULT_DATE
    return arg

## Hlavni stranka (index)
# Root cesta
# Funguje s GET metodou
@app.route('/', methods=["GET"])
def index():
    print(db)
    arg = getDate()
    try:    # dodatecna kontrola ze datum je v poradku
        date_check = convertDashDate(arg)   # zkonvertuj datum
    except:
        return badRequest(400)

    highlight = request.args.get('highlight')   # zjisti, jestli je nejaky vybray sloupec
    if request.args.get('highlight') == '' or request.args.get('highlight') == None:
        highlight = ""
    programme = request.args.get('programme')   # zjisti predchozi program
    if (programme == None or programme == ''):
        programme = "1"
    country = request.args.get('country')   # zjisti predchozi zemi vysilani
    if (country == None or country == ''):
        country = "CZ"
    
    week = str(getWeek(datetime.datetime.strptime(arg, '%Y-%m-%d'))) + ". týden"    # string s tydnem pro priblizeni jaky je tyden

    # najdi prvni a poslendi den v danem tydnu
    dt = datetime.datetime.strptime(arg, '%Y-%m-%d').date()
    start_week = (dt - datetime.timedelta(days=dt.weekday()))

    days, dates = [], []
    country_id = db.session.query(Country).filter_by(name=country).first()  # ziskej z databaze zem vysilani
    if country_id == None:
        country_id = country
    else:
        country_id = country_id.id
    weekday = None
    for i in range(0,7):
        date = start_week + datetime.timedelta(days=i)
        if date == dt:
            weekday = getDay(i) # ziskej dny vysilani
        tmp = db.session.query(AiredAtTime, Series, Date, Time, Description).join(Series).join(Date).join(Time).join(Description).filter(Date.date == date,\
                Series.id == AiredAtTime.series_id, AiredAtTime.programme == programme, AiredAtTime.country_id == country_id).order_by(Time.timeAiring.asc()).all()   # ziskej porady pro dany den
        days.append(sortTime(tmp))
        dates.append(formatDate(date))

    saves = [programme, country]
    times = [dt - datetime.timedelta(days=7), dt + datetime.timedelta(days=7)]
    arg = convertDate(arg)
    return render_template('index.html', times=times, dates=dates, days=days, def_val=arg, date_check=date_check,\
                            year=arg[0:4], week=week, saves=saves, weekday=weekday, search=0, highlight=highlight)

## Vyhledavani poradu
# pracuje s metodou GET
@app.route('/searchSeries', methods=["GET"])
def searchSeries():
    arg = convertDate(getDate())
    if request.args.get('searchbar_film') != None or request.args.get('searchbar_film') != '':  # Kdyz nebyl zadan zadny porad, je to chyba
        if (len(request.args.get('searchbar_film')) < 2):
            return badRequest(400)

        search_text = '%' + request.args.get('searchbar_film') + '%'    # Pridej k hledanemu textu procenta reprezentujici wildcard

    arg = request.args.get('date')
    # Kdyz nebyl vybrany datum, vyber
    if (arg == None):
        arg = DEFAULT_DATE
    
    # ziskej prvnich 800 vysledku z databaze poradu, predtim preved hlednay text na ASCII kvuli podpore vyhledavani bez diakritiky
    results = db.session.query(AiredAtTime, Series, Date, Time, Country).join(Series).join(Date).join(Time).join(Country).filter\
             (Series.shadowName.ilike(unidecode.unidecode(search_text)), Series.id == AiredAtTime.series_id).limit(800).all() 
    if (search_text == "%%"):
        results = []
    
    dates = []
    for result in results:
        dates.append(formatDate(datetime.datetime.strptime(result[2].date, "%Y-%m-%d")))    # zformatuj jejich data vysilani

    arg = convertDate(arg)
    return render_template('searchSeries.html', results=results, dates=dates, def_val=arg, week="", search=1, text=search_text[1:-1])

## Vyhledavani osob
# pracuje s metodou GET
@app.route('/searchPeople', methods=["GET"])
def searchPeople():
    arg = convertDate(getDate())
    if request.args.get('searchbar_people') != None or request.args.get('searchbar_people') != '':  # kdyz nebyl zadan text, chyba
        if (len(request.args.get('searchbar_people')) < 2):
            return badRequest(400)

        search_text = '%' + request.args.get('searchbar_people') + '%'

    arg = request.args.get('date')
    if (arg == None or arg == ''):
        arg = DEFAULT_DATE

    ppl = Person.query.filter(Person.shadowName.ilike(unidecode.unidecode(search_text))).all()  # Ziskej jmena osob, predtim preved ziskany text na ASCII kvuli diakritice
    results = []
    people = []

    # Pro kazdou nalezenou osobu vyhledej porady, ve kterych se vyskytovala
    for pl in ppl:
        res = PersonPlays.query.filter_by(id_person=pl.id).all()    # vsechny porady kde osoba hrala
        if res != []:
            for series in res:  # Pro kazdy porad ziskej jeho informace
                srs = db.session.query(AiredAtTime, Series, Date, Time, Country).join(Series).join(Date).join(Time).join(Country).filter(AiredAtTime.id == series.id_aired).order_by(Date.date.asc()).all()
                role_name = db.session.query(Role).get(series.id_role).name
                people.append([pl.name, role_name])
                results.append(srs)

    if (search_text == "%%"):
        results = []

    dates = []

    for result in results:
        dates.append(formatDate(datetime.datetime.strptime(result[0][2].date, "%Y-%m-%d")))

    arg = convertDate(arg)
    return render_template('searchPeople.html', dates=dates, results=results, def_val=arg, week="", people=people, search=1, text=search_text[1:-1])

## Stranka s informacemi o projektu
@app.route('/infopage', methods=["GET"])
def infopage():
    arg = convertDate(getDate())
    return render_template('infopage.html', search=1, def_val=arg)

## AJAX stranka pro podporu automatickeho doplnovani pri vyhledavani
@app.route('/autocompleteSeries', methods=["GET"])
def autocompleteSeries():
    search_text = request.args.get('term')
    switch = request.args.get('switch') # Podle prepinace zjisti, jestli se vyhledava osoba nebo porad
    # moc kratky text nema cenu zkouset zpracovat
    if search_text == None:
        search_text = ""
    if len(search_text) < 3:
        return ""
    search_text = '%' + search_text + '%'
    results_limit = 15 # pouze prvnich 15 vysledku v obou pripadech
    if switch == "1":
        results = db.session.query(Series.name).where(Series.shadowName.ilike(unidecode.unidecode(search_text))).limit(results_limit).all()
    elif switch == "2":
        results = db.session.query(Person.name).where(Person.shadowName.ilike(unidecode.unidecode(search_text))).limit(results_limit).all()
    else:
        return ""
    names = []
    for result in results:
        result = result[0]
        names.append(result)
    return json.dumps(names)    # zformatuj vysledek na json

#################
# ERROR STRANKY #
#################

## Chyba 400 - Spatny request
@app.errorhandler(400)
def badRequest(error):
    arg = DEFAULT_DATE_CZ
    return render_template('errors/400.html', search=1, def_val=arg), 400

## Chyba 404 - Not found
@app.errorhandler(404)
def pageNotFound(error):
    arg = DEFAULT_DATE_CZ
    return render_template('errors/404.html', search=1, def_val=arg), 404

## Chyba 405 - Pristup zamitnut
@app.errorhandler(405)
def notAllowedMethod(error):
    arg = DEFAULT_DATE_CZ
    return render_template('errors/405.html', search=1, def_val=arg), 405

## Chyba 500 - Vnitrni chyba
@app.errorhandler(500)
def internalError(error):
    arg = DEFAULT_DATE_CZ
    return render_template('errors/500.html', search=1, def_val=arg), 500
