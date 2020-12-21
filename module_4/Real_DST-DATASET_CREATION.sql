/**
В проекте использутся база, скачанная по ссылке https://edu.postgrespro.ru/demo-big.zip
Установка 
В терминале:
psql -f demo-big-20170815.sql
psql
В запущенном psql команды:
ALTER DATABASE demo RENAME TO dst_project;
\q

Запуск этого скрипта создаёт два новых материальных представления - anapa_dataset и other_dataset - готовые для дальнейшего анализа.
 **/
/**
Первым делом создадим представление со всеми зимними рейсами из Анапы второе со всеми рейсами НЕ из Анапы
 **/
CREATE TEMP TABLE anapa_flights AS (
    SELECT
        *
    FROM
        flights
    WHERE
        departure_airport = 'AAQ'
        AND (date_trunc('month', scheduled_departure) IN ('2017-01-01', '2017-02-01', '2017-12-01'))
        AND status NOT IN ('Cancelled')
);

CREATE TEMP TABLE other_winter_flights AS (
    SELECT
        flights.*,
        round(((extract(epoch FROM actual_arrival - actual_departure) / 3600.0)::numeric), 2
) AS flight_duration
    FROM
        flights
    WHERE
        departure_airport != 'AAQ'
        AND (date_trunc('month', scheduled_departure) IN ('2017-01-01', '2017-02-01', '2017-12-01'))
        AND status NOT IN ('Cancelled')
        AND aircraft_code IN ('733', 'SU9')
);


/** 
Создадим новое представление для самолётов, в котором посчитано сколько в самолёте мест какого класса
 **/
CREATE TEMP TABLE aircrafts_seats AS (
    SELECT
        ac.*,
        sts.business_seats,
        sts.economy_seats,
        sts.total_seats
    FROM ( SELECT DISTINCT
        count(seat_no) FILTER (WHERE fare_conditions = 'Business') OVER (PARTITION BY aircraft_code) business_seats, count(seat_no) FILTER (WHERE fare_conditions = 'Economy') OVER (PARTITION BY aircraft_code) economy_seats, count(seat_no) OVER (PARTITION BY aircraft_code) total_seats, aircraft_code
    FROM seats ORDER BY aircraft_code) sts
    LEFT JOIN aircrafts ac ON ac.aircraft_code = sts.aircraft_code
);


/**
посчитаем выручку по рейсам в среднем по Анапе и по стране в 3 зимние месяца для тех же типов самолётов, которые летают из Анапы, а также учтём длительность полёта и отнесём выручку к длительности полёта, запишем в представление
 **/
CREATE TEMP TABLE anapa_flights_revenue AS (
    SELECT
        af.flight_id,
        rev.revenue,
        af.flight_no,
        af.actual_arrival,
        af.arrival_airport,
        af.aircraft_code,
        round((extract(epoch FROM af.actual_arrival - af.actual_departure) / 3600.0)::numeric, 2
) AS flight_duration,
        round((rev.revenue / (extract(epoch FROM af.actual_arrival - af.actual_departure) / 3600.0))::numeric, 2
) AS rph
    FROM (
    SELECT
        flight_id, COALESCE(sum(amount), 0
) AS revenue
    FROM
        anapa_flights a
    LEFT JOIN ticket_flights USING (flight_id)
GROUP BY
    flight_id) rev
    JOIN anapa_flights af USING (flight_id)
    JOIN (
    SELECT
        count(seat_no) seat_count, aircraft_code
    FROM
        seats s
    GROUP BY
        aircraft_code) sc ON af.aircraft_code = sc.aircraft_code
);

CREATE TEMP TABLE other_flights_revenue AS (
    SELECT
        wf.flight_id,
        wf.aircraft_code,
        wf.flight_no,
        wf.actual_arrival,
        wf.departure_airport,
        wf.arrival_airport,
        rev.revenue,
        wf.flight_duration,
        round((rev.revenue / wf.flight_duration), 2
) AS rph
    FROM (
    SELECT
        flight_id, COALESCE(sum(amount), 0
) AS revenue
    FROM
        other_winter_flights o
    LEFT JOIN ticket_flights USING (flight_id)
GROUP BY
    flight_id) rev
    JOIN other_winter_flights wf USING (flight_id)
    JOIN (
    SELECT
        count(seat_no) seat_count, aircraft_code
    FROM
        seats s
    GROUP BY
        aircraft_code) sc ON wf.aircraft_code = sc.aircraft_code
);


/**
Посчитаем общую заполненность рейсов из Анапы и по стране для тех же типов судов, а также разбивку по классам обслуживания (эконом, бизнес).
 **/
CREATE TEMP TABLE anapa_fill AS (
    SELECT
        afs.*,
        ast.total_seats total_capacity,
        ast.economy_seats economy_capacity,
        ast.business_seats business_capacity,
        round(afs.total_tickets / ast.total_seats::numeric, 2) total_fill,
        round(afs.economy_tickets / ast.economy_seats::numeric, 2) economy_fill,
        round(afs.business_tickets / ast.business_seats::numeric, 2) business_fill
    FROM ( SELECT DISTINCT
        af.flight_id, 
        af.aircraft_code, 
        count(ticket_no) OVER (PARTITION BY tf.flight_id, aircraft_code) total_tickets, 
        count(ticket_no) FILTER (WHERE fare_conditions = 'Economy') OVER (PARTITION BY tf.flight_id, aircraft_code) economy_tickets, 
        count(ticket_no) FILTER (WHERE fare_conditions = 'Business') OVER (PARTITION BY tf.flight_id, aircraft_code) business_tickets
    FROM anapa_flights af
    LEFT JOIN ticket_flights tf ON af.flight_id = tf.flight_id) afs
    LEFT JOIN aircrafts_seats ast ON afs.aircraft_code = ast.aircraft_code
);

CREATE TEMP TABLE other_fill AS (
    SELECT
        ofs.flight_id,
        ofs.aircraft_code,
        ofs.total_tickets,
        ofs.economy_tickets,
        ofs.business_tickets,
        ast.total_seats total_capacity,
        ast.economy_seats economy_capacity,
        ast.business_seats business_capacity,
        round(ofs.total_tickets / ast.total_seats::numeric, 2) total_fill,
        round(ofs.economy_tickets / ast.economy_seats::numeric, 2) economy_fill,
        round(ofs.business_tickets / ast.business_seats::numeric, 2) business_fill
    FROM ( SELECT DISTINCT
        of.flight_id, 
        of.aircraft_code, 
        of.scheduled_departure, 
        of.status, 
        count(ticket_no) OVER (PARTITION BY tf.flight_id, aircraft_code) total_tickets, 
        count(ticket_no) FILTER (WHERE fare_conditions = 'Economy') OVER (PARTITION BY tf.flight_id, aircraft_code) economy_tickets, 
        count(ticket_no) FILTER (WHERE fare_conditions = 'Business') OVER (PARTITION BY tf.flight_id, aircraft_code) business_tickets
    FROM other_winter_flights OF
    LEFT JOIN ticket_flights tf ON of.flight_id = tf.flight_id) ofs
    LEFT JOIN aircrafts_seats ast ON ofs.aircraft_code = ast.aircraft_code
WHERE ofs.aircraft_code IN ('733', 'SU9') AND (date_trunc('month', ofs.scheduled_departure) IN ('2017-01-01', '2017-02-01', '2017-12-01')) AND status NOT IN ('Cancelled')
);


/**
Создаём датасеты, сливая всю посчитнанную ранее информацию в две таблицы.
 **/
CREATE TABLE anapa_dataset AS (
    SELECT
        afr.flight_id,
        afr.flight_no,
        afr.actual_arrival,
        afr.arrival_airport,
        afr.aircraft_code,
        afr.revenue,
        afr.flight_duration,
        afr.rph,
        af.total_tickets,
        af.economy_tickets,
        af.business_tickets,
        af.total_capacity,
        af.economy_capacity,
        af.business_capacity,
        af.total_fill,
        af.economy_fill,
        af.business_fill
    FROM
        anapa_flights_revenue afr
        JOIN anapa_fill af USING (flight_id)
);

CREATE TABLE other_dataset AS (
    SELECT
        ofr.flight_id,
        ofr.flight_no,
        ofr.actual_arrival,
        ofr.departure_airport,
        ofr.arrival_airport,
        ofr.aircraft_code,
        ofr.revenue,
        ofr.flight_duration,
        ofr.rph,
        of.total_tickets,
        of.economy_tickets,
        of.business_tickets,
        of.total_capacity,
        of.economy_capacity,
        of.business_capacity,
        of.total_fill,
        of.economy_fill,
        of.business_fill
    FROM
        other_flights_revenue ofr
        JOIN other_fill OF USING (flight_id)
);

ALTER TABLE anapa_dataset
    ADD PRIMARY KEY (flight_id);

ALTER TABLE other_dataset
    ADD PRIMARY KEY (flight_id);

