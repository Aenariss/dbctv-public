## @file extractProgram
# @author Vojtech Fiala <xfiala61>
#
# Soucast bakalarske prace Databaze Vysilani Ceskoslovenske Televize, 2022
#
# Slouzi k extrakci casu vysilani a nazvu poradu, vcetne jeho popisu.

import re
import os
import pytesseract
from pytesseract import Output
import sys
from cv2 import imread, waitKey, imshow

## Globalni promenna urcujici nastaveni Tesseractu
TESSERACT_CONFIG = r'-l ces --psm 1 --oem 1'

#pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe' # Kdyby nefungoval Tesseract v PATH, lze nastavit rucne

## Den vysilani
DAY = None
## Mesic vysilani
MONTH = None
## Rok vysilani
YEARR = None

## Funkce na nacteni souboru s programem 
#
# Funkce predpoklada, ze v korenovem adresari existuje slozka "programmes"
# V te slozce jsou soubory ve formatu programmes_<year> obsahujici
# kompletni seznam souboru s programem
#
# @param year Rok, jehoz programy maji byt nacteny
# @return List souboru obsahujicich televizni program
def getPotentialFiles(year):
    try:
        tmp = open("./programmes/programmes_" + str(year) + ".txt", 'r', encoding="utf-8")
    except:
        print("Dany soubor " + 'programmes_' + str(year) + " nebyl ve slozce programmes nalezen!")
        print("Spoustite program ze spravne slozky? (src/)")
        exit(1)
    files = []
    lines = tmp.readlines()

    for line in lines:
        if line[0] != '#':  # "komentare"
            # dulezite, protoze mam i .tif soubory
            try:
                index = line.index('png')
            except:
                index = line.index('tif')
            files.append(line[:index+3])

    return files

## Funkce na zjisteni, jestli existuje soubor s porady pro dany rok
# 
# Pokud neexistuje, vytvori jej
#
# @param year Rok vysilani
def checkProgrammeExistence(year):
    programme_file_name = "tv-series-" + year + ".txt"
    if (os.path.exists(programme_file_name)):
        return
    else:
        f = open(programme_file_name, 'w')
        f.close()

## Funkce na preskoceni prazdnych prvku seznamu
#
# @param current_line Seznam obsahujici stringy
# @param length Delka seznamu
# @param index Pozice, ze ktere preskakovani zacina
# @return Index, na kterem se nenachazi prazdny znak
def skipEmpty(current_line, length, index):
    while index+1 < length:
        index += 1
        if current_line[index] != '':
            break
    return index

## Funkce na urceni, jestli je slovo mesic
#
# Kontroluje, jestli je slovo mesic ve 2. padu 
#
# @param word String ktery ma byt overen
# @return Pravdivostni hodnota jestli je slovo mesic
def isMonth(word):
    word = word.lower()
    if re.search("^ledn", word) or re.search("^únor", word) or re.search("^unor", word) or re.search("^březn", word)\
                                or re.search("^brezn", word) or re.search("^dub", word) or re.search("^květn", word) or re.search("^kvetn", word)\
                                or re.search("^červ", word) or re.search("^cerv", word) or re.search("^cervn", word) or re.search("^srpn", word)\
                                or re.search("^září", word) or re.search("^zari", word) or re.search("^říjn", word) or re.search("^rijn", word)\
                                or re.search("^listop", word) or re.search("^prosin", word) or re.search("^cerve", word):
        return True
    else:
        return False

## Funkce na prepocitani nazvu mesice na jeho ciselne oznaceni
#
# @param word Nazev mesice ve 2. padu
# @return Ciselna hodnota odpovidajici mesici
def monthNumber(word):
    word = word.lower()
    if re.search("^ledn", word):
        return 1
    elif (re.search("^únor", word) or re.search("^unor", word)):
        return 2
    elif re.search("^březn", word) or re.search("^brezn", word):
        return 3
    elif re.search("^dub", word):
        return 4
    elif re.search("^květn", word) or re.search("^kvetn", word):
        return 5
    elif re.search("^červn", word) or re.search("^cervn", word):
        return 6
    elif re.search("^červe", word) or re.search("^cerve", word):
        return 7
    elif re.search("^srpn", word):
        return 8
    elif re.search("^září", word) or re.search("^zari", word):
        return 9
    elif re.search("^říjn", word) or re.search("^rijn", word):
        return 10
    elif re.search("^listop", word):
        return 11
    elif re.search("^prosin", word):
        return 12
    else:
        return 99 # error

## Funkce na zformatovani nacteneho poradu a popisu
# 
# @param current_line Seznam obsahujici porad vcetne popisu a data vysilani
# @return Zformatovany string reprezentujici cas vysilani a informace o poradu s detekovanym nazvem
def createStr(current_line):
    string = ""
    index = 0
    length = len(current_line)
    titleFlag, continueFlag = False, False

    # funkce co detekuije mezery po datu, to znaci novy radek vetsinou... pokud slovo konci - (no-, '', viny), tak vzit i prvni slovo co se nerovna empty
    while (index < length):

        word = current_line[index]
        word = word.replace('\'', '')
        word = word.replace('\"', '')
        
        # jestlize uz mam nazev poradu, nepotrebuju resit prazdne mista
        if titleFlag:
            if word == '':
                index += 1
                continue
        else:
            string += word + ' ' # cas, ktery je vzdy na 1. miste
            # dokud nedojdu ke konci (nebo nenajdu nazev poradu)
            while index+1 < length:
                index += 1
                # jestlize slovo konci pomlckou ale neni to jenom pomlcka, tak jdu dal, dokud nenajdu dalsi slovo
                if (re.search('(-|—)$', current_line[index]) and len(current_line[index]) > 2):
                    string += current_line[index][:-1]
                    index = skipEmpty(current_line, length, index)
                    # jakmile jsem nasel neco co neni mezera, bude to snad druha cast slova
                    string += current_line[index] + ' '
                    break
                # pokud je to jenom pomlcka na zacatku, pokracuju jakoby nic
                elif (re.search('(-|—)$', current_line[index]) and len(string) < 8):
                    continue
                # jinak prictu slovo do nazvu
                else:
                    # jestlize mam prazdny string a zaroven mam nactene vic nez jen cas, je to asi ok a nactu mezeru
                    # pootom lze vyuzit na odstraneni spatnych popisu podle vysokeho poctu mezer na konci
                    if current_line[index] == '' and len(string) > 8:
                        break
                    else:
                        if current_line[index] != '':
                            string += current_line[index] + ' '
            # oznaceni, ze predchazejici text je nazev
            string += 'NAZEVPORADU '
            continueFlag = True
            titleFlag = True

        if not continueFlag:
            if (re.search('(-|—)$', word) and len(word) > 2):
                if (index+1 < length):
                    index = skipEmpty(current_line, length, index)
                    next_word = current_line[index]
                    if (len(next_word) != 1):
                        word = word[:-1] + next_word
                    else:
                        if (index+2 < length):
                            word = word[:-1] + current_line[index+2]
                            index += 2

            string += word
            string += ' '
        continueFlag = False
        index += 1
    string += '\n'
    return string

## Funkce na posunuti mesice v pripade, ze den prekrocil hranici
def resetDay():
    global DAY
    global MONTH
    global YEARR

    if MONTH in [1,3,5,7,8,10,12]:  # 31 dni
        if DAY > 31:
            DAY = 1
            MONTH += 1
    elif MONTH == 2:   # specialni unor
        if YEARR % 4 == 0:
            if DAY > 29:
                DAY = 1
                MONTH += 1
        else:
            if DAY > 28:
                DAY = 1
                MONTH += 1
    else:   # 30 dni
        if DAY > 30:
            DAY = 1
            MONTH += 1

    # novy rok
    if MONTH == 13:
        YEARR += 1
        MONTH = 1
        DAY = 1

## Funkce na urceni, jestli je dane slovo cas
#
# @param word Slovo ktere ma byt kontrolovano
# @return Bool jestli je slovo cas
def isTime(word):
    return re.search("^( |-|„|\()?[0-9]+(\.|,) ?[0-9]+:?((-|—)[0-9]+(\.|,) ?[0-9]+:?)?\.?$", word)

## Funkce na vytvoreni jednotne podoby casu ze slova
# 
# @param word Slovo ze ktereho ma byt cas vytvoren
# @return Cas ve formatu h.mm
def timeify(word):
    numbers = re.findall(r'[0-9]+', word)
    time = ''
    if len(numbers) > 1:
        time = numbers[0] + '.' + numbers[1]
    else:
        time = '99.99'  # invalid sign
    return time

## Funkce pro zpracovani 2. programu pro rok 1970
#
# @param f Soubor s porady
# @param text Nacteny OCR text
def secondProgramme70(f, text):
    length = len(text)
    index = 0
    current_programme = []
    top_line = ''
    while index < length:

        flag = 0
        word = text[index]

        if isTime(word):
            current_programme, flag, _ = newTime(f, word, current_programme)

        # Jestlize jsem nasel nove datum, musim zapsat
        elif (re.search("[0-9]{1,2}", word) and index+1 < length):
            # Nasleduje za datem mesic? 25. dubna napriklad
            if (isMonth(text[index+1])):
                # Jestlize ano, je to nove vysilani -- zapis stavajici
                if current_programme != []:
                    f.write(createStr(current_programme))
                    current_programme = []
                # Zapis metadata
                f.write("\nCZ")
                top_line = '\n' + word + ' ' + str(monthNumber(text[index+1])) + '. ' + str(YEARR) + '\n' + "2" + "\n"
                f.write(top_line)
                index += 2
                continue
        
        if ("RATISLA" in word.upper() and ("KOŠIC" in text[index+1].upper() or "KOSIC" in text[index+1].upper())):
            # Zapsani posledniho nacteneho z ctv
            f.write(createStr(current_programme))
            current_programme = []

            f.write("\nSK" + top_line + "2" + "\n")
            index += 2
            continue

        if (current_programme != [] and not flag):
            current_programme.append(word)

        # navysuju index, abych ve for loopu vedel, kde jsem a umel se divat i dopredu
        index += 1
    if current_programme != []:
        f.write(createStr(current_programme))

## Funkce pro ziskani OCR textu
#
# @param file Soubor s programem
# @param year Rok do nejz program patri
#
# @return text Ziskany OCR text
# @return f Soubor s porady pro dany rok
def getText(file, year):
    img = imread(file)
    print("OCR nacita soubor...")
    ocr_res = pytesseract.image_to_data(img, output_type=Output.DICT, config=TESSERACT_CONFIG)
    text = ocr_res.get('text')

    f = open('tv-series-' + str(year) + ".txt", 'a', encoding="utf-8")
    return text, f

## Funkce pro prvotni zapis metadat poradu
#
# @param f Soubor s porady
# @param country Zeme vysilani (CZ/SK)
# @param programme Program vysilani
def writeTop(f, country, programme):
    global DAY
    global MONTH
    global YEARR

    top_line = '\n' + str(DAY) + '. ' + str(MONTH) + '. ' + str(YEARR) + '\n' + programme + "\n"
    f.write("\n" + country)
    f.write(top_line)

## Funkce na zapsani aktualniho poradu do souboru 
#
# Taky slouzi k pridani casu do aktualniho poradu
#
# @param f Soubor s porady
# @param word Aktualni resene slovo
# @param current_programme Seznam obsahujici aktualni porad
#
# @return current_programme Seznam s aktualnim poradem
# @return flag Vlajka indikujici ze byl zapsan cas
# @return hour Hodina vysilani aktualniho poradu
def newTime(f, word, current_programme):
    # konverze casu do jednotne podoby (XX.YY)
    word = timeify(word)

    # Jestlize uz jsem neco nacetl a radek neni prazdny (tzn. jsem pr. u 2. poradu)
    # tak je nutne zapsat do souboru aktualni porad, vymazat jej z pameti a zacit znovu
    if current_programme != []: 
        f.write(createStr(current_programme))
        current_programme = []
        current_programme.append(word)

    # Jestlize aktualni radek prazdny je a zaroven jsem nasel cas,
    # znamena to, ze jsem na zacatku souboru a beru jen cas a nic nemazu
    else:
        current_programme.append(word)

    flag = 1
    # Ulozeni hodiny poradu pro kontrolu, jestli uz neni novy den
    hour = int(re.findall(r'[0-9]{1,2}', word.split('.')[0])[0])
    
    return current_programme, flag, hour

## Funkce pro ulozeni posledni nactene hodiny
# 
# @param hour Aktualni nacteny cas, konkretne jeho hodina
# @param previous_last_time Predminula hodnota casu
# @param last_time Minuly cas
# 
# @return previous_last_time Predminula hodnota
# @return last_time Minula hodnota
def getLastTime(hour, previous_last_time, last_time):
    # Jestlize hodina neni 0 a nebo 1 (Kvuli vysilani az do noci)
    # uloz hodnoty
    if (hour not in (0,1)):
        previous_last_time = last_time # z predminula se stane minula
        last_time = hour # soucasna se stane minulou
    return previous_last_time, last_time

## Funkce na kontrolu, jestli nbeylo nalezeno vysilani pro Bratislavu/Kosice
#
# @param f Soubor s porady
# @param sk_flag Aktualni hodnota vlajky urcujici, zda bylo nalezeno SK vysilani
# @param current_programme Seznam obsahujici stringy se soucasnym poradem
# @param word Aktualni prohledavane slovo
# @param text Cely prohledavany text
# @param index Aktualni pozice prohledavani
# @param flag Vlajka urcujici jestli ma dojit k zapisu metadat, vychozi hodnota Ne
#
# @return current_programme Seznam obsahujici aktualni porad (a nebo zadny)
# @return sk_flag Vlajka indikujici pritomnost vysilani pro SK
def checkBratislava(f, sk_flag, current_programme, word, text, index, flag=0):
    if ("RATISLA" in word.upper() and ("KOŠIC" in text[index+1].upper() or "KOSIC" in text[index+1].upper())):
        # Zapsani posledniho nacteneho z ctv
        f.write(createStr(current_programme))
        current_programme = []
        sk_flag = True

        if flag:
            return current_programme, sk_flag

        writeTop(f, "SK", "1")
        # Naznak, ze jsem narazil na vysilani pro Blavu
    return current_programme, sk_flag

## Funkce na zakonceni nacitani poradu pro dany den
#
# @param current_programme Seznam obsahujici stringy se soucasnym poradem
# @param f Soubor s porady
def finishDay(current_programme, f):
    global DAY
    # Jestlize program neni prazdny, zapis zbytek
    if (current_programme != []):
        f.write(createStr(current_programme))
        DAY += 1    # inkrementuj den
        resetDay()
    
    f.close()

## Funkce na inkrementaci dne a zapsani metadat do programu
#
# @param f Soubor s porady
def dayWrite(f):
    global DAY
    DAY += 1
    resetDay()
    writeTop(f, "CZ", "1")

## Funkce na zpracovani programu z let 68-70
#
# @param file Vstupni soubor s programem
# @param year Rok do ktereho vysilani nalezi
def get1968(file, year):
    global DAY
    text, f = getText(file, year)
    writeTop(f, "CZ", "1")
    
    current_programme = []
    index, last_time, previous_last_time = 0, 0, 0
    sk_flag = False
    rozhlas = False

    for word in text:
        flag = 0
        # Je nasledujici prvek v naskenovanem textu cas? 
        # Cas oddeluje jednotlive porady
        if isTime(word):
            
            if not (rozhlas):
                # konverze casu do jednotne podoby (XX.YY)
                word = timeify(word)

                if current_programme != [] and text[index-1] != "v":    # "Uvadime pravidelne v..." Jen zprava v programu
                    f.write(createStr(current_programme))
                    current_programme = []
                    current_programme.append(word)

                else:
                    current_programme.append(word)

                if text[index-1] == "v":
                    index += 1
                    continue
                
                flag = 1
            
            # Ulozeni hodiny poradu pro kontrolu, jestli uz neni novy den
            hour = int(re.findall(r'[0-9]{1,2}', word.split('.')[0])[0])

            # Jestlize jsem nasel mensi datum nez predchozi, jsem uz na dalsim dnu
            if (hour < last_time and last_time >= previous_last_time and hour not in (0,1)):

                # Jestlize neni zapnute SK vlajka (tj. nenarazil jsem jen na Bratislavu)
                # tak je potreba inkrementovat den
                if ((not sk_flag) and (not rozhlas)):
                    dayWrite(f)

                if (rozhlas):
                    rozhlas = False
                sk_flag = False

            previous_last_time, last_time = getLastTime(hour, previous_last_time, last_time)

        # "bratislava, kosice" ve sloupci tedy znaci konec programu ceskeho vysilani pro dany den
        current_programme, sk_flag = checkBratislava(f, sk_flag, current_programme, word, text, index)

        if ("ROZHLAS" in word.upper() and text[index+1].upper() in ("VÝBĚR", "VYBER", "VÝBER")):
            rozhlas = True
            index += 2 
            continue
            
        # Jestlize dane slovo neni ani cas, ani Bratislava, tak to bude popis poradu
        # a ten se prida do aktualniho zpracovavaneho
        if (current_programme != [] and not flag):
            current_programme.append(word)

        # navysuju index, abych ve for loopu vedel, kde jsem a umel se divat i dopredu
        index += 1
    finishDay(current_programme, f)

## Funkce na zpracovani programu z 2. casti roku 1970
#
# @param file Vstupni soubor s programem
# @param year Rok do ktereho vysilani nalezi
def get1970_2(file, year):
    text, f = getText(file, year)
    writeTop(f, "CZ", "1")

    current_programme = []
    index, name_flag, flag = 0,0,0

    for word in text:
        flag = 0

        if name_flag:   # jestlize jsem narazil na identifikator 2. progrmau, preskocim ho
            name_flag = 0
            index += 1
            continue

        # Je nasledujici prvek v naskenovanem textu cas? 
        # Cas oddeluje jednotlive porady
        if isTime(word):
            # konverze casu do jednotne podoby (H.M)
            current_programme, flag, _ = newTime(f, word, current_programme)

        word_up = word.upper()
        # I. / II. Program (Respektive 1. a 2. pozdeji znacene)
        if (("I" in word_up or "2" in word_up or "IL" in word_up or "LI" in word_up or "IE" in word_up or "LL" in word_up or "JI" in word_up) and "PROGR" in text[index+1].upper() and current_programme != []):
            f.write(createStr(current_programme))
            current_programme = []
            writeTop(f, "CZ", "2")
            name_flag = 1   # naznak ze mam preskocit toto slovo

        # "bratislava, kosice" ve sloupci tedy znaci konec programu vysilani pro dany den
        if ("RATISLA" in word_up and (("KOŠICE" in text[index+1].upper() or "KOSICE" in text[index+1].upper()) or ("KOŠICE" in text[index+2].upper() or "KOSICE" in text[index+2].upper()))):
            # Zapsani posledniho nacteneho z ctv
            f.write(createStr(current_programme))
            current_programme = []
            break

        # Jestlize dane slovo neni ani cas, ani Bratislava, tak to bude popis poradu
        # a ten se prida do aktualniho zpracovavaneho
        if (current_programme != [] and not flag and not name_flag):
            current_programme.append(word)

        # navysuju index, abych ve for loopu vedel, kde jsem a umel se divat i dopredu
        index += 1
    finishDay(current_programme, f)

## Funkce na zpracovani programu z let 70-71
#
# @param file Vstupni soubor s programem
# @param year Rok do ktereho vysilani nalezi
def get1970_3(file, year):
    global DAY
    text, f = getText(file, year)
    writeTop(f, "CZ", "1")

    current_programme = []
    index, last_time, previous_last_time = 0, 0, 0
    sk_flag = False
    monoskop = False

    for word in text:
        flag = 0
        # Je nasledujici prvek v naskenovanem textu cas? 
        # Cas oddeluje jednotlive porady
        if isTime(word):
            
            current_programme, flag, hour = newTime(f, word, current_programme)
        
            # Jestlize jsem nasel mensi datum nez predchozi, jsem uz na dalsim dnu
            if (hour < last_time and last_time >= previous_last_time and hour not in (0,1)):

                # Jestlize neni zapnute SK vlajka (tj. nenarazil jsem jen na Bratislavu)
                # tak je potreba inkrementovat den
                if ((not sk_flag) and (not monoskop)):
                    dayWrite(f)

                monoskop = False
                sk_flag = False

            previous_last_time, last_time = getLastTime(hour, previous_last_time, last_time)
        current_programme, sk_flag = checkBratislava(f, sk_flag, current_programme, word, text, index)

        if ("ONOSKOP" in word.upper()):
            monoskop = True
            index += 1
            continue

        if ("DRUH" in word.upper() and "PROGR" in text[index+1].upper()):
            secondProgramme70(f, text[index:])
            f.close()
            return
            
        # Jestlize dane slovo neni ani cas, ani Bratislava, tak to bude popis poradu
        # a ten se prida do aktualniho zpracovavaneho
        if (current_programme != [] and not flag):
            current_programme.append(word)

        # navysuju index, abych ve for loopu vedel, kde jsem a umel se divat i dopredu
        index += 1

    finishDay(current_programme, f)

## Funkce na zpracovani programu z let 72-75
#
# @param file Vstupni soubor s programem
# @param year Rok do ktereho vysilani nalezi
def get1972(file, year):
    global DAY
    text, f = getText(file, year)
    writeTop(f, "CZ", "1")

    current_programme = []
    index, last_time, previous_last_time = 0, 0, 0
    dont_increment_flag = False

    for word in text:
        flag = 0
        # Je nasledujici prvek v naskenovanem textu cas? 
        # Cas oddeluje jednotlive porady
        if isTime(word):

            current_programme, flag, hour = newTime(f, word, current_programme)

            # Jestlize jsem nasel mensi datum nez predchozi, jsem uz na dalsim dnu
            if (hour < last_time and last_time >= previous_last_time and hour not in (0,1)):

                # Jestlize neni zapnute SK vlajka (tj. nenarazil jsem jen na Bratislavu)
                # tak je potreba inkrementovat den
                if (not dont_increment_flag):
                    dayWrite(f)

                dont_increment_flag = False

            previous_last_time, last_time = getLastTime(hour, previous_last_time, last_time)

        upper = word.upper()
        # Potreba rucne upravovat program vysilani bratislavy, automaticky to nema cenu
        # protoze se moc casto rozbiji segmentace
        current_programme, dont_increment_flag = checkBratislava(f, dont_increment_flag, current_programme, word, text, index)
        
        # regex pro vyhledavani 2. dne
        regex = "(PO|UT|ÚT|ST|CT|ČT|PA|PÁ|SO|NE)(1|!|l|\||)*[0-9](1|!|l|\||)*[0-9]*"
        if (re.search(regex, upper) or ("DRUH" in upper and "PROGR" in text[index+1].upper())):
            if current_programme != []:
                f.write(createStr(current_programme))
                current_programme = []
            writeTop(f, "CZ", "2")
            dont_increment_flag = True

        # Jestlize dane slovo neni ani cas, ani Bratislava, tak to bude popis poradu
        # a ten se prida do aktualniho zpracovavaneho
        if (current_programme != [] and not flag):
            current_programme.append(word)

        # navysuju index, abych ve for loopu vedel, kde jsem a umel se divat i dopredu
        index += 1
    finishDay(current_programme, f)

## Funkce na zpracovani programu z let 76-78
#
# @param file Vstupni soubor s programem
# @param year Rok do ktereho vysilani nalezi
def get1976(file, year):
    global DAY
    text, f = getText(file, year)
    writeTop(f, "CZ", "1")

    current_programme = []
    index, last_time, previous_last_time = 0, 0, 0
    index_flag = 0

    for word in text:
        flag = 0
        # Je nasledujici prvek v naskenovanem textu cas? 
        # Cas oddeluje jednotlive porady
        if isTime(word):
            current_programme, flag, hour = newTime(f, word, current_programme)

            # Jestlize jsem nasel mensi datum nez predchozi, jsem uz na dalsim dnu
            if (hour < last_time and last_time >= previous_last_time and hour not in (0,1)):
                # Narazil jsem na novy den - zvysim index, protoze v techto letech
                # je mensi datum ne novy den, ale druhy program - novy den az "kazdy druhy", pokud vse nacte dobre
                index_flag += 1
                if (index_flag % 2 == 0):
                    dayWrite(f)
                else:
                    writeTop(f, "CZ", "2")

            previous_last_time, last_time = getLastTime(hour, previous_last_time, last_time)

        # Jestlize dane slovo neni ani cas, ani Bratislava, tak to bude popis poradu
        # a ten se prida do aktualniho zpracovavaneho
        if (current_programme != [] and not flag):
            current_programme.append(word)

        # navysuju index, abych ve for loopu vedel, kde jsem a umel se divat i dopredu
        index += 1
    finishDay(current_programme, f)

## Funkce na zpracovani programu z let 79-90
#
# @param file Vstupni soubor s programem
# @param year Rok do ktereho vysilani nalezi
def get1979(file, year):
    text, f = getText(file, year)
    writeTop(f, "CZ", "1")

    current_programme = []
    index, last_time, previous_last_time = 0, 0, 0
    bratislava_counter = 0
    dont_increment_flag = 0

    for word in text:
        flag = 0
        # Je nasledujici prvek v naskenovanem textu cas? 
        # Cas oddeluje jednotlive porady
        if isTime(word):
            current_programme, flag, hour = newTime(f, word, current_programme)

            # Jestlize jsem nasel mensi datum nez predchozi, jsem uz na dalsim dnu
            if (hour < last_time and last_time >= previous_last_time and hour not in (0,1)):
                # Narazil jsem na novy den - zvysim index, protoze v techto letech
                if not dont_increment_flag:
                    if int(year) >= 1990:
                        if bratislava_counter == 0:
                            bratislava_counter += 1
                            writeTop(f, "CZ", "2")
                        else:
                            writeTop(f, "SK", "1")
                    else:
                        writeTop(f, "CZ", "2")

                dont_increment_flag = False

            previous_last_time, last_time = getLastTime(hour, previous_last_time, last_time)
        
        upper = word.upper()
        if (("RATISLA" in upper and ("KOŠIC" in text[index+1].upper() or "KOSIC" in text[index+1].upper())) 
            or ("SLOVENS" in upper and ("OKRUH" in text[index+1].upper() or "TELEVI" in text[index+1].upper()))):
            # Zapsani posledniho nacteneho z ctv
            f.write(createStr(current_programme))
            current_programme = []

            bratislava_counter += 1
            writeTop(f, "SK", str(bratislava_counter))
            # Naznak, ze jsem narazil na vysilani pro Blavu
            dont_increment_flag = True

        # Jestlize dane slovo neni ani cas, ani Bratislava, tak to bude popis poradu
        # a ten se prida do aktualniho zpracovavaneho
        if (current_programme != [] and not flag):
            current_programme.append(word)

        # navysuju index, abych ve for loopu vedel, kde jsem a umel se divat i dopredu
        index += 1
    finishDay(current_programme, f)

## Funkce na zpracovani 2. casti programu z let 90-92 (OK3 kanal)
#
# @param file Vstupni soubor s programem
# @param year Rok do ktereho vysilani nalezi
def get1990_2(file, year):
    text, f = getText(file, year)
    writeTop(f, "CZ", "2")

    current_programme = []
    index, last_time, previous_last_time = 0, 0, 0

    for word in text:
        flag = 0
        # Je nasledujici prvek v naskenovanem textu cas? 
        # Cas oddeluje jednotlive porady
        if isTime(word):
            current_programme, flag, hour = newTime(f, word, current_programme)

            # Jestlize jsem nasel mensi datum nez predchozi, jsem uz na dalsim dnu
            if (hour < last_time and last_time >= previous_last_time and hour not in (0,1)):
                # Narazil jsem na novy den - zvysim index, protoze u OK3 jsou dalsi kanaly zahranicni
                # Neodpovidajici smazu rucne
                # Nemuzu breaknout kvuli segmentaci...
                f.write("\nOTHER\n")
            
            previous_last_time, last_time = getLastTime(hour, previous_last_time, last_time)
        
        # Jestlize dane slovo neni ani cas, ani Bratislava, tak to bude popis poradu
        # a ten se prida do aktualniho zpracovavaneho
        if (current_programme != [] and not flag):
            current_programme.append(word)

        # navysuju index, abych ve for loopu vedel, kde jsem a umel se divat i dopredu
        index += 1
    finishDay(current_programme, f)

## Funkce na vypsani napovedy
def printHelp():
    print("Pouziti je: ")
    print("     python ./extractProgram <day> <month> <year> <yearBelongs> [part] <start> <fin>")
    print("                         <day>, <month> a <year> urcuji datum, kterym program zacina")
    print("                         <yearCheck> urcuje rok, z nejz se program vytvori (napr. 30. prosinec je" + '\n' +  "\t\t\t soucasti jeste predchoziho roku, ale patri az do nasledujiciho)")
    print("                         <part> urcuje cast roku")
    print("                         <start> a <fin> urcuji indexy souboru, ktere se maji zpracovat")
    print("Ukazkove volani:")
    print("     python ./extractProgram.py 1 1 1986 1986 0 1")

## Funkce na zpracovani argumentu
#
# @return day Zadany den
# @return month Zadany mesic
# @return year Zadany rok
# @return year_belongs Rok, do ktereho zadany program patri
# @return part Zadana cast roku
def getArgs():
    # Kontrola jestli nebyl volany help
    if "--help" in sys.argv or "-h" in sys.argv:
        printHelp()
        exit(0)

    day = sys.argv[1]
    month = sys.argv[2]
    year = sys.argv[3]
    year_belongs = sys.argv[4]

    part = None
    if (len(sys.argv) == 8): # pri 8 argumentech (mam part) je part 5.
        part = sys.argv[5]

    checkProgrammeExistence(year_belongs)
    # konverze parametru na integery kvuli moznosti inkrementovani
    try:
        year = int(year)
        month = int(month)
        day = int(day)
    except:
        sys.stderr.write("Neplatne datum!\n")
        printHelp()
        exit(1)

    year = int(year)
    month = int(month)
    day = int(day)

    # zpracovavaji se roky jen 66-92
    if (year > 1992 or year < 1966):
        sys.stderr.write("Neplatny rok!\n")
        printHelp()
        exit(1)

    return day, month, year, year_belongs, part

## Hlavni ridici funkce
def main():

    if (len(sys.argv) > 1):
        
        global YEARR
        global DAY
        global MONTH
        DAY, MONTH, YEARR, year_belongs, part = getArgs()

        # Ziskani kontrolniho roku v pripade, ze byl ve formatu 1991_1 (odlisne casti souboru)
        try:
            x = year_belongs.index('_')
            year_check = year_belongs[:x]
            year_check = int(year_check)
        except:
            year_check = int(year_belongs)

        s1,s2 = None,None   # indexy do listu souboru
        try:
            if part != None:
                s1 = int(sys.argv[6])
                s2 = int(sys.argv[7])
            else:
                s1 = int(sys.argv[5])
                s2 = int(sys.argv[6])
        except:
            sys.stderr.write("Neplatne indexy!")
            printHelp()
            exit(1)

        files = getPotentialFiles(year_belongs)[s1:s2]    # ziskani souboru

        # Extrakce poradu
        # Na zaklade roku a casti, kam program patri, zvoli metodu zpracovani
        for file in files:
            print("Zpracovavam ", file)
            if ((year_check <= 1969 and year_check >= 1966) or year_check == 1970 and part == '1'):
                get1968(file, year_belongs)
            elif (year_check == 1970 and part == '2'):
                get1970_2(file, year_belongs)
            elif ((year_check == 1970 and part == '3') or year_check == 1971):
                get1970_3(file, year_belongs)
            elif (year_check in {1972, 1973, 1974, 1975}):
                get1972(file, year_belongs)
            elif (year_check in {1976, 1977, 1978}):
                get1976(file, year_belongs)
            elif (year_check in range(1979,1990)):  # range(end) is omitted!
                get1979(file, year_belongs)
            elif (year_check in range(1990,1993) and (part == '1' or part == '2')): # Prvni strana programu
                get1979(file, year_belongs)
            elif (year_check in range(1990,1993) and part == '3'):  # OK3 - druha strana programu
                get1990_2(file, year_belongs)

        print("Vsechny programy uspesne vytvoreny")
    else:
        sys.stderr.write("Neplatne argumenty!\n")
        printHelp()
        exit(1)

if __name__ == "__main__":
    main()
