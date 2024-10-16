import pandas as pd
import pywhatkit as kit
import pyautogui
import time
import streamlit as st
from pathlib import Path

# Mover a primeira coluna para o sidebar
with st.sidebar:
    # Selecionar o arquivo CSV com os contatos
    st.title("Selecione o arquivo CSV de contatos")
    contatos_path = st.file_uploader("Escolha um arquivo CSV", type=["csv"])

    if contatos_path is not None:
        # Carregar a lista de contatos do CSV formatado
        contatos_df = pd.read_csv(contatos_path)

        # Garantir que a coluna "Enviados" exista, caso contrário, criar a coluna vazia e definir como string
        if 'Enviados' not in contatos_df.columns:
            contatos_df['Enviados'] = ''

        # Garantir que a coluna "Enviados" seja do tipo string para evitar problemas de compatibilidade
        contatos_df['Enviados'] = contatos_df['Enviados'].astype(str)

        # Extrair apenas o primeiro nome de cada pessoa na coluna 'Nome'
        contatos_df['Primeiro Nome'] = contatos_df['Nome'].str.split().str[0]
        contatos_df['Primeiro Nome'] = contatos_df['Primeiro Nome'].str.capitalize()
        contatos_df['Primeiro Nome'] = contatos_df['Primeiro Nome'].str.replace(r'[\d\-.+]', '', regex=True)

        # Filtrar apenas os contatos que ainda não receberam mensagens (sem "X" na coluna "Enviados")
        contatos_df_nao_enviados = contatos_df[contatos_df['Enviados'] != 'X']

        # Verificar se há contatos para mostrar
        if contatos_df_nao_enviados.empty:
            st.write("Todos os contatos já receberam mensagens.")
        else:
            # Exibir uma tabela com os contatos e permitir seleção
            st.title("Envio de Mensagens pelo WhatsApp")
            st.write("Selecione os contatos para os quais deseja enviar a mensagem:")

            # Adicionar um checkbox para selecionar todos os contatos
            select_all = st.checkbox(f'Selecionar todos os contatos ({len(contatos_df_nao_enviados)})')

            # Adicionar uma multiselect para selecionar contatos individualmente
            if select_all:
                selected_contacts = contatos_df_nao_enviados['Primeiro Nome'].tolist()
            else:
                selected_contacts = st.multiselect(
                    'Selecione os contatos:',
                    contatos_df_nao_enviados['Primeiro Nome'],
                    default=None
                )

            # Campo para escrever a mensagem complementar
            if 'mensagem_complementar' not in st.session_state:
                st.session_state.mensagem_complementar = ""

            mensagem_complementar = st.text_area(
                "Escreva o restante da mensagem",
                value=st.session_state.mensagem_complementar,
                key="mensagem_complementar"
            )

# Layout centralizado para revisão da mensagem
st.markdown("<div style='text-align: center;'><h2>Revisão da Mensagem</h2></div>", unsafe_allow_html=True)

if contatos_path is not None and selected_contacts:
    mensagem_fixa = "Olá {nome}, tudo bem?"
    mensagem_final = f"{mensagem_fixa.format(nome=selected_contacts[0])}\n\n{mensagem_complementar}"
    st.write("Mensagem final a ser enviada:")
    st.write(mensagem_final, unsafe_allow_html=True)

# Exibir os contatos selecionados e botão para enviar
if contatos_path is not None and selected_contacts:
    # Botão para enviar a mensagem
    if st.button("Enviar Mensagem"):
        for index, row in contatos_df_nao_enviados.iterrows():
            if row['Primeiro Nome'] in selected_contacts:
                numero = '+55' + str(row['Telefone'])

                # Enviar a mensagem via WhatsApp
                kit.sendwhatmsg_instantly(numero, mensagem_final)

                # Aguardar alguns segundos para garantir que a mensagem foi digitada
                time.sleep(5)

                # Simular um clique na posição onde o botão de enviar está
                pyautogui.click(x=1000, y=700)  # Ajuste as coordenadas conforme necessário

                # Pressionar "Enter" para enviar a mensagem automaticamente
                pyautogui.press('enter')

                # Aguardar alguns segundos entre as mensagens para evitar problemas
                time.sleep(3)

                # Marcar o contato como enviado na coluna "Enviados" do DataFrame original
                contatos_df.loc[contatos_df['Telefone'] == row['Telefone'], 'Enviados'] = 'X'

        # Salvar as mudanças de volta no arquivo CSV
        contatos_df.to_csv('contatos_atualizados.csv', index=False)
        st.success("Mensagens enviadas com sucesso!")