from datetime import date

import paho.mqtt.client as mqtt
import tkinter
import sqlite3
import time


terminal_list = []
employee_list = []
terminal_report = []


class Employee:

    def __init__(self, name, surname, card_id):
        self.name = name
        self.surname = surname
        self.card_id = card_id


class Terminal:

    def __init__(self, card_id, terminal_id, time_in, time_out, date):
        self.terminal_id = terminal_id
        self.card_id = card_id
        self.time_in = time_in
        self.time_out = time_out
        self.date = date


def add_employee(name, surname, card_id):
    new_employee = Employee(name, surname, card_id)
    employee_list.append(new_employee)


def find_employee(card_id):
    for i in range(len(employee_list)):
        if str(employee_list[i].card_id) == card_id:
            return employee_list[i].name + " " + employee_list[i].surname
    return ""


def assign_card(name, surname, card_id):
    for i in range(len(employee_list)):
        if employee_list[i].name == name and employee_list[i].surname == surname:
            employee_list[i].card_id = card_id
            print(name + " " + str(card_id))
            break


def remove_card(card_id):
    for i in range(len(employee_list)):
        if employee_list[i].card_id == card_id:
            del employee_list[i].card_id
            break


def card_scanner(card_id, terminal_id):

    result = ""
    # checking if card is in the system
    is_card_in_system = True
    for i in range(len(employee_list)):
        if str(employee_list[i].card_id) == card_id:
            break
        if i == len(employee_list) - 1:
            is_card_in_system = False

    # checking if employee is leaving or entering
    is_inside = False
    index = -1
    for i in range(len(terminal_list)):
        if str(terminal_list[i].card_id) == str(card_id) and terminal_list[i].time_out is None:
            is_inside = True
            index = i

    # entering
    if not is_inside:
        time_in = round(time.time())
        new_entry = Terminal(card_id, terminal_id, time_in, None, date.today())
        terminal_list.append(new_entry)
        if is_card_in_system:
            result = "Employee " + find_employee(card_id) + " walked in"
        else:
            result = "Unknown employee with card " + str(card_id) + " walked in"

    # leaving
    else:
        time_out = round(time.time())
        terminal_list[index].time_out = time_out
        time_at_work = terminal_list[index].time_out - terminal_list[index].time_in
        if is_card_in_system:
            result = "Employee " + find_employee(card_id)
        else:
            result = "Unknown employee with card " + str(card_id)
        result += ": date: " + str(date.today()) + " time at work: " + str(time_at_work) + " used terminal: "\
                  + str(terminal_id)
    return result


def make_report(card_id):
    report = []
    for i in range(len(terminal_list)):
        if terminal_list[i].card_id == card_id:
            report.append(terminal_list[i])

    return report


def print_report(card_id):
    print("Report of days at work for employee " + find_employee(card_id) + ":")
    report = make_report(card_id)
    for i in range(len(report)):
        print(find_employee(card_id) + ": Date: " + str(report[i].date) +
              " Time at work: " + str(report[i].time_out - report[i].time_in))


def print_terminal_list():
    for i in range(len(terminal_list)):
        print(
            str(terminal_list[i].card_id) + " " + str(terminal_list[i].client_id) + " " + str(terminal_list[i].time_in)
            + " " + str(terminal_list[i].time_out) + " " + str(terminal_list[i].date))


def read_file():
    employee_txt = open("employee.txt", "r")
    terminal_txt = open("terminal.txt", "r")

    if employee_txt.mode == 'r':
        for i in employee_txt.readlines():
            split_data = i.split(",")
            new_employee = Employee(split_data[0], split_data[1], int(split_data[2]))
            employee_list.append(new_employee)

    if terminal_txt.mode == 'r':
        for i in terminal_txt.readlines():
            split_data = i.split(",")
            new_entry = Terminal(int(split_data[0]), int(split_data[1]), int(split_data[2]), int(split_data[3]),
                                 split_data[4])
            terminal_list.append(new_entry)
    employee_txt.close()
    terminal_txt.close()


def save_file():
    employee_txt = open("new_employee.txt", "w")
    terminal_txt = open("new_terminal.txt", "w")

    for i in employee_list:
        employee_txt.write(i.name + "," + i.surname + "," + str(i.card_id) + '\n')

    for i in terminal_list:
        terminal_txt.write(str(i.card_id) + "," + str(i.client_id) + "," + str(i.time_in) + "," + str(i.time_out)
                           + "," + str(i.date) + '\n')

    employee_txt.close()
    terminal_txt.close()


def default_employees():
    employee_list.clear()

    add_employee("Harvey", "Keitel", 1)
    add_employee("Tim", "Roth", 2)
    add_employee("Michael", "Madsen", 3)
    add_employee("Chris", "Penn", 4)
    add_employee("Steve", "Buscemi", 5)


broker = "LAPTOP-TCT8GKUL"
port = 8883

client = mqtt.Client()
window = tkinter.Tk()


def process_message(client, user_data, message):
    message_decoded = (str(message.payload.decode("utf-8"))).split(".")
    if message_decoded[0] != "Client connected" and message_decoded[0] != "Client disconnected":
        connection = sqlite3.connect("working_hours.db")
        cursor = connection.cursor()
        new_record = card_scanner(message_decoded[0], message_decoded[1])
        terminal_report.append(new_record)
        cursor.execute("INSERT INTO workers VALUES (?,?,?,?)", (message_decoded[0], message_decoded[1],
                                                                    date.today(), round(time.time())))
        connection.commit()
        connection.close()
    else:
        print(message_decoded[0] + " : " + message_decoded[1])


def print_record_to_window():
    record_labels = []
    print_record_window = tkinter.Tk()

    for record in terminal_report:
        record_labels.append(tkinter.Label(print_record_window, text=record))

    for label in record_labels:
        label.pack(side="top")

    print_record_window.mainloop()


def create_main_window():
    window.geometry("250x50")
    window.title("Receiver")
    label = tkinter.Label(window, text="Working hours")
    print_button = tkinter.Button(window, text="Print report", command=print_record_to_window)
    hello_button = tkinter.Button(window, text="Hello from the server",
                                  command=lambda: client.publish("server/name", "Hello from the server"))
    new_topic_button = tkinter.Button(window, text="New topic", command=lambda: client.publish("new/topic", "New topic"))
    label.pack()
    print_button.pack(side="right")
    hello_button.pack(side="right")
    new_topic_button.pack(side="right")


def connect_to_broker():
    client.tls_set("ca.crt")
    client.username_pw_set(username='client', password='password')
    client.connect(broker, port)
    client.on_message = process_message
    client.loop_start()
    client.subscribe("worker/name")


def disconnect_from_broker():
    client.loop_stop()
    client.disconnect()


def run_receiver():
    default_employees()
    connect_to_broker()
    create_main_window()
    window.mainloop()
    disconnect_from_broker()


if __name__ == "__main__":
    run_receiver()
