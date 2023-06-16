from fastapi import FastAPI
from enum import Enum
import requests
import asyncio
from flask import Flask, render_template, request

app=FastAPI()
api_key = "549825c1d81701d2c7f1fbb349db8b54"


app = Flask(__name__)


@app.get("/city_coords/{city}")
def get_coordinates(city: str):
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={api_key}"  # coords
    response = requests.get(url).json()
    coords = (response[0]["lat"], response[0]["lon"])
    lat = coords[0]
    lon = coords[1]
    return {"lat": lat, "lon": lon}


@app.get("/city_data/{city}")
def get_city_data(city: str):
    lat, lon = get_coordinates(city)["lat"], get_coordinates(city)["lon"]
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}"
    response = requests.get(url).json()
    return response

@app.get("/temperatures/{city}/{day_from}/{day_to}")
async def get_temp(city: str, day_from: int, day_to: int):
    data = get_city_data(city)
    # print(data)
    t = []
    for _ in range(len(data["list"])):
        t.append((data["list"][_]["main"]["temp"] - 273.15, data["list"][_]["dt_txt"]))
    # t = list(map(lambda x: round(x - 273.15, 4), t))
    return {"data": t[day_from*8:day_to*8]}
    # return sum(t)/len(t)

@app.get("/average_temp/{city}/{day_from}/{day_to}")
async def get_avg_temp(city: str, day_from: int, day_to: int):
    t = await get_temp(city, day_from, day_to)
    sum = 0
    for i in range(len(t["data"])):
        sum += t["data"][i][0]
    return {"average": round(sum/len(t["data"]), 3)}

@app.get("/max_temp/{city}/{day_from}/{day_to}")
async def get_max_temp(city: str, day_from: int, day_to: int):
    t = await get_temp(city, day_from, day_to)
    max_t = -float("inf")
    id = 0
    for i in range(len(t["data"])):
        if t["data"][i][0] > max_t:
            max_t = t["data"][i][0]
            id = i
    return {"max_temp": round(max_t, 3),
            "at": t["data"][id][1]}

@app.get("/min_temp/{city}/{day_from}/{day_to}")
async def get_min_temp(city: str, day_from: int, day_to: int):
    t = await get_temp(city, day_from, day_to)
    min_t = float("inf")
    id = 0
    for i in range(len(t["data"])):
        if t["data"][i][0] < min_t:
            min_t = t["data"][i][0]
            id = i
    return {"min_temp": round(min_t, 3),
            "at": t["data"][id][1]}



@app.get("/wind/{city}/{day_from}/{day_to}")
async def get_wind(city: str, day_from: int, day_to: int):
    data = get_city_data(city)
    # print(data)
    t = []
    for _ in range(len(data["list"])):
        t.append((data["list"][_]["wind"]["speed"], data["list"][_]["dt_txt"]))
    # t = list(map(lambda x: round(x - 273.15, 4), t))
    return {"data": t[day_from*8:day_to*8]}

@app.get("/max_wind/{city}/{day_from}/{day_to}")
async def get_max_wind(city: str, day_from: int, day_to: int):
    t = await get_wind(city, day_from, day_to)
    max_t = -float("inf")
    id = 0
    for i in range(len(t["data"])):
        if t["data"][i][0] > max_t:
            max_t = t["data"][i][0]
            id = i
    return {"max_wind": round(max_t, 3),
            "at": t["data"][id][1]}


@app.route('/', methods=['GET', 'POST'])
async def submit_form():
    if request.method == 'POST':
        city = request.form['city']
        day_from: int = request.form['day_from']
        day_to: int = request.form['day_to']
        task1 = asyncio.create_task(get_max_wind(city, int(day_from), int(day_to)))
        task2 = asyncio.create_task(get_max_temp(city, int(day_from), int(day_to)))
        task3 = asyncio.create_task(get_min_temp(city, int(day_from), int(day_to)))
        task4 = asyncio.create_task(get_avg_temp(city, int(day_from), int(day_to)))

        avg_temp = await task4
        min_temp = await task3
        max_temp = await task2
        wind = await task1
        print(wind)
        return f'Największa temperatura od {day_from} dni od dzisiaj do {day_to} dni od dzisiaj to: {max_temp["max_temp"]} i jest ona dokładnie: {max_temp["at"]} \n' \
               f'Najmniejsza temperatura to: {min_temp["min_temp"]} i jest ona dokładnie: {min_temp["at"]} \n' \
               f'Średnia arytmetyczna temperatur wynosi: {avg_temp["average"]} \n' \
               f'Największa szybkość wiatru w ciągu tych dni wynosi: {wind["max_wind"]} i jest ona dokładnie: {wind["at"]}'
    else:
        return render_template('form.html')

async def main():
    app.run()
    task = asyncio.create_task(get_max_wind("kraków", 0, 3))
    value = await task
    print( value)

asyncio.run(main())
