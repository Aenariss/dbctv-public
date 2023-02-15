Autor: Vojtěch Fiala
Součást bakalářské práce Databáze vysílání Československé televize, VUT FIT 2022

Zde se nachází podrobný popis jednotlivých vytvořených nástrojů a dalších věcí.

series_original/ -- Extrahované pořady po manuální korekci segmentace, rozdělené podle let či částí s odlišným TV programem
series_edited/ -- Složka s extrahovanými pořady po automatické úpravě, její obsah byl nahráván do databáze
ui/ -- Složka s uživatelským rozhraním
    ui/static -- statické soubory jako vlastní CSS styl a česká lokalizace výběru data. Obsahuje stažené knihovny Bootstrap a jQuery, které umožňují UI fungovat offline
    ui/templates -- HTML šablony
    ui/utils -- pomocné Python funkce pro backend
    
requirements.txt -- Seznam požadovaných python modulů
requirements-ui.txt -- Seznam modulů pouze pro UI

Následuje popis jednotlivých souborů, které jsou popsány v takovém pořadí, v jakém byly používány

convert.py -- Nástroj pro prahování a ořezávání obrazů.
getProgramPart.py -- Detekce jaký soubor obsahuje TV program, vytváři textový soubor s výsledky
extractProgram.py -- Extrahování pořadů, očekává složku programmes, která bude obsahovat programy pro jednotlivé roky či jejich části. Výstupem je soubor s pořady
improveSeries.py -- Soubor pro automatickou úpravu výsledků
ui/create.sql -- skript pro tvorbu SQLite databáze, vyžaduje nainstalovaný SQLite, vytvořenou SQLite databázi db.sql a spouští se v SQLite konzoli příkazem .read create.sql
ui/db.sql -- Databáze vysílání pořadů
ui/fillDb.py -- Nahrávání pořadů do databáze, detekce jmen v popisu
ui/app.py -- Hlavní řídící backend aplikace pro webové rozhraní