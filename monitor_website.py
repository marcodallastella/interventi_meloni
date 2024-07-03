import requests, locale, csv
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from time import sleep

def get_interventi_urls(base_url, main_url):
  response = requests.get(base_url)
  response.raise_for_status()
  soup = BeautifulSoup(response.text, "html.parser")
  article_selector = "box_text_container clearfix"
  articles = soup.find_all('div', class_=article_selector)

  interventi_urls = [
    f"{main_url}{a.get('href')}"
    for article in articles
    for a in article.select("a", href=True) 
    if not a.get('href').startswith('http')
  ]
  return interventi_urls


def read_csv(filename):
  df = pd.read_csv(filename)
  return df["url"].tolist()

def get_date(soup):
  # locale.setlocale(locale.LC_TIME, 'it_IT.UTF-8')
  italian_months = {
      "gennaio": "01",
      "febbraio": "02",
      "marzo": "03",
      "aprile": "04",
      "maggio": "05",
      "giugno": "06",
      "luglio": "07",
      "agosto": "08",
      "settembre": "09",
      "ottobre": "10",
      "novembre": "11",
      "dicembre": "12"
  }

  date = soup.find("p", class_="h6").text
  day_month, year = date_str.split(", ")[1].split()
  # Format the date in YYYY-MM-DD
  formatted_date = f"{year}-{italian_months[day_month.lower()]}-{day_of_month:02}"

  # italian_date = datetime.strptime(date, "%A, %d %B %Y")
  # formatted_date = italian_date.strftime("%Y-%m-%d")
  return formatted_date

def create_data(interventi_urls):
  # Creates a list of dictionaries from the list of URLS.
  data = []

  for url in interventi_urls:
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    title = soup.find("h2").text
    content = soup.find("div", class_="body_intervista").text
    date = get_date(soup)

    data.append({"title": title, "content": content, "date": date, "url": url})
  return data

def append_to_csv(data, filename):
  # Appends the data to a CSV file.
  with open(filename, "a", newline="") as csvfile:
    fieldnames = ["title", "content", "date", "url"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    for row in data:
      writer.writerow(row)

def write_to_csv(data, filename):
  with open(filename, "w", newline="") as csvfile:
    fieldnames = ["title", "content", "date", "url"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for row in data:
      writer.writerow(row)

def main():
  base_url = 'https://www.governo.it/it/interventi'
  main_url = 'https://www.governo.it'
  filename = "./data/interventi_meloni.csv"

  interventi_urls = get_interventi_urls(base_url, main_url)
  existing_urls = read_csv(filename)

  new_urls = [url for url in interventi_urls if url not in existing_urls]

  if new_urls:
    data = create_data(new_urls)
    append_to_csv(data, filename)
  else:
    print("No new URLS found.")

main()