'''
    Adicionar o comando editar aqui, e terminar no bot_funçoes
    Adicionar o tutorial aqui, terminar no bot_funçoes
'''

import os
import pyperclip
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
        'erros': ['Data invalida', 'Matéria invalida', 'Tipo invalido'],
        'ajuda': ['Tente esse formato: DD/MM/YY ou DD/MM/YYYY', '', 'Tipos aceitos: Prova, Trabalho, atividade e Vazio']
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
        entrou = False
    finally:
        if entrou:
            break


try:
    resposta = []
    while entrou:
        sleep(0.00056)
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

                    #Essa parte vai pegar o número da pessoa e vai "limpalo"]
                    #De "+55 11 98765-4321" para "5511987654321"
                    # 1. Abre o perfil (como você já fez)
                    seletor_cabecalho = 'header div[title="Dados do perfil"]'
                    WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.CSS_SELECTOR, seletor_cabecalho))).click()

                    # 2. Aguarda a barra lateral carregar (importante!)
                    sleep(1.3)

                    # 3. SCANNER: Pega todos os elementos que podem ter texto
                    todos_os_spans = driver.find_elements(By.CSS_SELECTOR, 'span[data-testid="selectable-text"]')

                    nome_capturado = "Não encontrado"
                    numero_capturado = "Não encontrado"

                    for span in todos_os_spans:
                        texto = span.text.strip()
                        
                        # Se o texto tem um '+', quase certeza que é o número
                        if '+' in texto and any(char.isdigit() for char in texto):
                            numero_capturado = texto
                        
                        # O primeiro span longo que não tem '+' geralmente é o Nome ou o Recado
                        # (Você pode ajustar essa lógica para pegar o nome no topo da barra)

                    print(f"DEBUG - Texto Bruto Encontrado: {numero_capturado}")

                    # Agora sim, limpamos
                    numero_pessoa = "".join(filter(str.isdigit, numero_capturado))
                    print(f"RESULTADO - Número da pessoa: {numero_pessoa}")
                    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                    
                    resultado = bot_funcoes.decidir_destino(mensagem.lower(), numero_pessoa)
                    print(f"Função decidir_destino retornou: {resultado}")

                    if resultado[0] == 'agendar':
                        print("comando agendar detectado")

                        if "1" in resultado[1]:
                            print(f"Tem erros: {resultado[1]}")
                            for ind, mensagem in enumerate(RESPOSTAS_SISTEMA[resultado[0]]['erros']):
                                if resultado[1][ind] == "1":
                                    resposta.append(RESPOSTAS_SISTEMA[resultado[0]]['erros'][ind])
                                    resposta.append(RESPOSTAS_SISTEMA[resultado[0]]['ajuda'][ind])

                        elif resultado[1] == 'falta_agrs':
                            resposta.append('Não foi possivel agendar o evento por falta argumentos')
                            resposta.append('*Como Usar o comando*:')
                            resposta.append('   *Agendar*: estilo de entrada 》 agendar DD/MM/YY ou DD/MM/YYYY (data) | Matéria | Tipo (Prova, Trabalho, atividade ou Vazio) | descrição (opcinal)')
                            resposta.append('   *Exemplo de mensagem*: ')
                            resposta.append('       agendar 31/12/1999|Português|Prova|verbos, Redação, corigas')

                        elif resultado[1] == 'sem_permissão':
                            resposta.append('Você não tem permissão para usar esse comando')
                        
                        else:
                            resposta.append('Evento salvo com sucesso')

                    elif resultado[0] == 'Najudar':
                        resposta.append('Não entendi o comando usado!')
                        resposta.append('Aqui vão os comandos que temos, e como usa-los.')
                        resposta.append('   *Agendar*: estilo de entrada》 agendar DD/MM/YY ou DD/MM/YYYY (data) | Matéria | Tipo (Prova, Trabalho, atividade ou Vazio) | descrição (opcinal)')
                        resposta.append('   *Exemplo de mensagem*: ')
                        resposta.append('       agendar 12/08/2008|Português|Prova|verbos,Redação,corigas')
                        resposta.append('')
                        resposta.append('   *status*: status (serve para ver todos os eventos que irão ter)')
                        resposta.append('')
                        resposta.append('   *hoje*: hoje (serve para ver todos os eventos que irão ter hoje)')
                        resposta.append('')
                        resposta.append('   *amanhã*: amanhã (serve para ver todos os eventos de amanhã)')
                        resposta.append('   *Exemplo da resposta dos 3 comandos acima*:')
                        resposta.append('       🆔 [15] - Física')
                        resposta.append('       📅 Data: 2026-03-12')
                        resposta.append('       ✍️ Tipo: Prova')
                        resposta.append('       📚 O que estudar: Ondas')
                        resposta.append('       ―――――――――――――――――――――――')

                    elif resultado[0] == 'status' or resultado[0] == 'hoje' or resultado[0] == 'amanha' or resultado[0] == 'amanhã':
                        if resultado[1]: # Resultado[1] = (ID, Data, Matéria, Tipo, Descrição)
                            for infos in resultado[1]:
                                parte_mensagem_enviara = []
                                print(f'Informação sendo colocado na resposta: {infos}')
                                parte_mensagem_enviara.append(f'🆔[{infos[0]}]' + f' ― {infos[2]}')
                                parte_mensagem_enviara.append(f'📅Data: {infos[1]}')
                                parte_mensagem_enviara.append(f'✍️Tipo: {infos[3]}')
                                resposta.extend(parte_mensagem_enviara)
                                if infos[4] != 'Vazio':
                                    resposta.append(f'📚O que estudar: {infos[4]}')
                                resposta.append('―――――――――――――――――――――――')

                        else:
                            resposta.append("Não a nenhum evento programado")

                    print(f"A mensagem que será enviada é: {resposta}")

                    barra_texto = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
                    barra_texto.click()

                    resposta_final = '\n'.join(resposta)
                    pyperclip.copy(resposta_final)

                    barra_texto.send_keys(Keys.CONTROL, 'v')
                    sleep(0.7)
                    barra_texto.send_keys(Keys.ENTER)

                    barra_texto.send_keys(Keys.ENTER)
                    barra_texto.send_keys(Keys.ESCAPE)
                    del resposta_final, resposta[:]

            else:
                # Se não houver nada, o bot fica em silêncio
                pass
        except Exception as e:
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
            print(f"Erro na patrulha: {e}")
    
except KeyboardInterrupt:
    print("Fechando o bot")
except Exception as Erro:
    print(f"Aconteceu um erro inesperado: {Erro}")

finally:
    driver.quit()
    print("Bot fechado com sucesso")