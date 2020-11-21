from tkinter import messagebox

import paho.mqtt.client as mqtt
import tkinter

terminal_id = "01"
broker = "LAPTOP-TCT8GKUL"
port = 8883

client = mqtt.Client()
window = tkinter.Tk()


def process_message(client, userdata, message):
    message_decoded = (str(message.payload.decode("utf-8")))
    messagebox.showinfo("Message from the Server", message_decoded)


def send_message(card_id):
    client.publish("worker/name", card_id + "." + terminal_id, )


def create_main_window():
    window.geometry("150x100")
    window.title("Sender")

    title = tkinter.Label(window, text="Select employee:")
    title.grid(row=0, columnspan=5)

    button_1 = tkinter.Button(window, text="Employee 1",
                              command=lambda: send_message("1"))
    button_1.grid(row=1, column=0)
    button_2 = tkinter.Button(window, text="Employee 2",
                              command=lambda: send_message("2"))
    button_2.grid(row=2, column=0)
    button_3 = tkinter.Button(window, text="Employee 3",
                              command=lambda: send_message("3"))
    button_3.grid(row=3, column=0)
    button_4 = tkinter.Button(window, text="Employee 4",
                              command=lambda: send_message("4"))
    button_4.grid(row=1, column=1)
    button_5 = tkinter.Button(window, text="Employee 5",
                              command=lambda: send_message("5"))
    button_5.grid(row=2, column=1)
    button_6 = tkinter.Button(window, text="Employee 6",
                              command=lambda: send_message("6"))
    button_6.grid(row=3, column=1)


def connect_to_broker():
    client.tls_set("ca.crt")
    client.username_pw_set(username='client', password='password')
    client.connect(broker, port)
    send_message("Client connected")
    client.on_message = process_message
    client.loop_start()
    client.subscribe("server/name")
    client.subscribe("new/topic")


def disconnect_from_broker():
    send_message("Client disconnected")
    client.disconnect()


def run_sender():
    connect_to_broker()
    create_main_window()
    window.mainloop()
    disconnect_from_broker()


if __name__ == "__main__":
    run_sender()
