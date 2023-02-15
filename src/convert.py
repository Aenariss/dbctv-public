## @file convert
# @author Vojtech Fiala <xfiala61>
#
# Soucast bakalarske prace Databaze Vysilani Ceskoslovenske Televize, 2022
#
# Umoznuje orezavat obrazove soubory podle nastavenych parametru
# Umoznuje prahovat soubory vybranym zpusobem

import cv2
import sys
import os


## Error funkce na zahlaseni chyby a ukonceni programu
def error():
    print("Nespravny pocet parametru ci jejich format; pouziti programu je:")
    print("pro thresholding: python3 ./convert.py [1/2/3/4] <soubory_ke_zpracovani>")
    print("[1/2/3/4] znaci zpusob pouziteho thresholdu - globalni(Threshold)/globalni(Otsuho)/adaptivni(mean)/adaptivni(gauss)")
    print("pro crop: python3 ./convert.py [--crop/-c] x1 x2 y1 y2 <soubory_ke_zpracovani>")
    print("Ukazka konkretniho spusteni: \n\t python3 ./convert.py 1 image.png")
    exit(1)

## Funkce na prahovani obrazu
#
# Vstupni obrazy jsou rovnou prepisovany
# @param file Soubor nebo slozka (obsahujici soubory), co se ma zprahovat
# @param way Vybrany zpusob prahovani
# @param thresh Threshold na globalni prahovani
# Kod na prevody prevzat z:
# https://docs.opencv.org/4.x/d7/d4d/tutorial_py_thresholding.html
def threshold(file, way, thresh=170):
    print(file)
    img = cv2.imread(file, 0)

    blur = cv2.GaussianBlur(img,(3,3),0) # blur kvuli zlepseni vysledku
    if way == '2':
        _, img = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    elif way == '3':
        img = cv2.adaptiveThreshold(blur,255,cv2.ADAPTIVE_THRESH_MEAN_C,\
            cv2.THRESH_BINARY,5,2)

    elif way == '4':
        img = cv2.adaptiveThreshold(blur,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
            cv2.THRESH_BINARY,27,12)

    elif way == '1':
        _, img = cv2.threshold(blur,thresh,255,cv2.THRESH_BINARY)
    else:
        error()
        
    cv2.imwrite(file[:-4]+"_new.png", img)

## Funkce na orezavani obrazu
#
# Vstupni obrazy jsou rovnou prepisovany
# @param file Soubor nebo slozka (obsahujici soubory), co se maji orezat
# @param x1 Prvni souradnice na ose X urcujici kde orezani zacne
# @param x2 Druha souradnice na ose X urcujici kde orezani skonci
# @param y1 Prvni souradnice na ose Y urcujici kde orezani zacne
# @param y2 Druha souradnice na ose Y urcujici kde orezani skonci
def crop(file, x1, x2, y1, y2):
    img = cv2.imread(file, 0)
    img = img[y1:y2, x1:x2]
    cv2.imwrite(file[:-4] + "_new.png", img)

## Funkce na ziskani souboru
#
# Ze zadaneho parametru v pripade, kdy je to slozka
# ziska vsechny soubory v ni
# @param pos Index argumentu, co obsahuje soubor a nebo slozku
# @return Seznam souboru ve slozce
def getFiles(pos):
    files = None
    if os.path.isdir(sys.argv[pos]):

        # https://stackoverflow.com/a/3207973/13279982 -- funkce na nacteni souboru ze slozky
        # jestlize je soubor soubor a ne slozka, pridej ho do seznamu
        files = [f for f in os.listdir(sys.argv[pos]) if os.path.isfile(os.path.join(sys.argv[pos], f))]
        
        new_files = []
        # pridej pred soubory cestu k nim
        for f in files:
            new_files.append(sys.argv[pos] + "\\" + f)
            files = new_files
    else:
        files = sys.argv[pos:]
    return files

## Ridici main funkce
#
# Na zaklade zadanych parametru spousti ostatni funkce
def main():
    # Jestlize byly mene nez 3 argumenty, je to chyba
    if len(sys.argv) < 3:
        error()
    else:
        if len(sys.argv) >= 3 and sys.argv[1] != "--crop" and sys.argv[1] != "-c":  # Threshold ma 3+ parametru
            way = sys.argv[1]

            # jestlize globalni prahovani, zpracuj prah
            if way == "1":
                files = getFiles(3)
                thresh = sys.argv[2]
                try:
                    thresh = int(thresh)
                except:
                    error()
                for file in files:
                    threshold(file, way, thresh=thresh)
            else:
                files = getFiles(2)
                for file in files:
                    threshold(file, way)

        elif (sys.argv[1] == "--crop" or sys.argv[1] == "-c") and len(sys.argv) > 6: # Crop ma parametru vice a klicove slovo
            x1,x2,y1,y2 = None,None,None,None
            try:
                x1 = int(sys.argv[2])
                x2 = int(sys.argv[3])
                y1 = int(sys.argv[4])
                y2 = int(sys.argv[5])
            except:
                error()

            files = getFiles(6)
            for file in files:
                crop(file, x1, x2, y1, y2)
        else:
            error()

if __name__ == "__main__":
    main()
