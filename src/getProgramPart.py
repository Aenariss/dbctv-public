## @file getProgramPart
# @author Vojtech Fiala <xfiala61>
#
# Soucast bakalarske prace Databaze Vysilani Ceskoslovenske Televize, 2022
#
# Slouzi k vyhledani, ktere z naskenovanych souboru obsahuji televizni program

import re
import pytesseract
from pytesseract import Output
import sys
from cv2 import imread, imshow, waitKey
from os import listdir
from os.path import isfile, join, exists

## Globalni promenna urcujici nastaveni, v jakem ma byt spousten Tesseract OCR
TESSERACT_CONFIG = r'-l ces --psm 3 --oem 1'

## Funkce na vypsani napovedy a ukonceni programu
def printHelp():
    print("Pouziti je: python3 ./get_program_part.py <year> [part] <folder/with/images>")
    exit(0)

## Funkce na kontrolu, jestli existuje soubor s televiznimi programy pro dany rok
# 
# Jestli neexistuje, je vytvoren
# @param year Rok, z jakeho programy pochazeji
def checkProgrammeExistence(year):
    programme_file_name = "programmes_" + year + ".txt"
    if (exists(programme_file_name)):   # Soubor existuje
        return
    else:   # Soubor neexistuje
        f = open(programme_file_name, 'w')
        f.close()

## Funkce na orezani casti z let 66-67
# 
# @param filename Soubor co ma byt orezan
# @param redundance Vlajka urcujici jaka cast obrazu ma byt orezana, zde jen kvuli kompatibilite
# @return Orezany obraz
def cropPart67(filename, redundance=0):
    img = imread(filename)
    _, width, _ = img.shape
    crop = img[0:int(width/3), 300:1300]
    return crop

## Funkce na orezani casti z let 68-70
# 
# @param filename Soubor co ma byt orezan
# @param redundance Vlajka urcujici jaka cast obrazu ma byt orezana
# @return Orezany obraz
def cropPart68(filename, redundance=0):
    img = imread(filename)
    _, width, _ = img.shape
    crop = None
    if not redundance:
        crop = img[500:1500, 100:int(width/4)+100]
    else:
        crop = img[1000:2000, 1000:1700]
    return crop

## Funkce na orezani casti z 2. casti roku 70
# 
# @param filename Soubor co ma byt orezan
# @param redundance Vlajka urcujici jaka cast obrazu ma byt orezana, zde jen kvuli kompatibilite
# @return Orezany obraz
def cropPart70_2(filename, redundance=0):
    img = imread(filename)
    height, width, _ = img.shape
    crop = img[0:height, 0:int(width/2)]
    return crop

## Funkce na orezani casti z let 70-78
# 
# @param filename Soubor co ma byt orezan
# @param redundance Vlajka urcujici jaka cast obrazu ma byt orezana
# @return Orezany obraz
def cropPart70s(filename, redundance=0):
    img = imread(filename)

    crop = None
    if not redundance:
        crop = img[400:1000, 600:1700]
    else:
        crop = img[1300:2500, 800:1900]
    return crop

## Funkce na orezani casti z let 79-92
# 
# @param filename Soubor co ma byt orezan
# @param redundance Vlajka urcujici jaka cast obrazu ma byt orezana
# @return Orezany obraz
def cropPart90s(filename, redundance=0):
    img = imread(filename)
    height, width, _ = img.shape

    crop = None
    if not redundance:
        crop = img[int(height/2):int(height/2+1500), 0:int(width/2)+200] # cv2 ma height: width
    else:
        crop = img[int(height/2)-400:int(height/2)+900, 500:int(width/2)+700]
    return crop

## Funkce na urceni, jestli je nactene slovo cas
#
# Cas muze byt ve formatech 0.00-24.00 a nebo napr. 13.50-14.30 urcujici blok vysilani
# @param word Slovo, nad kterym bude kontrola provedena
# @return Bool urcujici jestli je slovo cas
def isTime(word):
    regex_string = "^( |-|„|\()?[0-9]+(\.|,) ?[0-9]+:?\
((-|—)[0-9]+(\.|,) ?[0-9]+:?)?\.?$"
    return re.search(regex_string, word)

## Funkce na spocitani, kolikrat se v textu nachazi cas vysilani poradu
# 
# @param text Text, ve kterem ma byt vyskyt casu spocitan
# @return Bool jestli se v textu nachazi alespon 3 casy
def countTimes(text):
    counter = 0
    times_check = 3 # pocet casu, ktere aspon chci najit
    for word in text:
        if isTime(word):
            counter += 1
    return counter >= times_check

## Funkce na ziskani textu z obrazu s vyuzitim OCR Tesseract
# 
# Pred volanim OCR je obraz orezan v zavislosti na zadane funkci
# @param cropFunction Funkce, kterou ma byt obraz orezan
# @param filename Obraz, ktery ma byt orezan
# @param redundance Priznak, jestli ma byt spousteno redundantni orezavani, tzn. orezavani jine casti obrazu
# @return Text ziskany z OCR
def tesseractText(cropFunction, filename, redundance=0):
    file = cropFunction(filename, redundance=redundance)
    text = pytesseract.image_to_data(file, output_type=Output.DICT, config=TESSERACT_CONFIG).get('text')
    return text

## Funkce na ziskani casu v danem roce bez pouziti redundanci
# 
# @param cropFunc Funkce, kterou bude obraz orezan
# @param filename Obraz, ktery ma byt orezan
# @return Bool jestli text obsahuje dostatecny pocet casu
def cropYearNoRedundance(cropFunc, filename):
    text = tesseractText(cropFunc, filename)
    return countTimes(text)

## Funkce na ziskani casu v danem roce s pouzitim redundanci
# 
# @param cropFunc Funkce, kterou bude obraz orezan
# @param filename Obraz, ktery ma byt orezan
# @return Bool jestli text obsahuje dostatecny pocet casu
def cropYearRedundance(cropFunc, filename):
    text = tesseractText(cropFunc, filename)
    if countTimes(text):
        return True
    else:
        # Pokud se nepovedlo nalezt v prvnim hledani, zalozni moznosti je redundance
        text = tesseractText(cropFunc, filename, 1)
        return countTimes(text)

## Funkce na ziskani souboru ze slozky
# 
# @param dir Slozka, ve ktere maji byt soubory hledany
# @return Seznam souboru ve slozce
def getFileNames(dir):
    # https://stackoverflow.com/a/3207973/13279982 -- nacteni souboru ze slozky
    onlyfiles = [f for f in listdir(dir) if isfile(join(dir, f))]
    files = []
    for file in onlyfiles:
        files.append(dir + file)
    return files

## Funkce na pridani souboru do seznamu programu
#
# @param file Nalezeny soubor obsahujici televizni program
# @param year Rok, ve kterem zpracovavani probiha
def addToFile(file, year):
    f = open('programmes_' + str(year) + ".txt", 'a')
    f.write(file + '\n')
    f.close()

## Hlavni ridici funkce
def main():
    # Parametry musi byt aspon 3 - program, rok a slozka se soubory
    if len(sys.argv) > 2:

        # jestli byl zadany help, vypis help
        if "--help" in sys.argv or "-h" in sys.argv:
            printHelp()

        year = sys.argv[1]
        part = 1
        if len(sys.argv) > 3:
            part = sys.argv[2]
            files = getFileNames(sys.argv[3])
        else:
            files = getFileNames(sys.argv[2])
        checkProgrammeExistence(year)
        try:
            # rok a jeho cast musi byt cisla
            year = int(year)
            part = int(part)
        except:
            sys.stderr.write("Neplatny rok!\n")
            exit(1)

        # rok musi byt validni
        if (year > 1993 or year < 1966 or part not in [1,2,3]):
            sys.stderr.write("Neplatny rok nebo jeho cast!\n")
            exit(1)

        counter = 1
        max = len(files)
        for file in files:
            # Cyklus pro zpracovani jendotlivych souboru v danem roku
            print("Zpracovavam ",  str(counter) + "/" + str(max), "--", file)
            counter += 1
            if (year <= 1992 and year >= 1979):
                if cropYearRedundance(cropPart90s, file):
                    addToFile(file, year)

            elif (year <= 1978 and year >= 1971) or (year == 1970 and part == 3):
                if cropYearRedundance(cropPart70s, file):
                    addToFile(file, year)

            elif (year == 1970 and part == 2):
                if cropYearNoRedundance(cropPart70s, file):
                    addToFile(file, year)

            elif (year == 1970 and part == 1) or (year in [1969, 1968]):
                if cropYearRedundance(cropPart68, file):
                    addToFile(file, year)

            elif (year in [1967, 1966]):
                if cropYearNoRedundance(cropPart67, file):
                    addToFile(file, year)
    else:
        sys.stderr.write("Neplatne argumenty!\n")
        printHelp()

if __name__ == "__main__":
    main()
