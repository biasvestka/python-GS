import json
import os
from threading import Thread

import cx_Oracle
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

oracle_username = "RM551534"
oracle_password = "140804"
oracle_host = "oracle.fiap.com.br"
oracle_port = 1521
oracle_service_name = "ORCL"

executar_interface = False


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
            nome_clinica = HelpFila["nome_clinica"]
            sql = "INSERT INTO HELPFILA (nome, email, telefone, cep, idade, nome_clinica) VALUES (:nm_nome, :nm_email, :nm_telefone, :nm_cep, " \
                  ":nr_idade, :nm_nome_clinica)"
            cursor.execute(sql, nm_nome=nome, nm_email=email, nm_telefone=telefone, nm_cep=cep, nr_idade=idade, nm_nome_clinica=nome_clinica)
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


# Função para alterar informações de clientes no banco de dados Oracle
def alterar_cliente_oracle(nome, novo_email, novo_telefone, novo_cep, nova_idade, novo_nome_clinica):
    dsn = cx_Oracle.makedsn(oracle_host, oracle_port, service_name=oracle_service_name)

    try:
        connection = cx_Oracle.connect(oracle_username, oracle_password, dsn)
        cursor = connection.cursor()
        check_query = "SELECT COUNT(*) FROM HELPFILA WHERE nome = :nm_nome"
        cursor.execute(check_query, nm_nome=nome)
        result = cursor.fetchone()
        if result[0] == 1:
            update_query = "UPDATE HELPFILA SET email = :nm_email, telefone = :nm_telefone, cep = :nm_cep, idade = :nr_idade, nome_clinica = :nm_nome_clinica WHERE nome = :nm_nome"
            cursor.execute(update_query, nm_nome=nome, nm_email=novo_email, nm_telefone=novo_telefone, nm_cep=novo_cep, nr_idade=nova_idade, nm_nome_clinica=novo_nome_clinica)
            connection.commit()
            print(f"Informações do cliente {nome} alteradas no Oracle com sucesso.")
        else:
            print(f"Nenhum cliente encontrado com o nome {nome}.")
        cursor.close()
        connection.close()
    except cx_Oracle.Error as error:
        print("Erro ao alterar no Oracle:", error)


class ClienteInfoApp(App):
    def build(self):
        self.layout = BoxLayout(orientation="vertical")

        self.nome_input = TextInput(hint_text="Nome")
        self.email_input = TextInput(hint_text="Email")
        self.tel_input = TextInput(hint_text="Telefone")
        self.cep_input = TextInput(hint_text="CEP")
        self.idade_input = TextInput(hint_text="Idade")
        self.nome_clinica_input = TextInput(hint_text="Nome da Clínica ou Hospital")
        self.cliente_serial_input = TextInput(hint_text="Nome do cliente a ser excluído/alterado")

        self.submit_button = Button(text="Salvar Informações")
        self.submit_button.bind(on_press=self.save_to_json_and_oracle)

        self.remove_cliente_button = Button(text="Remover Cliente")
        self.remove_cliente_button.bind(on_press=self.remove_cliente_from_json_and_oracle)

        self.alterar_cliente_button = Button(text="Alterar Cliente")
        self.alterar_cliente_button.bind(on_press=self.alterar_cliente)

        self.show_clientes_button = Button(text="Ver Clientes")
        self.show_clientes_button.bind(on_press=self.show_clientes)

        self.layout.add_widget(Label(text="Digite as informações do cliente:"))
        self.layout.add_widget(self.nome_input)
        self.layout.add_widget(self.email_input)
        self.layout.add_widget(self.tel_input)
        self.layout.add_widget(self.cep_input)
        self.layout.add_widget(self.idade_input)
        self.layout.add_widget(self.nome_clinica_input)
        self.layout.add_widget(Label(text="Digite o nome do cliente a ser excluído/alterado:"))
        self.layout.add_widget(self.cliente_serial_input)
        self.layout.add_widget(self.submit_button)
        self.layout.add_widget(self.remove_cliente_button)
        self.layout.add_widget(self.alterar_cliente_button)
        self.layout.add_widget(self.show_clientes_button)

        return self.layout

    def save_to_json_and_oracle(self, instance):
        nome = self.nome_input.text
        email = self.email_input.text
        telefone = self.tel_input.text
        cep = self.cep_input.text
        idade = self.idade_input.text
        nome_clinica = self.nome_clinica_input.text

        if not (3 <= len(nome) <= 50 and nome.replace(" ", "").isalpha()):
            print("Erro: O nome deve ter entre 3 e 50 caracteres e conter apenas letras.")
            return

        if not email:
            print("Erro: O campo de email não pode ser vazio.")
            return

        if len(telefone) > 20:
            print("Erro: O telefone deve ter no máximo 20 caracteres.")
            return

        if not cep:
            print("Erro: O campo de CEP não pode ser vazio.")
            return

        try:
            idade = int(idade)
            if not (1 <= idade <= 130):
                raise ValueError
        except ValueError:
            print("Erro: A idade deve ser um número entre 1 e 130.")
            return

        cliente_info = {
            "nome": nome,
            "email": email,
            "telefone": telefone,
            "cep": cep,
            "idade": str(idade),
            "nome_clinica": nome_clinica
        }

        if os.path.exists("clientes.json"):
            with open("clientes.json", "r") as json_file:
                data = json.load(json_file)
        else:
            data = []

        data.append(cliente_info)

        with open("clientes.json", "w") as json_file:
            json.dump(data, json_file)

        insert_info_to_oracle(cliente_info)

        self.nome_input.text = ""
        self.email_input.text = ""
        self.tel_input.text = ""
        self.cep_input.text = ""
        self.idade_input.text = ""
        self.nome_clinica_input.text = ""

        print("Informações do cliente cadastradas com sucesso.")

    def show_clientes(self, instance):
        if os.path.exists("clientes.json"):
            with open("clientes.json", "r") as json_file:
                cliente_data = json.load(json_file)

            if not cliente_data:
                print("Nenhum cliente cadastrado.")
            else:
                for cliente in cliente_data:
                    print("Nome:", cliente.get("nome", "N/A"))
                    print("Email:", cliente.get("email", "N/A"))
                    print("Telefone:", cliente.get("telefone", "N/A"))
                    print("Cep:", cliente.get("cep", "N/A"))
                    print("Idade:", cliente.get("idade", "N/A"))
                    print("Nome da Clínica ou Hospital:", cliente.get("nome_clinica", "N/A"))
                    print("\n")
        else:
            print("Nenhum cliente cadastrado no JSON.")

    def remove_cliente_from_json_and_oracle(self, instance):
        cliente_serial = self.cliente_serial_input.text

        if os.path.exists("clientes.json"):
            with open("clientes.json", "r") as json_file:
                data = json.load(json_file)

            for cliente in data:
                if cliente["nome"] == cliente_serial:
                    data.remove(cliente)
                    print(f"Cliente {cliente_serial} removido do JSON.")
                    break

            with open("clientes.json", "w") as json_file:
                json.dump(data, json_file)
        else:
            print("Nenhum cliente cadastrado no JSON.")

        remove_cliente_from_oracle(cliente_serial)

    def alterar_cliente(self, instance):
        nome_antigo = input("Digite o nome do cliente que deseja alterar: ").strip()

        if os.path.exists("clientes.json"):
            with open("clientes.json", "r") as json_file:
                data = json.load(json_file)

            cliente_encontrado = False

            for cliente in data:
                if cliente["nome"] == nome_antigo:
                    cliente_encontrado = True
                    nome_novo = input("Digite o novo nome: ").strip()

                    if not (3 <= len(nome_novo) <= 50 and nome_novo.replace(" ", "").isalpha()):
                        print("Erro: O novo nome deve ter entre 3 e 50 caracteres e conter apenas letras.")
                        return

                    novo_email = input("Digite o novo email: ").strip()
                    if not novo_email:
                        print("Erro: O campo de email não pode ser vazio.")
                        return

                    novo_telefone = input("Digite o novo telefone: ").strip()
                    if len(novo_telefone) > 20:
                        print("Erro: O telefone deve ter no máximo 20 caracteres.")
                        return

                    try:
                        nova_idade = int(input("Digite a nova idade: "))
                        if not (1 <= nova_idade <= 130):
                            raise ValueError
                    except ValueError:
                        print("Erro: A idade deve ser um número entre 1 e 130.")
                        return

                    novo_cep = input("Digite o novo CEP: ").strip()
                    if not novo_cep:
                        print("Erro: O campo de CEP não pode ser vazio.")
                        return

                    novo_nome_clinica = input("Digite o novo Nome da Clínica ou Hospital: ").strip()

                    cliente["nome"] = nome_novo
                    cliente["email"] = novo_email
                    cliente["telefone"] = novo_telefone
                    cliente["cep"] = novo_cep
                    cliente["idade"] = str(nova_idade)
                    cliente["nome_clinica"] = novo_nome_clinica

                    print(f"Informações do cliente {nome_antigo} atualizadas.")
                    break

            if not cliente_encontrado:
                print(f"Nenhum cliente encontrado com o nome {nome_antigo}.")
        else:
            print("Nenhum cliente cadastrado no JSON.")

        with open("clientes.json", "w") as json_file:
            json.dump(data, json_file)

        try:
            dsn = cx_Oracle.makedsn(oracle_host, oracle_port, service_name=oracle_service_name)
            connection = cx_Oracle.connect(oracle_username, oracle_password, dsn)
            if connection:
                print("Conexão Oracle estabelecida com sucesso.")
                cursor = connection.cursor()

                update_query = """
                    UPDATE HELPFILA 
                    SET nome = :nm_novo_nome,
                        email = :nm_email,
                        telefone = :nm_telefone,
                        cep = :nm_cep,
                        idade = :nr_nova_idade,
                        nome_clinica = :nm_nome_clinica
                    WHERE nome = :nm_antigo_nome
                """

                cursor.execute(update_query,
                               nm_novo_nome=nome_novo,
                               nm_email=novo_email,
                               nm_telefone=novo_telefone,
                               nm_cep=novo_cep,
                               nr_nova_idade=str(nova_idade),
                               nm_nome_clinica=novo_nome_clinica,
                               nm_antigo_nome=nome_antigo)

                connection.commit()
                cursor.close()
                connection.close()
                print(f"Informações do cliente {nome_antigo} atualizadas no Oracle.")
            else:
                print("Não foi possível estabelecer a conexão com o Oracle.")
        except cx_Oracle.Error as error:
            print("Erro ao atualizar no Oracle:", error)

def show_menu():
    print("Menu de Opções:")
    print("1. Inserir Cliente")
    print("2. Consultar Clientes")
    print("3. Excluir Cliente")
    print("4. Alterar Cliente")
    print("5. Sair")

def menu_thread_function():
    global executar_interface

    while True:
        show_menu()
        choice = input("Escolha uma opção (1-5): ")

        if choice == "1" or choice == "2" or choice == "3" or choice == "4" or choice == "5":
            executar_interface = True
            break
        else:
            print("Opção inválida. Por favor, escolha uma opção de 1 a 5.")


if __name__ == "__main__":
    # Inicia a thread do menu
    menu_thread = Thread(target=menu_thread_function)
    menu_thread.start()

    # Aguarda até que o usuário faça uma escolha no menu
    menu_thread.join()

    # Se o usuário escolheu iniciar a interface, executa a aplicação Kivy
    if executar_interface:
        ClienteInfoApp().run()
