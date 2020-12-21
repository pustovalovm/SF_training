/**
Проект REAL-DST-SQL, авиарейсы.
Автор - Михаил Пустовалов, поток DSPR-8.TABLE

Проект выполнялся на выгруженной базе demo-big с сайта 
https://postgrespro.ru/docs/postgrespro/10/demodb-bookings-installation
 **/
/**
Подготовительный этап.

Переименовываем базу. По умолчанию скрипт создаёт базу с названием demo 
Перед выполнением запроса надо будет отключиться от этой базы. После выполнения,
возможно, придётся перенастроить соединение.
 **/
ALTER DATABASE demo RENAME TO dst_project;


/**
В созданной базе в таблицах некоторые названия хранятся как на русском, так и на английском языке, в формате jsonb. Пример из таблицы самолётов.
{"en": "Boeing 777-300", "ru": "Боинг 777-300"}.
При этом в представлениях можно выбрать, какой язык будет показываться. Переключим на английский. Надо будет переподключиться, чтобы изменения отразились.
 **/
ALTER DATABASE dst_project SET bookings.lang = en;


/** Задание 4.1. База данных содержит список аэропортов практически всех крупных городов России. В большинстве городов есть только один аэропорт. Исключение составляет:
 **/
SELECT
    city,
    count(airport_code) AS cnt
FROM
    airports
GROUP BY
    city
ORDER BY
    cnt DESC
LIMIT 2;

--Ответ: Moscow, Ulyanovsk
/**
Задание 4.2
Вопрос 1. Таблица рейсов содержит всю информацию о прошлых, текущих и запланированных рейсах. Сколько всего статусов для рейсов определено в таблице?
 **/
SELECT
    count(DISTINCT status)
FROM
    flights;

--Ответ: 6
/**
Вопрос 2. Какое количество самолетов находятся в воздухе на момент среза в базе (статус рейса «самолёт уже вылетел и находится в воздухе»).
 **/
SELECT
    count(DISTINCT flight_id)
FROM
    flights
WHERE
    status = 'Departed';

--Ответ: 58
/**
Вопрос 3. Места определяют схему салона каждой модели. Сколько мест имеет самолет модели 773 (Boeing 777-300)?
 **/
SELECT
    count(DISTINCT seat_no)
FROM
    seats
WHERE
    aircraft_code = '773';

--Ответ: 402
/**
Вопрос 4. Сколько состоявшихся (фактических) рейсов было совершено между 1 апреля 2017 года и 1 сентября 2017 года?
 **/
SELECT
    count(flight_id)
FROM
    flights
WHERE (date(actual_arrival) BETWEEN '2017-04-01'
    AND '2017-09-01')
AND status = 'Arrived';

--Ответ: 74227(в metabase, в локальной базе 74228)
/**
Задание 4.3
Вопрос 1. Сколько всего рейсов было отменено по данным базы?
 **/
SELECT
    count(flight_id)
FROM
    flights
WHERE
    status = 'Cancelled';

--Ответ: 437
/**
Вопрос 2. Сколько самолетов моделей типа Boeing, Sukhoi Superjet, Airbus находится в базе авиаперевозок?
 **/
SELECT
    'Boeing' manufacturer,
    count(aircraft_code)
FROM
    aircrafts
WHERE
    model ~ 'Boeing'
UNION
SELECT
    'Sukhoi Superjet' manufacturer,
    count(aircraft_code)
FROM
    aircrafts
WHERE
    model ~ 'Sukhoi Superjet'
UNION
SELECT
    'Airbus' manufacturer,
    count(aircraft_code)
FROM
    aircrafts
WHERE
    model ~ 'Airbus';

-- Ответ: 3,1,3
/**
Вопрос 3. В какой части (частях) света находится больше аэропортов?
 **/
SELECT
    count(airport_code),
    LEFT (timezone,
        strpos(timezone, '/') - 1) AS loc
FROM
    airports_data
GROUP BY
    loc;

-- Ответ: Europe, Asia
/**
Вопрос 4. У какого рейса была самая большая задержка прибытия за все время сбора данных? Введите id рейса (flight_id).
 **/
SELECT
    flight_id,
    (actual_arrival - scheduled_arrival) AS delay
FROM
    flights
ORDER BY
    delay DESC nulls LAST
LIMIT 1;

-- Ответ: 157571
/**
Задание 4.4
Вопрос 1. Когда был запланирован самый первый вылет, сохраненный в базе данных?
 **/
SELECT
    min(scheduled_departure)
FROM
    flights;

-- Ответ: 2016-08-15 (по местному времени, 2016-08-14 по Гринвичу)
/**
Вопрос 2. Сколько минут составляет запланированное время полета в самом длительном рейсе?
 **/
SELECT
    departure_airport,
    arrival_airport,
    (scheduled_arrival - scheduled_departure) AS delta
FROM
    flights
ORDER BY
    delta DESC
LIMIT 1;

-- Ответ: 530 минут
/**
Вопрос 4. Сколько составляет средняя дальность полета среди всех самолетов в минутах? Секунды округляются в меньшую сторону (отбрасываются до минут).
 **/
SELECT
    avg(actual_arrival - actual_departure)
FROM
    flights;

-- Ответ: 128 минут
/**
Задание 4.5
Вопрос 1. Мест какого класса у SU9 больше всего?
 **/
SELECT
    aircraft_code,
    fare_conditions,
    count(seat_no) seat_count
FROM
    seats
GROUP BY
    fare_conditions,
    aircraft_code
HAVING
    aircraft_code = 'SU9'
ORDER BY
    seat_count DESC
LIMIT 1;

-- Ответ: Economy
/**
Вопрос 2. Какую самую минимальную стоимость составило бронирование за всю историю?
 **/
SELECT
    min(total_amount)
FROM
    bookings;

-- Ответ: 3400
/**
Вопрос 3. Какой номер места был у пассажира с id = 4313 788533? 
 **/
SELECT
    seat_no
FROM
    boarding_passes
WHERE
    ticket_no = (
        SELECT
            ticket_no
        FROM
            tickets
        WHERE
            passenger_id = '4313 788533');

-- Ответ: 2A
/**
Небольшая подготовка - выясним код аэропорта Анапы
 **/
SELECT
    airport_code
FROM
    airports
WHERE
    city = 'Anapa';

-- результат - 'AAQ'

/**
Задание 5.1
Вопрос 1. Анапа — курортный город на юге России. Сколько рейсов прибыло в Анапу за 2017 год?
 **/
SELECT
    count(flight_id)
FROM
    flights
WHERE
    EXTRACT(year FROM actual_arrival) = 2017
    AND arrival_airport = 'AAQ';

-- Ответ: 486
/**
Вопрос 2. Сколько рейсов из Анапы вылетело зимой 2017 года?
 **/
SELECT
    count(flight_id)
FROM
    flights
WHERE
    date(actual_departure) BETWEEN '2017-01-01'
    AND '2017-02-28'
    AND departure_airport = 'AAQ';

-- Ответ: 127
/**
Вопрос 3. Посчитайте количество отмененных рейсов из Анапы за все время. 
 **/
SELECT
    count(flight_id)
FROM
    flights
WHERE
    status = 'Cancelled'
    AND departure_airport = 'AAQ';

-- Ответ: 1
/**
Вопрос 4. Сколько рейсов из Анапы не летают в Москву?
 **/
SELECT
    count(DISTINCT flight_id)
FROM
    flights
WHERE
    departure_airport = 'AAQ'
    AND arrival_airport NOT IN (
        SELECT
            airport_code
        FROM
            airports
        WHERE
            city = 'Moscow');

-- Ответ: 2
/**
Вопрос 5. Какая модель самолета летящего на рейсах из Анапы имеет больше всего мест?
 **/
SELECT
    count(seat_no),
    a.model
FROM
    seats s left JOIN aircrafts a on s.aircraft_code = a.aircraft_code 
WHERE
    s.aircraft_code IN ( SELECT DISTINCT
            aircraft_code
        FROM
            anapa_flights)
GROUP BY
    a.model
-- Ответ: Boeing 737-300
