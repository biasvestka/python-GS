import json
import os

import cx_Oracle
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

# Configurações de conexão Oracle
oracle_username = "RM551534"
oracle_password = "140804"
oracle_host = "oracle.fiap.com.br"
oracle_port = 1521
oracle_service_name = "ORCL"


# Função para inserir informações no banco de dados Oracle
def insert_bike_info_to_oracle(bike_info):
    dsn = cx_Oracle.makedsn(oracle_host, oracle_port, service_name=oracle_service_name)

    try:
        connection = cx_Oracle.connect(oracle_username, oracle_password, dsn)
        if connection:
            print("Conexão Oracle estabelecida com sucesso.")
            cursor = connection.cursor()
            modelo = bike_info["modelo"]
            numero_serie = bike_info["numero_serie"]
            proprietario = bike_info["proprietario"]
            sql = "INSERT INTO BIKE_ADD (modelo, numero_serie, proprietario) VALUES (:modelo, :numero_serie, " \
                  ":proprietario)"
            cursor.execute(sql, modelo=modelo, numero_serie=numero_serie, proprietario=proprietario)
            connection.commit()
            cursor.close()
            connection.close()
            print("Informações da bicicleta inseridas no Oracle com sucesso.")
        else:
            print("Não foi possível estabelecer a conexão com o Oracle.")
        print("Informações da bicicleta inseridas no Oracle com sucesso.")
    except cx_Oracle.Error as error:
        print("Erro ao inserir no Oracle:", error)


# Função para remover bicicletas do banco de dados Oracle
def remove_bike_from_oracle(numero_serie):
    dsn = cx_Oracle.makedsn(oracle_host, oracle_port, service_name=oracle_service_name)

    try:
        connection = cx_Oracle.connect(oracle_username, oracle_password, dsn)
        cursor = connection.cursor()
        check_query = "SELECT COUNT(*) FROM BIKE_ADD WHERE numero_serie = :numero_serie"
        cursor.execute(check_query, numero_serie=numero_serie)
        result = cursor.fetchone()
        if result[0] == 1:
            remove_query = "DELETE FROM BIKE_ADD WHERE numero_serie = :numero_serie"
            cursor.execute(remove_query, numero_serie=numero_serie)
            connection.commit()
            print(f"Bicicleta com número de série {numero_serie} removida do Oracle com sucesso.")
        else:
            print(f"Nenhuma bicicleta encontrada com o número de série {numero_serie}.")
        cursor.close()
        connection.close()
    except cx_Oracle.Error as error:
        print("Erro ao remover do Oracle:", error)


class BikeInfoApp(App):
    def build(self):
        self.layout = BoxLayout(orientation="vertical")

        self.model_input = TextInput(hint_text="Modelo da Bicicleta")
        self.serial_input = TextInput(hint_text="Número de Série")
        self.owner_input = TextInput(hint_text="Proprietário")
        self.bike_serial_input = TextInput(hint_text="Número de Série para Remoção")

        self.submit_button = Button(text="Salvar Informações")
        self.submit_button.bind(on_press=self.save_to_json_and_oracle)

        self.remove_bike_button = Button(text="Remover Bicicleta")
        self.remove_bike_button.bind(on_press=self.remove_bike_from_json_and_oracle)

        self.show_bikes_button = Button(text="Ver Bicicletas")
        self.show_bikes_button.bind(on_press=self.show_bikes)

        self.layout.add_widget(Label(text="Digite as informações da bicicleta:"))
        self.layout.add_widget(self.model_input)
        self.layout.add_widget(self.serial_input)
        self.layout.add_widget(self.owner_input)
        self.layout.add_widget(Label(text="Digite o Número de Série para Remoção:"))
        self.layout.add_widget(self.bike_serial_input)
        self.layout.add_widget(self.submit_button)
        self.layout.add_widget(self.remove_bike_button)
        self.layout.add_widget(self.show_bikes_button)

        return self.layout

    def save_to_json_and_oracle(self, instance):
        bike_info = {
            "modelo": self.model_input.text,
            "numero_serie": self.serial_input.text,
            "proprietario": self.owner_input.text
        }

        # Verificar a existência do arquivo JSON (bikes.json)
        if os.path.exists("bikes.json"):
            with open("bikes.json", "r") as json_file:
                data = json.load(json_file)
        else:
            data = []

        data.append(bike_info)

        with open("bikes.json", "w") as json_file:
            json.dump(data, json_file)

        self.model_input.text = ""
        self.serial_input.text = ""
        self.owner_input.text = ""

        insert_bike_info_to_oracle(bike_info)

        with open("bikes.json", "r") as json_file:
            print(json.load(json_file))

    def show_bikes(self, instance):
        if os.path.exists("bikes.json"):
            with open("bikes.json", "r") as json_file:
                bike_data = json.load(json_file)

            if not bike_data:
                print("Nenhuma bicicleta cadastrada.")
            else:
                for bike in bike_data:
                    print("Modelo:", bike["modelo"])
                    print("Número de Série:", bike["numero_serie"])
                    print("Proprietário:", bike["proprietario"])
                    print("\n")
        else:
            print("Nenhuma bicicleta cadastrada no JSON.")

    def remove_bike_from_json_and_oracle(self, instance):
        bike_serial = self.bike_serial_input.text

        if os.path.exists("bikes.json"):
            with open("bikes.json", "r") as json_file:
                data = json.load(json_file)

            for bike in data:
                if bike["numero_serie"] == bike_serial:
                    data.remove(bike)
                    print(f"Bicicleta com número de série {bike_serial} removida do JSON.")
                    break

            with open("bikes.json", "w") as json_file:
                json.dump(data, json_file)
        else:
            print("Nenhuma bicicleta cadastrada no JSON.")

        remove_bike_from_oracle(bike_serial)


if __name__ == "__main__":
    BikeInfoApp().run()
