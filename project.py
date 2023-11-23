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
def insert_info_to_oracle(HelpFila):
    dsn = cx_Oracle.makedsn(oracle_host, oracle_port, service_name=oracle_service_name)

    try:
        connection = cx_Oracle.connect(oracle_username, oracle_password, dsn)
        if connection:
            print("Conexão Oracle estabelecida com sucesso.")
            cursor = connection.cursor()
            nome = HelpFila["nome"]
            email = HelpFila["email"]
            telefone = HelpFila["telefone"]
            cep = HelpFila["cep"]
            idade = HelpFila["idade"]
            sql = "INSERT INTO HELPFILA (nome, email, telefone, cep, idade) VALUES (:nm_nome, :nm_email, :nm_telefone, :nm_cep, " \
                  ":nr_idade)"
            cursor.execute(sql, nm_nome=nome, nm_email=email, nm_telefone=telefone, nm_cep=cep, nr_idade=idade,)
            connection.commit()
            cursor.close()
            connection.close()
            print("Informações do cliente inseridas no Oracle com sucesso.")
        else:
            print("Não foi possível estabelecer a conexão com o Oracle.")
    except cx_Oracle.Error as error:
        print("Erro ao inserir no Oracle:", error)


# Função para remover clientes do banco de dados Oracle
def remove_cliente_from_oracle(nome):
    dsn = cx_Oracle.makedsn(oracle_host, oracle_port, service_name=oracle_service_name)

    try:
        connection = cx_Oracle.connect(oracle_username, oracle_password, dsn)
        cursor = connection.cursor()
        check_query = "SELECT COUNT(*) FROM HELPFILA WHERE nome = :nm_nome"
        cursor.execute(check_query, nm_nome=nome)
        result = cursor.fetchone()
        if result[0] == 1:
            remove_query = "DELETE FROM HELPFILA WHERE nome = :nm_nome"
            cursor.execute(remove_query, nm_nome=nome)
            connection.commit()
            print(f"Cliente {nome} removido do Oracle com sucesso.")
        else:
            print(f"Nenhum cliente encontrado com o nome {nome}.")
        cursor.close()
        connection.close()
    except cx_Oracle.Error as error:
        print("Erro ao remover do Oracle:", error)


class ClienteInfoApp(App):
    def build(self):
        self.layout = BoxLayout(orientation="vertical")

        self.nome_input = TextInput(hint_text="Nome")
        self.email_input = TextInput(hint_text="Email")
        self.tel_input = TextInput(hint_text="Telefone")
        self.cep_input = TextInput(hint_text="CEP")
        self.idade_input = TextInput(hint_text="Idade")
        self.cliente_serial_input = TextInput(hint_text="Nome do cliente a ser excluído")

        self.submit_button = Button(text="Salvar Informações")
        self.submit_button.bind(on_press=self.save_to_json_and_oracle)

        self.remove_cliente_button = Button(text="Remover Cliente")
        self.remove_cliente_button.bind(on_press=self.remove_cliente_from_json_and_oracle)

        self.show_clientes_button = Button(text="Ver Clientes")
        self.show_clientes_button.bind(on_press=self.show_clientes)

        self.layout.add_widget(Label(text="Digite as informações do cliente:"))
        self.layout.add_widget(self.nome_input)
        self.layout.add_widget(self.email_input)
        self.layout.add_widget(self.tel_input)
        self.layout.add_widget(self.cep_input)
        self.layout.add_widget(self.idade_input)
        self.layout.add_widget(Label(text="Digite o nome do cliente a ser excluído:"))
        self.layout.add_widget(self.cliente_serial_input)
        self.layout.add_widget(self.submit_button)
        self.layout.add_widget(self.remove_cliente_button)
        self.layout.add_widget(self.show_clientes_button)

        return self.layout

    def save_to_json_and_oracle(self, instance):
        nome = self.nome_input.text
        email = self.email_input.text
        telefone = self.tel_input.text
        cep = self.cep_input.text
        idade = self.idade_input.text

        # Validação do nome
        if not (3 <= len(nome) <= 50 and nome.isalpha()):
            print("Erro: O nome deve ter entre 3 e 50 caracteres e conter apenas letras.")
            return

        # Validação do email
        if not email:
            print("Erro: O campo de email não pode ser vazio.")
            return

        # Validação do telefone
        if len(telefone) > 20:
            print("Erro: O telefone deve ter no máximo 20 caracteres.")
            return

        # Validação do CEP
        if not cep:
            print("Erro: O campo de CEP não pode ser vazio.")
            return

        # Validação da idade
        try:
            idade = int(idade)
            if not (1 <= idade <= 130):
                raise ValueError
        except ValueError:
            print("Erro: A idade deve ser um número entre 1 e 130.")
            return

        # Se todas as validações passarem, continue com o processamento
        cliente_info = {
            "nome": nome,
            "email": email,
            "telefone": telefone,
            "cep": cep,
            "idade": str(idade)  # Converta idade para string antes de armazenar
        }

        # Salve as informações no arquivo JSON
        if os.path.exists("clientes.json"):
            with open("clientes.json", "r") as json_file:
                data = json.load(json_file)
        else:
            data = []

        data.append(cliente_info)

        with open("clientes.json", "w") as json_file:
            json.dump(data, json_file)

        # Agora chame a função para inserir no Oracle
        insert_info_to_oracle(cliente_info)

        # Limpe os campos de entrada
        self.nome_input.text = ""
        self.email_input.text = ""
        self.tel_input.text = ""
        self.cep_input.text = ""
        self.idade_input.text = ""

        # Exiba uma mensagem de sucesso
        print("Informações do cliente cadastradas com sucesso.")

    def show_clientes(self, instance):
        if os.path.exists("clientes.json"):
            with open("clientes.json", "r") as json_file:
                cliente_data = json.load(json_file)

            if not cliente_data:
                print("Nenhum cliente cadastrado.")
            else:
                for cliente in cliente_data:
                    print("Nome:", cliente["nome"])
                    print("Email:", cliente["email"])
                    print("Telefone:", cliente["telefone"])
                    print("Cep:", cliente["cep"])
                    print("Idade:", cliente["idade"])
                    print("\n")
        else:
            print("Nenhum cliente cadastrado no JSON.")

    def remove_cliente_from_json_and_oracle(self, instance):
        cliente_serial = self.cliente_serial_input.text

        if os.path.exists("clientes.json"):
            with open("clientes.json", "r") as json_file:
                data = json.load(json_file)

            for cliente in data:
                if cliente["nome"] == cliente_serial:  # Correção aqui, trocando 'numero_serie' por 'nome'
                    data.remove(cliente)
                    print(f"Cliente {cliente_serial} removido do JSON.")
                    break

            with open("clientes.json", "w") as json_file:
                json.dump(data, json_file)
        else:
            print("Nenhum cliente cadastrado no JSON.")

        remove_cliente_from_oracle(cliente_serial)


if __name__ == "__main__":
    ClienteInfoApp().run()
