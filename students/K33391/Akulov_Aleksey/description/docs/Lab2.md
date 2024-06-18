# Отчет по лабораторной работе №2

Выполнил: Акулов Алексей, K33391

#### Цель работы:

Понять отличия потоками и процессами и понять, что такое ассинхронность в Python.

Работа о потоках, процессах и асинхронности поможет студентам развить
навыки создания эффективных и быстродействующих программ, что важно для работы с большими объемами данных и выполнения вычислений. Этот опыт также подготавливает студентов к реальным проектам, где требуется использование многопоточности и асинхронности для эффективной обработки данных или взаимодействия с внешними сервисами. 
Вопросы про потоки, процессы и ассинхронность встречаются,
как минимум, на половине собеседований на python-разработчика уровня middle и Выше.

## Задание 1

### Текст задания:

Напишите три различных программы на Python, использующие каждый из подходов:
threading, multiprocessing и async. 

Каждая программа должна решать считать сумму всех чисел от 1 до 1000000. 
Разделите вычисления на несколько параллельных задач для ускорения выполнения.

### Код

#### asyncio

```
async def calculate_sum_async(start, end):
    return sum(range(start, end + 1))


async def main_async(total_numbers=1000000, ts=4):
    part = total_numbers // ts
    threads = []

    for i in range(ts):
        start = i * part + 1
        end = (i + 1) * part if i != ts-1 else total_numbers
        threads.append(calculate_sum_async(start, end))

    results = await asyncio.gather(*threads)
    total_sum = sum(results)
    print(f"Total sum is: {total_sum}")
```


#### treading
```
def calculate_sum(start, end):
    return sum(range(start, end + 1))


def main_threading(total_numbers=1000000, ts=4):
    threads = []
    results = [0] * ts
    part = total_numbers // ts

    def worker(part_id):
        start = part_id * part + 1
        end = (part_id + 1) * part if part_id != (ts - 1) else total_numbers
        results[part_id] = calculate_sum(start, end)

    for i in range(ts):
        thread = threading.Thread(target=worker, args=(i,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    total_sum = sum(results)
    print(f"Total sum is: {total_sum}")
```

#### multiprocessing

```
def calculate_sum(start, end):
    return sum(range(start, end + 1))


def worker(start, end, results):
    partial_sum = calculate_sum(start, end)
    results.put(partial_sum)


def main_multiprocessing(total_numbers=1000000, ts=4):
    results = Queue()
    processes = []
    part = total_numbers // ts

    for i in range(ts):
        start = i * part + 1
        end = (i + 1) * part if i != ts - 1 else total_numbers
        process = Process(target=worker, args=(start, end, results))
        process.start()
        processes.append(process)

    for process in processes:
        process.join()

    total_sum = 0
    while not results.empty():
        total_sum += results.get()

    print(f"Total sum is: {total_sum}")
```


### Результаты

| Тип             | Время выполнения (сек) |
|-----------------|------------------------|
| Threading       | 0.04182000015862286    |
| Multiprocessing | 0.3447751000057906     |
| Asyncio         | 0.0711796001996845     |


## Задание 2

### Текст задания:

Напишите программу на Python для параллельного парсинга нескольких веб-страниц
с сохранением данных в базу данных с использованием подходов
threading, multiprocessing и async. 
Каждая программа должна парсить информацию с нескольких веб-сайтов, 
сохранять их в базу данных.

Был выбран сайт ebay для парсинга товаров и их цены, из него отобралось 3 url, для каждого 
перебиралось по 8 страниц, начиная со второй.

### Код

#### Общий код

```
URLS = ['https://www.ebay.com/sch/i.html?_nkw=phone&_pgn=',
        'https://www.ebay.com/sch/i.html?_nkw=shoes+men&_sop=12&_pgn=',
        'https://www.ebay.com/sch/i.html?_nkw=lego&_pgn=']

PAGES = [2, 3, 4, 5, 6, 7, 8]

BD_CON = "dbname=money_db user=postgres password=sobaka12345 host=localhost"

def pars_item(item):
    title_tag = item.find('div', class_='s-item__title')
    if title_tag:
        title_span = title_tag.find('span', {'role': 'heading'})
        if title_span:
            title_text = title_span.get_text()
        else:
            title_text = "Название не найдено"
    else:
        title_text = "Название не найдено"

    price = item.find('span', class_='s-item__price')
    if price:
        price_text = price.get_text()
    else:
        price_text = "Цена не найдена"

    return {"name": title_text,
            "price": price_text}


def insert_into_db(parsed_items):
    conn = psycopg2.connect(BD_CON)
    cursor = conn.cursor()
    cursor.executemany('''INSERT INTO items (name, price) VALUES (%s, %s)''',
                       [(item['name'], item['price']) for item in parsed_items])
    conn.commit()
    cursor.close()
    conn.close()

def parse_and_save(url):
    for page in PAGES:
        complete_url = f'{url}{page}'
        try:
            response = requests.get(complete_url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса на страницу: {complete_url}\n{e}")
            continue

        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.find_all('li', class_='s-item')

        parsed_items = []
        for item in items:
            item_res = pars_item(item)
            parsed_items.append(item_res)

        insert_into_db(parsed_items)


def create_db():
    conn = psycopg2.connect(BD_CON)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS items (
        id SERIAL PRIMARY KEY,
        name TEXT,
        price TEXT
    )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

create_db()
```

#### asyncio

Тут нужно немного поменять функции

```
async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

async def parse_and_save(session, url):
    for page in PAGES:
        complete_url = f'{url}{page}'
        try:
            text = await fetch(session, complete_url)
        except aiohttp.ClientError as e:
            print(f"Ошибка запроса на страницу: {complete_url}\n{e}")
            continue

        soup = BeautifulSoup(text, 'html.parser')
        items = soup.find_all('li', class_='s-item')

        parsed_items = []
        for item in items:
            item_res = pars_item(item)
            parsed_items.append(item_res)

        insert_into_db(parsed_items)
async def main(urls):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            task = parse_and_save(session, url)
            tasks.append(task)
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    start_time = time.time()
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main(URLS))
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
    end_time = time.time()
    execution_time = end_time - start_time

    print(f"Async time: {execution_time}")
```

#### treading

```
def main(urls):
    threads = []
    for url in urls:
        thread = Thread(target=parse_and_save, args=(url,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    start_time = time.time()
    main(URLS)
    end_time = time.time()
    execution_time = end_time - start_time

    print(f"Threading time: {execution_time}")
```

#### multiprocessing

```
def main(urls):
    num_process = len(urls) if len(urls) < 4 else 4
    pool = Pool(processes=num_process)
    pool.map(parse_and_save, urls)


if __name__ == "__main__":
    start_time = time.time()
    main(URLS)
    end_time = time.time()
    execution_time = end_time - start_time

    print(f"Mutiprocessing time: {execution_time}")
```

### Результаты

| Тип             | Время выполнения (сек)    |
|-----------------|---------------------------|
| Обычный         | 38.970824003219604        |
| Threading       | 17.90959644317627         |
| Multiprocessing | 16.606712579727173        |
| Asyncio         | 15.482174634933472        |