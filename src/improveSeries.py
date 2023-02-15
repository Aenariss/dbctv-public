## @file improveSeries
# @author Vojtech Fiala <xfiala61>
#
# Soucast bakalarske prace Databaze Vysilani Ceskoslovenske Televize, 2022
#
# Slouzi k automaticke uprave vysledku OCR za ucelem zlepseni.

from sys import argv
import re

## Funkce na vypsani chyboveho hlasky/napovedy
#
# ukonci program v zavislosti na miste sveho vzniku
# @param ex Hodnota s jakou program skonci, default 1
def error(ex=1):
    print("Usage is: \n\tpython ./improve_series.py <file>")
    print("Only other usage is \n\tpython ./improve_series.py --help")
    print("This argument prints this text")
    exit(ex)

## Funkce pro ziskani casu vysilani z radku
# 
# @param line Nacteny radek
# @return Regex match
def getTime(line):
    x = re.match("^([0-9]{1,2}).*?\.([0-9]{1,2}).*?", line)
    return x

## Funkce na kontrolu, ze nazev poradu je validni
#
#  Neplatny nazev indikuje, ze nebylo nacteni korektni
#  v takovem pripade ho nema smysl zapisovat
#
# @param name Nazev poradu
# @return Bool hodnota jestli je jmeno validni
def isValidName(name):
    name_length = len(name)
    # Jestlize je nazev kratsi nez 3 znaky, nejspis nebude spravny
    if name_length < 3:
        return False
    # Jestlize je tvoren prevazne mezerama a nebilych znaku neni vic jak 3
    # Taky to asi nebude v poradku
    elif (name_length - name.count(' ')) < 3:
        return False
    else:
        return True

## Funkce na kontrolu, ze je porad validni
#
#  musi mit nazev a nazev musi byt delsi nez 2 znaky
#
# @param line Nacteny radek
# @return Bool hodnota jestli je porad validni
def isValid(line):
    time = getTime(line)    # cas vysilani
    if time == None:        # jestlize neni, je neco spatne
        return False
    
    no_date = line[time.span()[1]+1:]  # "10.40 TEXT" -> cas + mezeru musim odecist
    name = re.search("NAZEVPORADU", no_date)
    if name == None: # kontrola, ze porad ma nazev
        return False
    elif name.span()[0] == 0:   # jestlize je NAZEVPORADU hned na zacatku, je nazev kratky 0 znaku (byly to jen mezery)
        return False
    name = no_date[:name.span()[0]-1]   # zbav se mezery u "porad NAZEVPORADU popis"
    if not isValidName(name):
        return False
    return True

## Funkce pro zkrasleni popisu poradu
#
# @param line Nacteny radek
# @param switch Vlajka urcujici jestli se edituje popis nebo nazev, default nazev
# @return line Upraveny radek
def beautify(line, switch=0):
    if line == None or len(line) == 0:
        return ''

    # Kdyz narazim na vic nez 3 mezery, mazu cely zbytek popisu
    if switch == 1:
        breakpoint = re.search('   .+', line)
        if breakpoint != None:
            line = line[:breakpoint.span()[0]]

    line = re.sub(" +", ' ', line)  # nahrad vsechny vicenasobne mezery jen jednou

    # jsem v descriptionu a musim odmazat pripadne prestavky
    if switch == 1:
        res = re.search("(Přestávka|Prestavka|Prestávka)", line)
        if (res):
            line = line[:res.span()[0]]
            if line == '':
                return line

    if line != '':
        if line[-1] == '':  # Smaz pripadny prazdny znak z konce radku
            line = line[:-1]

    #line = correct(line) # Pousteni autocorrectu, pozustatek protoze nefunguje... zabiji to jmena a obcas to zkratka ani opravit nejde
    return line

## Funkce na unifikaci formatu casu
#
# podle switche resi bud hodiny nebo minuty
#
# @param time Ziskany cas
# @param switch Vlajka urcujici jestli upravuju hodiny nebo minuty
# @return Upraveny cas
def improveTime(time, switch):
    # Pokud ma cas jen 1 znak - pr. 9 - vytvorim 09
    if len(time) == 1 and switch == 1:
        time = "0" + time
    # pokud ma cas jen 1 znak, ale jsou to minuty (5) -> vytvorim 50
    elif len(time) == 1 and switch == 2:
        time = time + "0"
    # pokud je znaku vic nez 2, chci jen prvni 2 (napr. 100 -- chyba)
    elif len(time) > 2:
        time = time[:2]
    return time

## Funkce pro editaci radku
#
# Slouzi ke spoustenei individualnich podfunkci zajistujicich zkrasleni radku
# 
# @param line Nacteny radek
# @return Upraveny radek
def edit(line):
    time = getTime(line)
    hour = improveTime(time.group(1), 1)
    minutes = improveTime(time.group(2), 2)

    line = line[time.span()[1]+1:] # radek bez casu
    name = line[:re.search("NAZEVPORADU", line).span()[0]-1] # nazev poradu
    desc = line[re.search("NAZEVPORADU", line).span()[1]+1:] # popis poradu

    if name != None:
        name = beautify(name)           # zhezci nazev
    if desc != None:
        desc = beautify(desc, switch=1) # zhezci popis

    time = hour + '.' + minutes # Vytvor znovu cas
    line = time + " " + name + " NAZEVPORADU " + desc   # znovu spoj informace do celeho radku
    return line

## Funkce na nacteni souboru a smazani nevalidnich programu
#
# Taky upravi existujici programy do hezciho formatu
# Nevalidni porady jsou odstraneny
# 
# @oaran file Soubor s extrahovanymi porady
def improve(file):
    f = open(file, "r", encoding='utf-8')
    f_new = open(file[:-4] + "_improved.txt", "w", encoding='utf-8') # vytvor novy soubor do nejz budou upravene porady ulozeny
    new_lines = []

    lines = f.readlines()
    line_counter = 1
    all = len(lines)
    for line in lines:
        print("Working on line " +  str(line_counter) + '/' + str(all))
        # Kontrola jestli radek neobsahuje metadata, pak je automaticky validni
        if re.search("^(CZ|SK|[0-9]{1,2}\. ?[0-9]{1,2}\. ?[0-9]{1,4}|\s+$|[1-3]\s+?.*?$)", line):
            new_lines.append(line)
        # Kontrola, jestli je radek validni porad (ma nazev)
        elif isValid(line):
            # Jestlize je validni, oprav chyby (zbytecne mezery, autocorrect, casy, prestavky...)
            line = edit(line)
            new_lines.append(line)
        line_counter += 1
    f.close()
    for line in new_lines:
        if line[-1] != '\n':
            line += "\n"
        f_new.write(line)

## Ridici funkce
def main():
    if len(argv) == 2:  # povoleny je jen 1 argument - help a nebo soubor s programem
        if argv[1] != "--help":
            improve(argv[1])
        else:
            error(ex=0)
    else:
        error()

if __name__ == "__main__":
    main()
