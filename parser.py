import requests
from bs4 import BeautifulSoup
import json
import csv


url = "https://health-diet.ru/table_calorie/?utm_source=leftMenu&utm_medium=table_calorie"

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
}

rec = requests.get(url, headers=headers)
src = rec.text

with open("page_food.html", "w", encoding="utf-8") as file:
    file.write(src)

with open("page_food.html", "r", encoding="utf-8") as file:
    page = file.read()

soup = BeautifulSoup(page, "lxml")

all_a = soup.find_all("a", {"class": "mzr-tc-group-item-href"})

links_dict = {}
for link in all_a:
    name = link.text
    url = "https://health-diet.ru" + link["href"]
    links_dict[name] = url

with open("links_dict.json", "w", encoding="utf-8") as file:
    json.dump(links_dict, file, indent=4, ensure_ascii=False) # ensure_ascii=False - не экранирует функции
                                                              # indent=4 - задает переносы строк и количество space

with open("links_dict.json", "r", encoding="utf-8") as file:
    links = json.load(file)

iteration_count = int(len(links))
print(f"Всего итераций: {iteration_count}")
count = 0
for category_name, category_link in links.items():
    rep = [", ", " ", "-", "'"]
    for item in rep:
        if item in category_name:
            category_name = category_name.replace(item, "_")

    rec = requests.get(url=category_link, headers=headers)
    src = rec.text

    with open(f"data/{count}_{category_name}.html", "w", encoding="utf-8") as file:
        file.write(src)
        file.close()

    with open(f"data/{count}_{category_name}.html", "r", encoding="utf-8") as file:
        content = file.read()

        soup = BeautifulSoup(content, "lxml")

        # проверка страницы на наличие таблицы с продуктами
        alert_block = soup.find(class_="uk-alert-danger")
        if alert_block is not None:
            continue

        table = soup.find("div", class_="uk-overflow-container")
        table_head = table.find("tr").find_all("th")
        product = table_head[0].text
        calories = table_head[1].text
        proteins = table_head[2].text
        fats = table_head[3].text
        carbonydrates = table_head[4].text

        with open(f"data/{count}_{category_name}.csv", "w", encoding="utf-8-sig", newline="") as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(
                (
                    product,
                    calories,
                    proteins,
                    fats,
                    carbonydrates
                )
            )


            # собираем список продуктов в формате html
            products = table.find("tbody").find_all("tr")

            product_info = []
            # извлекаем имена продуктов
            for item in products:
                product_tds = item.find_all("td")
                title = product_tds[0].find("a").text

                calories = product_tds[1].text
                proteins = product_tds[2].text
                fats = product_tds[3].text
                carbonydrates = product_tds[4].text

                product_info.append(
                    {
                        "Title": title,
                        "Calories": calories,
                        "Proteins": proteins,
                        "Fats": fats,
                        "Carbonydrates": carbonydrates,
                    }
                )

                with open(f"data/{count}_{category_name}.csv", "a", encoding="utf-8-sig", newline="") as file:
                    writer = csv.writer(file, delimiter=';')
                    writer.writerow(
                        (
                            title,
                            calories,
                            proteins,
                            fats,
                            carbonydrates
                        )
                    )
                file.close()

    with open(f"data/{count}_{category_name}.json", "a", encoding="utf-8") as file:
        json.dump(product_info, file, indent=4, ensure_ascii=False)

    count += 1
    print(f"# Итерация {count}. {category_name} записан...")
    iteration_count = iteration_count - 1

    if iteration_count == 0:
        print("Работа завершена")
        break

    print(f"Осталось итераций: {iteration_count}")




