# traffic flow prediction
## Requirements
Windows 10, python 3.10
if you have another OS you need to change repository url for pytorch in pyproject.toml file

## Build instructions
```shell
python -m pip install -r requirements.txt
python -m poetry shell
poetry install
python main.py 
```

## Description of work
My algorithm detects vehicles and counts them for both up and down directions. Also, it predicts cars'speed when they're passing drawn line.

Мой алгоритм считает проезжающие по левой и правой полосам автомобили и фиксирует их скорость в момент пересечения некоторой линии которую я отображаю на видео.

example of work - https://youtu.be/ocjWR-s7lg8


## Stream source
https://www.geocam.ru/en/online/transportnaya-2/

Southern Federal District › Krasnodar Krai › Sochi Municipality › Sochi > Transport Street