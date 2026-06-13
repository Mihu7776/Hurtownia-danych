# Prosta wersja projektu hurtowni danych

To jest druga wersja projektu zrobiona od nowa w osobnym folderze. Poprzedni program nie jest tutaj usuwany ani zmieniany.

## Najprostszy opis

Program pokazuje dane o lekach na stronie internetowej.

Droga danych wyglada tak:

```text
SQL Server -> Java Spring API -> Node -> HTML dashboard
```

SQL Server trzyma dane. Java pyta SQL Server o gotowe wyniki. Node uruchamia strone. HTML pokazuje dane w przegladarce.

Python jest dodatkowym prostym skryptem do pobrania danych openFDA.

## Po co sa te czesci

### SQL Server

SQL Server to baza danych. Baza nazywa sie:

```text
S
```

Backup bazy jest tutaj:

```text
data/S (1).bak
```

W SQL Serverze sa tez widoki dashboardu:

```text
dbo.v_dashboard_summary
dbo.v_sales_by_month
dbo.v_top_drugs
dbo.v_top_manufacturers
dbo.v_city_sales
dbo.v_open_source_summary
```

Widok to gotowe pytanie do bazy zapisane w SQL Serverze. Java nie musi wtedy znac calego trudnego SQL-a. Java pyta tylko widok.

### Java Spring

Java Spring jest backendem API.

Folder:

```text
java-api
```

Backend ma adres:

```text
http://127.0.0.1:8080
```

Przykladowe endpointy:

```text
/api/summary
/api/top-drugs
/api/manufacturers
/api/cities
/api/sources
```

Java odpala `sqlcmd`, pyta SQL Server i oddaje wynik jako JSON.

### Node

Node uruchamia frontend, czyli strone HTML.

Folder:

```text
node-frontend
```

Adres strony:

```text
http://127.0.0.1:3000
```

Node nie liczy danych. Node tylko podaje plik HTML do przegladarki.

### HTML, CSS, JavaScript

To jest widoczna strona dashboardu.

Folder:

```text
node-frontend/public
```

HTML pokazuje ekran. CSS robi wyglad. JavaScript pobiera dane z Javy i wpisuje je na strone.

### Python

Python jest pomocniczy.

Folder:

```text
python-loader
```

Skrypt:

```text
python-loader/load_openfda.py
```

Ten skrypt pobiera publiczne dane openFDA i robi z nich plik SQL.

## Schemat gwiazdy

W bazie jest schemat gwiazdy.

ERD jest tutaj:

```text
docs/ERD.md
```

W srodku jest tabela:

```text
factDrug
```

Ona trzyma liczby, np. ile sprzedano i jaka byla wartosc sprzedazy.

Dookola sa tabele opisowe:

```text
dimCity
dimConTh
dimDrug
dimDrugType
dimMan
dimTime
```

One mowia, czego dotycza liczby: jakie miasto, jaki lek, jaki producent i jaki czas.

## Uruchomienie Windows

Wymagania:

- Java 17
- Maven
- Node.js
- SQL Server LocalDB
- sqlcmd

Pierwsze przygotowanie bazy:

```powershell
.\setup_windows.bat
```

Start programu:

```powershell
.\run_windows.bat
```

Strona:

```text
http://127.0.0.1:3000
```

API:

```text
http://127.0.0.1:8080/api/summary
```

## Uruchomienie Linux EndeavourOS

Wymagania:

- Java 17
- Maven
- Node.js
- Docker
- sqlcmd

Instalacja podstaw:

```bash
sudo pacman -Syu jdk17-openjdk maven nodejs npm docker
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER"
```

Po tej komendzie trzeba wylogowac sie i zalogowac ponownie.

sqlcmd najprosciej doinstalowac z AUR:

```bash
yay -S mssql-tools
```

Pierwsze przygotowanie bazy:

```bash
bash setup_linux.sh
```

Start programu:

```bash
bash run_linux.sh
```

Strona:

```text
http://127.0.0.1:3000
```

## Co powiedziec prowadzacemu

Mozna powiedziec tak:

```text
Projekt trzyma dane w SQL Serverze. W SQL Serverze sa tez gotowe widoki z agregatami.
Backend jest w Javie Spring i wystawia API.
Frontend dziala na Node i pokazuje zwykla strone HTML.
JavaScript na stronie pyta API o dane i rysuje dashboard.
Python jest skryptem pomocniczym do pobierania publicznych danych openFDA.
```

Jeszcze prosciej:

```text
Baza trzyma dane, Java je pobiera, Node odpala strone, HTML je pokazuje.
```
