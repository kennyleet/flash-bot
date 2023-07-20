import gspread
import vk_api

from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from config_1 import vk_token, creds

client = gspread.authorize(creds)
sheet = client.open("sheet_flash").sheet1

session = vk_api.VkApi(token=vk_token)
api = session.get_api()


def send_message(vk_user_id, message, **kwargs):
    api.messages.send(
        user_id=vk_user_id,
        message=message,
        random_id=0,
        **kwargs
    )


def keyboard_start(userr_id):
    keyboard = VkKeyboard()
    keyboard.add_button(
        label="Жизни",
        color=VkKeyboardColor.POSITIVE
    )
    keyboard.add_button(
        label="Долги",
        color=VkKeyboardColor.NEGATIVE
    )
    keyboard.add_line()
    keyboard.add_button(
        label="Позвать куратора",
        color=VkKeyboardColor.PRIMARY
    )
    keyboard.add_line()
    keyboard.add_openlink_button(
        label="100points",
        link="https://100points.ru/student/courses"
    )
    keyboard.add_openlink_button(
        label="Stepik",
        link="https://stepik.org/learn/courses"
    )
    send_message(
        userr_id,
        "Панель добавлена!",
        keyboard=keyboard.get_keyboard()
    )


def find_by_id(vk_id):
    return sheet.find("https://vk.com/id" + str(vk_id))


def start():
    while True:
        try:
            for event in VkLongPoll(session).listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:

                    text = event.text.lower()
                    user_id = event.user_id

                    if text == "начать":
                        keyboard_start(user_id)
                    elif text == "жизни":
                        if find_by_id(user_id) is None:
                            send_message(
                                user_id,
                                "Подожди немного..."
                            )

                        else:
                            c = find_by_id(user_id)
                            value = sheet.cell(c.row, c.col + 2).value
                            send_message(
                                user_id,
                                "Твой баланс жизней: " + str(value)
                            )

                    elif text == "долги":
                        if find_by_id(user_id) is None:
                            send_message(
                                user_id,
                                "Подожди немного..."
                            )
                        else:
                            c = find_by_id(user_id)
                            value = sheet.cell(c.row, c.col + 3).value

                            if value is None:
                                send_message(
                                    user_id,
                                    "У тебя нет долгов. Отдыхай =)"
                                )

                            elif ";" in value:
                                value = value.split(";")
                                send_message(
                                    user_id,
                                    f"Твои долги: {value[0]}\nПричина: {value[1]}"
                                )

                            else:
                                send_message(
                                    user_id,
                                    f"Твои долги: {value}"
                                )

                    elif text == "позвать куратора":
                        user = session.method("users.get", {"user_ids": user_id})
                        send_message(
                            321187633,
                            f"{user[0]['first_name']} {user[0]['last_name']} ждет ответа"
                        )
                        send_message(
                            user_id,
                            f"Отправил сообщение Денису. Надеюсь, он скоро его прочитает..."
                        )
        except Exception:
            pass


while True:
    start()
