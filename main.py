from disnake.ext.commands import Bot
from disnake.ext import tasks
from disnake import Intents, Embed, Message, File, ui, ButtonStyle, MessageInteraction, Button

import json
from time import sleep
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

from config import *


bot: Bot = Bot(
    command_prefix="+",
    intents=Intents.all(),
    test_guilds=[server_id]
)
bot.remove_command("help")


def read_channel_id(file_path='data.json'):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data.get('message_id')
    except FileNotFoundError:
        pass


def write_channel_id(channel_id, file_path='data.json'):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            data['message_id'] = channel_id
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=2)
    except Exception:
        pass


def get_data() -> dict:
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://tsarvar.com/ru/servers/garrys-mod/194.147.90.50:24299")

    driver.execute_script("arguments[0].scrollIntoView();", driver.find_element(By.CLASS_NAME, "srvPage-art"))
    driver.execute_script("arguments[0].scrollIntoView();", driver.find_element(By.CLASS_NAME, "srvPage-contFoot"))

    sleep(5)

    title = driver.find_element(By.CLASS_NAME, "srvPage-titleName").text
    status = driver.find_element(By.CLASS_NAME, "srvPage-status2 ").text
    ip = driver.find_element(By.CLASS_NAME, "srvPage-addrText").text

    names = []
    if len(driver.find_elements(By.CLASS_NAME, "srvPage-playList")) > 1:
        for div in driver.find_elements(By.CLASS_NAME, "srvPage-playList")[0].find_elements(By.CLASS_NAME, "srvPage-playI "):
            try:
                names.append(div.find_element(By.CLASS_NAME, "srvPage-playIName").find_element(By.TAG_NAME, "a").text + " - " + div.find_element(By.CLASS_NAME, "srvPage-playIScore").text)
            except Exception:
                continue

    result: dict = {
        "ip": ip,
        "title": title,
        "names": names,
        "status": status
    }

    try:
        result["map"] = driver.find_element(By.CLASS_NAME, "srvPage-mapLink").text
        result["cur_count"] = driver.find_element(By.CLASS_NAME, "srvPage-countCur").text
        result["max_count"] = driver.find_element(By.CLASS_NAME, "srvPage-countMax").text
        result["uptime"] = driver.find_element(By.CLASS_NAME, "srvPage-contExt").text
    except Exception:
        pass

    return result


@bot.event
async def on_ready() -> None:
    try:
        message: Message = await bot.get_channel(channel_id).fetch_message(read_channel_id())
        task_loop.start()
    except Exception:
        data = get_data()

        if data["status"] == "ONLINE":
            embed: Embed = Embed(
                title=f"{data['title']}",
                color=0x3bad2f
            )
            embed.add_field(name="Адрес сервера", value=f"`{data['ip']}` ", inline=True)
            embed.add_field(name="** **", value="** **", inline=True)
            embed.add_field(name="Текущая карта", value=data["map"], inline=True)
            embed.add_field(name=f"Список игроков ({data['cur_count']}/{data['max_count']})", value=("\n".join(data['names']) if data['names'] else "Нет игроков"), inline=False)

            try:
                embed.set_thumbnail(file=File(fp=data["map"] + ".jpg"))
            except Exception:
                pass
            embed.set_footer(text=f"Uptime сервера: {data['uptime']} - Обновлено: Сегодня в {datetime.now().strftime('%H:%M')}")

        else:

            embed: Embed = Embed(
                title=data['title'],
                color=0x9c242c
            )
            embed.add_field(name="Статус", value="**Не в сети**", inline=True)
            embed.set_footer(text=f"Uptime сервера: {data['uptime']} - Обновлено: Сегодня в {datetime.now().strftime('%H:%M')}")

        mess = await bot.get_channel(channel_id).send(embed=embed, view=ServerView())

        write_channel_id(mess.id)

        task_loop.start()


@tasks.loop(minutes=delay)
async def task_loop() -> None:
    try:
        message: Message = await bot.get_channel(channel_id).fetch_message(read_channel_id())

        data = get_data()

        if data["status"] == "ONLINE":
            embed: Embed = Embed(
                title=f"{data['title']}",
                color=0x3bad2f
            )
            embed.add_field(name="Адрес сервера", value=f"`{data['ip']}` ", inline=True)
            embed.add_field(name="** **", value="** **", inline=True)
            embed.add_field(name="Текущая карта", value=data["map"], inline=True)
            embed.add_field(name=f"Список игроков ({data['cur_count']}/{data['max_count']})", value=("\n".join(data['names']) if data['names'] else "Нет игроков"), inline=False)
            try:
                embed.set_thumbnail(file=File(fp=data["map"] + ".jpg"))
            except Exception:
                pass
            embed.set_footer(text=f"Uptime сервера: {data['uptime']} - Обновлено: Сегодня в {datetime.now().strftime('%H:%M')}")

        else:
            embed: Embed = Embed(
                title=data['title'],
                color=0x9c242c
            )
            embed.add_field(name="Статус", value="**Не в сети**", inline=True)
            embed.set_footer(text=f"Uptime сервера: {data['uptime']} - Обновлено: Сегодня в {datetime.now().strftime('%H:%M')}")

        await message.edit(embed=embed, view=ServerView())

    except Exception:
        data = get_data()

        if data["status"] == "ONLINE":
            embed: Embed = Embed(
                title=f"{data['title']}",
                color=0x3bad2f
            )
            embed.add_field(name="Адрес сервера", value=f"`{data['ip']}` ", inline=True)
            embed.add_field(name="Текущая карта", value=data["map"], inline=True)
            embed.add_field(name=f"Список игроков ({data['cur_count']}/{data['max_count']})", value=("\n".join(data['names']) if data['names'] else "Нет игроков"), inline=False)
            try:
                embed.set_thumbnail(file=File(fp=data["map"] + ".jpg"))
            except Exception:
                pass
            embed.set_footer(text=f"Uptime сервера: {data['uptime']} - Обновлено: Сегодня в {datetime.now().strftime('%H:%M')}")

        else:

            embed: Embed = Embed(
                title=data['title'],
                color=0x9c242c
            )
            embed.add_field(name="Статус", value="**Не в сети**", inline=True)
            embed.set_footer(text=f"Uptime сервера: {data['uptime']} - Обновлено: Сегодня в {datetime.now().strftime('%H:%M')}")

        mess = await bot.get_channel(channel_id).send(embed=embed, view=ServerView())

        write_channel_id(mess.id)


class ServerView(ui.View):
    def __init__(self):
        super().__init__(
            timeout=None
        )

    @ui.button(
        label="Подключение к серверу",
        url="https://connectsteam.me/?194.147.90.50:24299",
        style=ButtonStyle.grey
    )
    async def join_button(self, button: Button, inter: MessageInteraction) -> None:
        pass

    @ui.button(
        label="Коллекция сервера",
        url="https://steamcommunity.com/sharedfiles/filedetails/?id=2040452510",
        style=ButtonStyle.grey
    )
    async def collect_button(self, button: Button, inter: MessageInteraction) -> None:
        pass


bot.run(bot_token)
