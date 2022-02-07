/*
The shops Data Exploration (PostgreSQL)

Skills used: Joins, Агрегатные функции, Операции над множествами, Подзапросы, Оконные функции
*/


# запрос для получения информации о продуктах со стоимостью, попадающей в один из диапазонов:
# от 5000 до 15000 и от 30000 до 40000 включая концы отрезков (product_price)

select *
from product_price
where price BETWEEN 5000 and 15000
    or price BETWEEN 30000 and 40000


# Получим информацию о стоимости первых 5 товаров с максимальной ценой, пропустив первые 2 (product_price)

select *
from product_price
order by price DESC
limit 5
offset 2


# Получим информацию о адресах магазинов, в которых заполнены и часы работы, и телефон (store_addres)

select *
from store_address
where opening_hours is not NULL
    and phone is not NULL


# Выведем список сотрудников из таблицы employee:

# row_num - номер строки;
# last_name - фамилия сотрудника;
# first_name - имя сотрудника.
# Сотрудники должны быть отсортированы сначала по фамилии, затем по имени.

select row_number() over(order by last_name, first_name) as row_num,
       last_name, first_name
from employee


# Получим информацию о товарах заказов, которых купили единовременно 5 или более штук:

# purchase_id - идентификатор заказа;
# purchase_date - дата заказа;
# product_id - идентификатор товара;
# count - количество единиц товара заказа;
# price - цена за единицу товара

# Отсортируем результат сначала по количеству единиц товара по убыванию, затем по дате заказа по убыванию

select p.purchase_id,
       p.purchase_date,
       pi.product_id,
       pi.count,
       pi.price
from purchase as p
join purchase_item as pi
    on pi.purchase_id = p.purchase_id
where pi.count >= 5
order by pi.count DESC, p.purchase_date DESC


# Из таблицы заказов получим единственную строку с информацией:

# count_total - общее количество заказов;
# count_employee - количество заказов, которые оформили сотрудники магазина.

select count (*) as count_total,
       count (employee_id) as count_employee
from purchase


# Посчитем статистику по руководителям (employee.manager_id) в магазинах. Выведем следующие данные:

# store_name - название магазина;
# manager_full_name - имя и фамилия руководителя, разделенные пробелом;
# amount_employees - количество человек в подчинении.
# Если в магазине есть сотрудники, у которых нет руководителя (manager_id is null), в результате должна быть строка,
# в которой manager_full_name принимает значение NULL, а amount_employees равно количеству сотрудников без руководителя в магазине.

# Отсортируем результат по названию магазина, затем по manager_full_name.

select s.name as store_name,
       m.first_name || ' ' || m.last_name as manager_full_name,
       count(*) as amount_employees
from employee as e
left join employee as m on m.employee_id = e.manager_id
left join store as s on s.store_id = e.store_id
group by e.store_id,
         s.name,
         e.manager_id,
         m.first_name,
         m.last_name
order by s.name, manager_full_name


# Для каждого товара получим минимальную и максимальную стоимость из таблицы product_price. Выведем столбцы:

# product_id - идентификатор товара;
# price_min - минимальная стоимость товара;
# price_max - максимальная стоимость товара.
# В результате оставить только те товары, для которых минимальная и максимальная стоимость отличается.

# Отсортируем результат по идентификатору товара.

select product_id,
       min(price) as price_min,
       max(price) as price_max
from product_price
group by product_id
having min(price) != max(price)
order by product_id


# Получим информацию о количестве сотрудников из таблицы employee:

# в каждом магазине на каждой должности;
# общее количество сотрудников во всех магазинах

# В результате выведем столбцы:
# store_id - идентификатор магазина;
# rank_id - идентификатор должности;
# count_employees - количество сотрудников.
# Отсортируем результат сначала по идентификатору магазина, затем по идентификатору должности.
# Для обоих полей NULL значения разместить в конце

select e.store_id,
       e.rank_id,
       count (*) AS count_employees
from employee as e
group by GROUPING SETS ((e.store_id, e.rank_id), ())
order by e.store_id NULLS LAST,
         e.rank_id NULLS LAST


# Вывести товары заказа (таблицы purchase_item и purchase), которые проданы по цене из каталога (таблица product_price).

# столбцы:
# product_id - идентификатор товара;
# store_id - идентификатор магазина;
# price - цена.

select pi.product_id,
       p.store_id,
       pi.price
from purchase_item as pi
join purchase as p on p.purchase_id = pi.purchase_id

INTERSECT

select pp.product_id,
       pp.store_id,
       pp.price
from product_price as pp


# Выведем идентификаторы товаров, которые есть в таблице product_price,
# но нет в таблице purchase_item, либо есть в таблице purchase_item, но нет в product_price

# Отсортируем результат по идентификатору товара product_id

(
 select product_id
 from product_price
 EXCEPT
 select product_id
 from purchase_item
)
UNION ALL
(
 select product_id
 from purchase_item
 EXCEPT
 select product_id
 from product_price
)
ORDER BY product_id


# Получим информацию о сотрудниках, которые никем не руководят (идентификатор сотрудника отсутствует в столбце employee.manager_id).
# Выведи следующие столбцы:

# employee_id - идентификатор сотрудника;
# last_name - фамилия;
# first_name - имя;
# rank_id - идентификатор должности.
# Отсортируй результат сначала по фамилии, затем по идентификатору сотрудника

select e.employee_id, e.last_name,
       e.first_name, e.rank_id
from employee as e
where employee_id not in (select em.manager_id
                          from employee as em
                          where em.manager_id IS NOT NULL)
order by e.last_name, e.employee_id






