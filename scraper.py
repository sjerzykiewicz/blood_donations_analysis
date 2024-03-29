from bs4 import BeautifulSoup
import requests
import csv
import pandas as pd
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time
import re


def scrap_all():
    url = "https://krew.info/zapasy/"
    result = requests.get(url)
    result = result.content.decode("utf-8")
    soup = BeautifulSoup(result, "html.parser")
    date = soup.find(text=re.compile("Aktualizacja stanu:.*"))
    date = re.findall("\d+.\d+\.\d+", date)
    date = date[0].replace(".", "-")
    if date[1] == "-":
        date = "0" + date

    file = pd.read_csv("data/blood_donation_all.csv")

    df = pd.DataFrame(file.iloc[-1:, :].values)
    if not df.empty:
        lastDate = df[4].values[0]

        if lastDate != date:

            blood = {
                "0 Rh+": "",
                "0 Rh-": "",
                "A Rh+": "",
                "A Rh-": "",
                "B Rh+": "",
                "B Rh-": "",
                "AB Rh+": "",
                "AB Rh-": "",
            }

            change = {
                "img/krew3.png": ["Very low", 5],
                "img/krew2.png": ["Medium", 50],
                "img/krew1.png": ["Optimal", 90],
                "img/krew11.png": ["Full", 100],
                "img/krew0.png": ["Full", 100],
            }

            cities = {
                "Białystok": blood.copy(),
                "Bydgoszcz": blood.copy(),
                "Gdańsk": blood.copy(),
                "Kalisz": blood.copy(),
                "Katowice": blood.copy(),
                "Kielce": blood.copy(),
                "Kraków": blood.copy(),
                "Lublin": blood.copy(),
                "Łódź": blood.copy(),
                "Olsztyn": blood.copy(),
                "Opole": blood.copy(),
                "Poznań": blood.copy(),
                "Racibórz": blood.copy(),
                "Radom": blood.copy(),
                "Rzeszów": blood.copy(),
                "Słupsk": blood.copy(),
                "Szczecin": blood.copy(),
                "Wałbrzych": blood.copy(),
                "Warszawa": blood.copy(),
                "Wrocław": blood.copy(),
                "Zielona Góra": blood.copy(),
            }

            for type in blood.keys():
                row = soup.find(text=type).parent.parent.parent
                imgs = row.find_all("img", alt=True)
                for img in imgs:
                    cities[img["alt"]][type] = change[img["src"]]

            with open(
                "data/blood_donation_all.csv", "a", newline="", encoding="utf-8"
            ) as f:
                csv_writer = csv.writer(f)
                for k, v in cities.items():
                    for k1, v1 in v.items():
                        csv_writer.writerow([k, k1, v1[0], v1[1], date])


def scrap_poznan():

    url_poznan = "https://www.rckik.poznan.pl/"
    result = requests.get(url_poznan)
    soup = BeautifulSoup(result.text, "html.parser")

    date = soup.find(text="Stan na ").parent.find("strong").string
    file = pd.read_csv("data/blood_donation_poznan.csv")
    df = pd.DataFrame(file.iloc[-1:, :].values)
    lastDate = df[4].values[0]

    if lastDate != date:
        blood = {
            "0 Rh +": "",
            "0 Rh -": "",
            "A Rh +": "",
            "A Rh -": "",
            "B Rh +": "",
            "B Rh -": "",
            "AB Rh +": "",
            "AB Rh -": "",
        }

        change = {
            "qVL": ["Very low", 5],
            "qL": ["Low", 20],
            "qM": ["Medium", 50],
            "qF": ["Full", 100],
        }

        for type in blood.keys():
            quantity = soup.find(text=type).parent["class"]
            quantity = quantity[0]
            quantity = change[quantity]
            blood[type] = quantity

        with open("data/blood_donation_poznan.csv", "a") as f:
            csv_writer = csv.writer(f)
            for k, v in blood.items():
                k = k.replace("Rh ", "Rh")
                csv_writer.writerow([k, v[0], v[1], "blood", date])


def scrap_warsaw():

    url_warsaw = "https://www.rckik-warszawa.com.pl/"
    options = Options()
    options.add_argument("--headless")
    browser = webdriver.Firefox(options=options)
    browser.get(url_warsaw)
    time.sleep(1)
    result = browser.page_source
    result = "".join(line.strip() for line in result.split("\n"))
    soup = BeautifulSoup(result, "html.parser")

    date = soup.find(text=re.compile("Stan na dzień:.*"))
    date = re.findall("\d+.\d+\.\d+", date)
    date = date[0].replace(".", "-")
    if date[1] == "-":
        date = "0" + date

    file = pd.read_csv("data/blood_donation_warsaw.csv")
    df = pd.DataFrame(file.iloc[-1:, :].values)
    lastDate = df[4].values[0]

    if lastDate != date:
        blood = {
            "0 Rh+": "",
            "0 Rh-": "",
            "A Rh+": "",
            "A Rh-": "",
            "B Rh+": "",
            "B Rh-": "",
            "AB Rh+": "",
            "AB Rh-": "",
        }

        plasma = blood.copy()

        change = {
            "height: 5%;": ["Very low", 5],
            "height: 20%;": ["Low", 20],
            "height: 50%;": ["Medium", 50],
            "height: 100%;": ["Full", 100],
        }

        for type in blood.keys():
            quantity = soup.find_all(text=type)
            quantity[0] = quantity[0].find_previous("svg")["style"]
            quantity[1] = quantity[1].find_previous("svg")["style"]
            quantity[0] = change[quantity[0]]
            quantity[1] = change[quantity[1]]
            blood[type] = quantity[0]
            plasma[type] = quantity[1]

        with open("data/blood_donation_warsaw.csv", "a") as f:
            csv_writer = csv.writer(f)

            for k, v in blood.items():
                csv_writer.writerow([k, v[0], v[1], "blood", date])

            for k, v in plasma.items():
                csv_writer.writerow([k, v[0], v[1], "platelets", date])


if __name__ == "__main__":
    scrap_poznan()
    # scrap_warsaw()
    scrap_all()
