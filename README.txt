README.txt soubor k bakalářské práci Databáze vysílání Československé televize, VUT FIT 2022
Autor: Vojtěch Fiala

*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

Popis obsahu média:
src/ -- zdrojové kódy, extrahované pořady před a po úpravě, databáze, stažené knihovny k UI -- Bootstrap, jQuery, které byly staženy kvůli offline funkcionalitě
doc/ -- zdrojové kódy k písemné zprávě, psané v LaTeXu
tv_examples/ -- Ukázky naskenovaných TV programů z různých let, pouze ilustrační, neboť se jedná o autorsky chráněný materiál
resources/ -- Knihovny a soubory potřebné pro spuštění
xfiala61-databaze-vysilani.pdf -- Písemná zpráva, barevné odkazy
xfiala61-databaze-vysilani-tisk.pdf -- Písemná zpráva, černé odkazy, pro tisk

*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*

;;;;;;;;;;;;;;;;;;;;
;MANUÁL KE SPUŠTĚNÍ;
;;;;;;;;;;;;;;;;;;;;

Podrobným popis jednotlivých souborů se nachází v src/README.txt
Tento manuál se zabývá spouštěním výsledků na OS Windows 10. Kompatibilita jinde není zaručena. Na Linuxu by spouštění mohlo být podobné, ovšem nebude možné využít přiložené .exe soubory a případná instalace Tesseractu je komplikovanější.
Všechny příkazy je vhodné spouštět z Powershellu
Pro spuštění pouze výsledku (webového rozhraní) není Tesseract vůbec potřeba a stačí se řídit následujícími kroky:

********************************
*SPOUŠTĚNÍ POUZE VÝSLEDKU -- UI*
********************************
1)  Pokud není nainstalován Python, je nutné jej nainstalovat ve verzi 3.10, včetně pipu. 
    - Pro to lze využít přiložený .exe soubor (resources/Python)

2)  Instalace pomocných modulů -- ve složce src/requirements-ui.txt jsou vypsány. 
    - Lze je nainstalovat pomocí pipu, skrz     pip install -r src/requirements-ui.txt
    - V případě offline instalace lze využít již stažené moduly, přítomné ve složce resources/Python/Modules
        - Tyto moduly je nutné vložit manuálně do pip složky s moduly -- na Windowsu je výchozí umístění C:\Users\<user>\AppData\Local\Programs\Python\Python310\Lib\site-packages
        - Je nutné vložit soubor pro spouštění Flasku (resources/Python/Scripts/flask.exe) do složky Scripts v Python složce -- výchozí C:\Users\<user>\AppData\Local\Programs\Python\Python310\Scripts

3) Spouštění probíhá příkazem flask run (nutné být ve složce src/ui, může být nutné exportovat hlavní aplikaci app.py jako systémovou proměnnou FLASK_APP příkazem      $env:FLASK_APP = "app")
    - Při manuální instalaci se může vyskytnout problém Fatal error in launcher při spouštění -- v takovém případě jsou 2 možnosti řešení:
        a) Přidat do složky src/ui soubor runFlask.py přítomný ve složce resources/Python/Scripts/ a spustit příkazem   python ./runFlask.py run
        b) Odinstalovat Flask (pip uninstall flask) a Flask znovu nainstalovat (pip install flask), pak lze opět lze spustit jako   flask run

4) Rozhraní je přístupné na loopbacku na výchozím Flask portu 5000, tzn. v prohlížeči na adrese localhost:5000 nebo 127.0.0.1:5000

*****************
*SPOUŠTĚNÍ VŠEHO*
*****************

Co je ke spuštění potřeba:
    Python (nejlépe 3.10, fungovat bude možná i nižší)
    Pip (Většinou nainstalován společně s Pythonem, kvůli dodatečným modulům)
    Tesseract (Pouze pro detekci souborů s programem a extrakci pořadů, pro UI NENÍ nutný)
    *SQLite3 (*V případě, že by mělo dojít k opětovné tvorbě databáze, jinak NENÍ nutný)

Ve složce resources/ jsou přítomny složky obsahující .exe instalační soubory pro Python, SQLite a Tesseract.
V případě instalace Tesseractu je nutné přidat natrénovaná data pro český jazyk (resources/Tesseract/ces.traineddata) do složky, kam se Tesseract nainstaloval -- <složka s tesseractem>/tessdata

Python moduly lze instalovat online či offline:

--- ONLINE
Je nutné nainstalovat pomocné moduly vypsané v souboru requirements.txt ve složce src skrz pip --   pip install -r src/requirements.txt

--- OFFLINE
Je nutné vložit Python moduly ze složky resources/Python/Modules do správné složky -- na Windowsu je výchozí umístění C:\Users\<user>\AppData\Local\Programs\Python\Python310\Lib\site-packages
Je nutné vložit soubor pro spouštění Flasku (resources/Python/Scripts/flask.exe) do složky Scripts v Python složce -- výchozí C:\Users\<user>\AppData\Local\Programs\Python\Python310\Scripts

Pak je již možné spouštět jednotlivé implementované nástroje
Spouštění UI je popsané na začátku souboru, v tutoriálu pro spouštění pouze UI, od kroku 3 dále

*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
