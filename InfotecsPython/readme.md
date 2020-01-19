# Описание методов script.py

Все запросы выполнялись с помощью консольной утилиты netcat. Примеры подключения:
```
  nc 127.0.0.1 8000
  nc localhost 8000
```
## Получить город по идентификатору
Необходимо выполнить запрос вида:
```
GET /towns/id?id={номер города} HTTP/1.1
Host: 127.0.0.1
Accept: text/html
```
После выполнения запроса будет возвращен html-код с данными о городе
Пример запроса:
```
  epicycloida@epicycloida-Lenovo-ideapad-330-15IKB:~$ nc localhost 8000
  GET /towns/id?id=451747 HTTP/1.1
  Host: 127.0.0.1
  Accept: text/html

  HTTP/1.1 200 OK
  Content-Type: text/html; charset=utf-8
  Content-Length: 128

  <html><head></head><body>#Zyabrikovo    Zyabrikovo              56.84665        34.7048 P       PPL     RU              77           0204     Europe/Moscow   2011-07-09
  </body></html>
```
## Получить список городов начиная с идентификатора
Необходимо выполнить запрос вида:
```
  GET /towns?id={номер первого города}&n={количество городов}
  Host: 127.0.0.1
  Accept: text/html
```
После выполнения запроса будет возвращен html-код с данными о городах
Пример запроса:
```
  epicycloida@epicycloida-Lenovo-ideapad-330-15IKB:~$ nc localhost 8000
  GET /towns?id=451747&n=4 HTTP/1.1
  Host: 127.0.0.1
  Accept: text/html

  HTTP/1.1 200 OK
  Content-Type: text/html; charset=utf-8
  Content-Length: 453

  <html><head></head><body<div>Города (4)</div><ul><li>#Zyabrikovo        Zyabrikovo              56.84665        34.7048 P       PPL  RU               77                              0               204     Europe/Moscow   2011-07-09
  </li><li>#Znamenka      Znamenka                56.74087        34.02323        P       PPL     RU              77                   0215     Europe/Moscow   2011-07-09
  </li><li>#Zhukovo       Zhukovo         57.26429        34.20956        P       PPL     RU              77                           0237     Europe/Moscow   2011-07-09
  </li><li>#Zhitovo       Zhitovo         57.29693        34.41848        P       PPL     RU              77                           0247     Europe/Moscow   2011-07-09
  </li></ul></body></html>
```
## Получить 2 города: северный и южный, и разницу в времени
Необхордимо выполнить запрос вида:
```
  GET /towns/north?first={имя первого города}&second={имя второго города} HTTP/1.1
  Host: 127.0.0.1
  Accept: text/html
```
Пример запроса:
```
  epicycloida@epicycloida-Lenovo-ideapad-330-15IKB:~$ nc localhost 8000
  GET /towns/north?first=Посёлок+Логи&second=Урочище+Салокачи HTTP/1.1
  Host: 127.0.0.1
  Accept: text/html

  HTTP/1.1 200 OK
  Content-Type: text/html; charset=utf-8
  Content-Length: 481

  <html><head></head><body<div>Есть временная разница</div><ul><li>Север: Posëlok Logi    Poselok Logi    Poselok Logi,Posjolok Logi,Posëlok Logi,Посёлок Логи  59.80535        28.48815        P       PPLX    RU              42                              0            123      Europe/Moscow   2019-12-06
  </li><li>Юг: Urochishche Salokachi      Urochishche Salokachi   Urochishche Salokachi,Urochishhe Salokachi,Урочище Салокачи     49.51421      131.47445       L       AREA    RU              05                              0               412     Asia/Yakutsk    2012-10-08
  </li></ul></body></html>
```
