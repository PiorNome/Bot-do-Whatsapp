"""
    Pra eu não me perder na lógica: Agr tenho que pegar o número da pessoa e mandar junto com a mensagem dela, e verificar se ela é um dos adimins do grupo.
"""

import os
import bot_funcoes
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from time import sleep
# Configurações para não precisar de QR Code toda hora
chrome_options = Options()
caminho_atual = os.getcwd()
localizacao_cookie = os.path.join(caminho_atual, "cookie")
chrome_options.add_argument(f"--user-data-dir={localizacao_cookie}")

RESPOSTAS_SISTEMA = {
    'agendar': {
        'erros': ['Data invalida\n', 'Matéria invalida\n', 'Tipo invalido\n'],
        'ajuda': ['Formato valido: DD/MM/YY ou DD/MM/YYYY\n', '\n', 'Tipos aceitos: Prova, Trabalho e Vazio\n']
        }
}


# Inicia o navegador
servico = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=servico, options=chrome_options)

# Abre o WhatsApp Web
driver.get("https://web.whatsapp.com")
for tentativa in range(3):
    try:
        # Espera até 60 segundos (tempo bom para dar tempo de ler o QR Code)
        elemento = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
        )
        print("WhatsApp carregado e pronto!")
        entrou = True
    except:
        print("Ocorreu um erro: O site demorou demais para carregar ou o QR Code expirou.")
        driver.quit()
        entrou = False
    finally:
        if entrou:
            break


try:
    while entrou:
        sleep(0.07)
        # Procuramos um SPAN que contenha a palavra 'lida' no seu rótulo de acessibilidade
            # Isso filtra apenas as notificações reais.
        try:
            notificacoes = driver.find_elements(By.XPATH, "//span[contains(@aria-label, 'lida')]")

            if len(notificacoes) > 0:
                # Pegamos a última bolinha da lista (geralmente as mais recentes ficam embaixo)
                bolinha = notificacoes[-1]
                
                # Movemos o mouse até a bolinha e clicamos (mais seguro que o .click direto)
                ActionChains(driver).move_to_element_with_offset(bolinha, -50, 0).click().perform()
                print("Agendaman detectou uma mensagem real e abriu a conversa!")
                sleep(0.5)
                baloes_recebidos = driver.find_elements(By.CSS_SELECTOR, "div.message-in")
                if len(baloes_recebidos) > 0:
                    mensagem = baloes_recebidos[-1].text
                    mensagem = mensagem[:-6]
                    print(f'Pessoa mandou: {mensagem}')
                    resultado = bot_funcoes.decidir_destino(mensagem.lower())
                    print(f"Função decidir_destino retornou: {resultado}")

                    resposta = ''

                    if resultado[0] == 'agendar':
                        print("comando agendar detectado")
                        if "1" in resultado[1]:
                            print(f"Tem erros: {resultado[1]}")
                            for ind, mensagem in enumerate(RESPOSTAS_SISTEMA[resultado[0]]['erros']):
                                if resultado[1][ind] == "1":
                                    resposta += RESPOSTAS_SISTEMA[resultado[0]]['erros'][ind]
                                    resposta += RESPOSTAS_SISTEMA[resultado[0]]['ajuda'][ind]
                        elif resultado[1] == 'falta_agrs':
                            resposta += 'Não foi possivel completar a tafefa por falta argumentos\nTente colocar: agendar DD/MM/YY ou DD/MM/YYYY | Matéria | Tipo (Prova, Trabalho ou Vazio) | descrição (opcinal)'
                        else:
                            resposta += 'Evento salvo com sucesso'

                    elif resultado[0] == 'Najudar':
                        resposta += 'Não entendi o camando usado\nTente colocar agendar DD/MM/YY ou DD/MM/YYYY | Matéria | Tipo (Prova, Trabalho ou Vazio) | descrição (opcinal)\nver_eventos'

                    print(f"A mensagem que será enviada é: {resposta}")

                
                    barra_texto = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
                    barra_texto.click()
                    barra_texto.send_keys(resposta)
                    barra_texto.send_keys(Keys.ENTER)
                    barra_texto.send_keys(Keys.ESCAPE)

            else:
                # Se não houver nada, o bot fica em silêncio
                pass
        except Exception as e:
            barra_texto = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
            barra_texto.send_keys(Keys.ESCAPE)
            print(f"Erro na patrulha: {e}")
    
except KeyboardInterrupt:
    print("Fechando o bot")
except Exception as Erro:
    print(f"Aconteceu um erro inesperado: {Erro}")

finally:
    driver.quit()
    print("Bot fechado com sucesso")