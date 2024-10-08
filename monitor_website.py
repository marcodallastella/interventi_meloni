import requests, csv
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
  italian_months = {
      'gennaio': 'January',
      'febbraio': 'February',
      'marzo': 'March',
      'aprile': 'April',
      'maggio': 'May',
      'giugno': 'June',
      'luglio': 'July',
      'agosto': 'August',
      'settembre': 'September',
      'ottobre': 'October',
      'novembre': 'November',
      'dicembre': 'December'
  }

  date = soup.find("p", class_="h6").text
  date = date.split(", ")[1]
  day_str, month_str, year_str = date.split()
  month_str = italian_months.get(month_str.lower(), month_str)
  date_obj = datetime.strptime(f"{day_str} {month_str} {year_str}", "%d %B %Y")
  formatted_date = date_obj.strftime('%Y-%m-%d')
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

def reorder_csv():
  df = pd.read_csv('data/interventi_meloni.csv')
  df = df.sort_values('date', ascending=False)
  df.to_csv('data/interventi_meloni.csv', index=False, encoding='utf-8-sig')

# def write_to_csv(data, filename):
#   with open(filename, "w", newline="") as csvfile:
#     fieldnames = ["title", "content", "date", "url"]
#     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

#     writer.writeheader()
#     for row in data:
#       writer.writerow(row)

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
  
  reorder_csv()

main()