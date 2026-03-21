import os
import pyperclip
import bot_funcoes
import random
from flask import Flask, send_file
import threading
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

# ==========================================
# 1. CONFIGURAÇÃO DO SERVIDOR WEB (FLASK)
# ==========================================
#app = Flask(__name__)
# Pega a porta dinâmica do Render ou usa a 10000 por padrão
#port = int(os.environ.get("PORT", 10000))

#@app.route('/')
#def show_qr():
#    if os.path.exists("qrcode.png"):
#        return send_file("qrcode.png", mimetype='image/png')
#    return "QR Code ainda não gerado. Aguarde alguns segundos e atualize a página."

#def run_flask():
#    app.run(host='0.0.0.0', port=port)

# Inicia o servidor em uma thread separada para não travar o bot
#threading.Thread(target=run_flask, daemon=True).start()

# ==========================================
# 2. CONFIGURAÇÕES DO SELENIUM E CHROME
# ==========================================
chrome_options = Options()
caminho_atual = os.getcwd()
localizacao_cookie = os.path.join(caminho_atual, "cookie")

chrome_options.add_argument(f"--user-data-dir={localizacao_cookie}")
#chrome_options.add_argument("--headless=new") # Atualizado para melhor performance
chrome_options.add_argument("--no-sandbox") 
chrome_options.add_argument("--disable-dev-shm-usage") 
#chrome_options.add_argument('--window-size=1920,1080') 

service = Service(ChromeDriverManager().install())

service = Service(ChromeDriverManager().install())

# O caminho do Chrome instalado pelo script no Render:
#chrome_options.binary_location = "/opt/render/project/.render/chrome/opt/google/chrome/google-chrome"

# ==========================================
# 3. VARIÁVEIS E FUNÇÕES DO BOT
# ==========================================
RESPOSTAS_SISTEMA = {
    'agendar': {
        'erros': ['Data invalida', 'Matéria invalida', 'Tipo invalido'],
        'ajuda': ['Tente esse formato: DD/MM/YY ou DD/MM/YYYY', '', 'Tipos aceitos: Prova, Trabalho, atividade e Vazio']
        }
}


print("Iniciando o Chrome...")
try:
    driver = webdriver.Chrome(service=service, options=chrome_options)
    print("✅ Navegador iniciado com sucesso!")
except Exception as e:
    print(f"❌ Erro ao iniciar o navegador: {e}")
    # Fallback caso o manager falhe: tentar iniciar sem o service manual
    driver = webdriver.Chrome(options=chrome_options)

print("Acessando o WhatsApp Web...")
driver.get("https://web.whatsapp.com")
sleep(6) # Aguarda o carregamento da página

#try:
#    # Espera até 60 segundos para o elemento 'canvas' (onde fica o QR Code) aparecer
#    wait = WebDriverWait(driver, 60)
#    wait.until(EC.presence_of_element_located((By.TAG_NAME, "canvas")))
    
    # Dá mais 5 segundos extras para garantir que o QR Code desenhou completamente
#    sleep(5) 
    
#    driver.save_screenshot("qrcode.png")
#    print("✅ QR Code capturado com sucesso! Verifique o link agora.")
#except Exception as e:
#    print(f"❌ O QR Code não carregou a tempo: {e}")
#    driver.save_screenshot("erro_carregamento.png")

entrou = False
for tentativa in range(3):
    if entrou:
        continue
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


try:
    resposta = []
    while entrou:
        sleep(0.00056)
        try:
            notificacao = driver.find_elements(By.XPATH, "//span[contains(@aria-label, 'lida')]")

            if len(notificacao) > 0:
                # Pegamos a última bolinha da lista (geralmente as mais recentes ficam embaixo)
                sleep(2)
                notificacoes = driver.find_elements(By.XPATH, "//span[contains(@aria-label, 'lida')]")
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
                        resposta.append('   *Agendar*: estilo de entrada》 !agendar DD/MM/YY ou DD/MM/YYYY (data) | Matéria | Tipo (Prova, Trabalho, atividade ou Vazio) | descrição (opcinal)')
                        resposta.append('   *Exemplo de mensagem*: ')
                        resposta.append('       !agendar 12/08/2008|Português|Prova|verbos,Redação,corigas')
                        resposta.append('')
                        resposta.append('   *status*: !status (serve para ver todos os eventos que irão ter)')
                        resposta.append('')
                        resposta.append('   *hoje*: !hoje (serve para ver todos os eventos que irão ter hoje)')
                        resposta.append('')
                        resposta.append('   *amanhã*: !amanhã (serve para ver todos os eventos de amanhã)')
                        resposta.append('   *Exemplo da resposta dos 3 comandos acima*:')
                        resposta.append('       🆔 [15] - Física')
                        resposta.append('       📅 Data: 13/03/26')
                        resposta.append('       ✍️ Tipo: Prova')
                        resposta.append('       📚 O que estudar: Ondas')
                        resposta.append('       ―――――――――――――――――――――――')

                    elif resultado[0] == 'status' or resultado[0] == 'hoje' or resultado[0] == 'amanha' or resultado[0] == 'amanhã':
                        if resultado[1]: # Resultado[1] = (ID, Data, Matéria, Tipo, Descrição)
                            for infos in resultado[1]:
                                parte_mensagem_enviara = []
                                print(f'Informação sendo colocado na resposta: {infos}')
                                data = infos[1]
                                data_formatada = f'{data[-2:]}/{data[5:7]}/{data[:4]}'
                                parte_mensagem_enviara.append(f'🆔[{infos[0]}]' + f' ― {infos[2]}')
                                parte_mensagem_enviara.append(f'📅Data: {data_formatada}')
                                parte_mensagem_enviara.append(f'✍️Tipo: {infos[3]}')
                                resposta.extend(parte_mensagem_enviara)
                                if infos[4] != 'Vazio':
                                    resposta.append(f'📚O que estudar: {infos[4]}')
                                resposta.append('―――――――――――――――――――――――')

                        else:
                            resposta.append("Não a nenhum evento programado")
                    
                    elif resultado[0] == 'editar':
                        # Primeiro ele vê se deu sucesso, depois se deu errado
                        if 'sucesso' in resultado[1]:
                            bot_funcoes.editar_bd
                            if resultado[1] == 'sucesso_data':
                                resposta.append('Sucesso ao editar a data🌟')
                            elif resultado[1] == 'sucesso_materia':
                                resposta.append('Sucesso ao editar a matéria🌟')
                            elif resultado[1] == 'sucesso_tipo':
                                resposta.append('Sucesso ao editar o tipo do evento🌟')
                            elif resultado[1] == 'sucesso_descricao':
                                resposta.append('Sucesso ao editar a descrição🌟')
                        
                        elif 'invalido' in resultado[1]:
                            if resultado[1] == 'id_invalido':
                                resposta.append('❌O id que você digitou é invalido')
                                resposta.append('Use o comando *status* para saber o id dos eventos')
                            elif resultado[1] == 'data_invalido':
                                resposta.append('❌A data que você digitou é invalida')
                                resposta.append('Digite a data em um desses formatos DD/MM/YY ou DD/MM/YYYY')
                            elif resultado[1] == 'materia_invalido':
                                resposta.append('❌A matéria que você digitou é invalida')
                                resposta.append('Olhe no suap para saber as matérias')
                            elif resultado[1] == 'tipo_invalido':
                                resposta.append('❌O tipo que você digitou é invalida')
                                resposta.append('Os tipos validos são: Prova, atividade, trabalho ou lição')
                            elif resultado[1] == 'campo_invalido':
                                resposta.append('❌O campo que você queria mudar é invalido')
                                resposta.append('Os campos aceitos são: data, tipo ou matéria')
                        
                        else: # Aqui vai ficar os casos de muitos argumentou e os poucos argumentos
                            if resultado[1] == 'muitos_agrs':
                                resposta.append('❌Você colocou mais informações do que deveria')
                                resposta.append('coloque dessa forma "editar [ID do evento] | [campo que você quer alterar] | [novo valor que você quer]"')
                            elif resultado[1] == 'falta_agrs':
                                resposta.append('❌Você colocou menos informações que deveria')
                                resposta.append('coloque dessa forma "editar [ID do evento] | [campo que você quer alterar] | [novo valor que você quer]"')
                    
                    elif resultado[0] == 'tutorial':
                        # Primeiro vai verivicar se a pessoa pediu só "tutorial"
                        # Depois vai verificar se o segundo argumento é um comando invalido "tutorial comando_não_existente"
                        # E por ultimo vai verificar se o segundo argumento é um comando valido "tutorial agendar"
                        if resultado[1] is None:
                            resposta.append("Aqui vai o tutorial de como me usar")
                            resposta.append("")
                            resposta.append("Como me usar?")
                            resposta.append("   agendar [data] | [materia] | [tipo] | [descrição(opcinal)]")
                            resposta.append("   editar [id] | [o campo que você que mudar] | [o valor que você quer]")
                            resposta.append("   status")
                            resposta.append("   hoje")
                            resposta.append("   amanha")
                            resposta.append('―――――――――――――――――――――――')
                            resposta.append('Dica: ')
                            resposta.append('   Você pode usar "*tutorial [comando]*" para saber mais sobre um comando especiicado')
                            resposta.append('―――――――――――――――――――――――')
                            resposta.append("obs: Não coloque as informações dentro de colchetes")
                        
                        elif resultado[1] == 'nao_encontrado':
                            resposta.append("Não entendi o comando que você queria ajuda")
                            resposta.append("")
                            resposta.append("*Como me usar?*")
                            resposta.append("   agendar [data] | [materia] | [tipo] | [descrição(opcinal)]")
                            resposta.append("   editar [id] | [o campo que você que mudar] | [o valor que você quer]")
                            resposta.append("   status")
                            resposta.append("   hoje")
                            resposta.append("   amanha")
                            resposta.append('―――――――――――――――――――――――')
                            resposta.append("obs: Não coloque as informações dentro de colchetes")

                        elif resultado[1] in ('agendar', 'status', 'hoje', 'amanha', 'amanhã', 'editar', 'tutorial',):
                            if resultado[1] == 'agendar':
                                resposta.append("Com o comando *agendar*, você registra uma nova atividade no seu cronograma.")
                                resposta.append("Para usar o comando *agendar* você precisa ser *ADMIN*")
                                resposta.append("*Como usar?*")
                                resposta.append("   agendar [data] | [materia] | [tipo] | [descrição(opcinal)]")
                                resposta.append("―――――――――――――――――――――――")
                                resposta.append("Dicas: ")
                                resposta.append("   Na *data* escreva dessa forma *DD/MM/YY* ou *DD/MM/YYYY*")
                                resposta.append("   Na *matéria*, é aceito alguns erros de escrita, como faltar um acento em algumas letras")
                                resposta.append("   Ainda na matéria, você pode escrever as abreviações que estão no suap")
                                resposta.append("   No *tipo* só será aceito algum desses *Prova, trabalho, atividade ou Vazio*")
                                resposta.append('   Na *descrição*, você pode escrever o que quiser ou simplesmente deixar em branco.')

                            elif resultado[1] == 'status':
                                resposta.append("Com o comando *status* você *tudo* o que está por vir")
                                resposta.append("*Como usar?*")
                                resposta.append("   status")
                                resposta.append("―――――――――――――――――――――――")
                                resposta.append("obs: Para usar você realmente só escreve \"!Status\"")

                            elif resultado[1] == 'hoje':
                                resposta.append("Com o comando *hoje* você *tudo* que vai ter *hoje*")
                                resposta.append("*Como usar?*")
                                resposta.append("   hoje")
                                resposta.append("―――――――――――――――――――――――")
                                resposta.append("obs: Para usar você realmente só escreve \"!Hoje\"")

                            elif resultado[1] == 'amanha' or resultado[1] == 'amanhã':
                                resposta.append("Com o comando *amanha* você *tudo* que vai ter *amanhã*")
                                resposta.append("*Como usar?*")
                                resposta.append("   amanha")
                                resposta.append("―――――――――――――――――――――――")
                                resposta.append("Dica: É aceito *!amanha* ou *!amanhã*")
                                resposta.append("―――――――――――――――――――――――")
                                resposta.append("obs: Para usar você realmente só escreve \"!Amanha\"")

                            elif resultado[1] == 'editar':
                                resposta.append("Com o comando *editar* você pode editar um evento que foi salvo")
                                resposta.append("Para usar o comando *editar* você precisa ser *ADMIN*")
                                resposta.append("*Como usar?*")
                                resposta.append("   editar [ID] | [campo] | [valor]")
                                resposta.append("―――――――――――――――――――――――")
                                resposta.append("Dica:")
                                resposta.append("   Use o comando *\"!status\"* para saber o ID do evento")
                                resposta.append("   No *campo*, você escreve o que você quer mudar, pode-ser data, matéria, tipo ou descrição")
                                resposta.append("> Use o comando \"!tutorial agendar\" para saber os tipos validos")
                                resposta.append("   No *valor*, você escreve a nova informação que deve entrar no lugar.")


                            elif resultado[1] == 'tutorial':
                                resposta.append("Com o comando *tutorial* você pode ver como usar os outros comandos")
                                resposta.append("*Como usar?*")
                                resposta.append("   !tutorial")
                                resposta.append("   !tutorial [comando]")
                                resposta.append("―――――――――――――――――――――――")
                                resposta.append("Dica:")
                                resposta.append("   Se você usar só \"*!tutorial*\", você irar ver um tutorial basico de cada comando")
                                resposta.append("   Se você usar \"tutorial [comando]\", você irar ver um tutorial mais completo do comando especificado")
                                resposta.append("> Use \"*!tutorial*\" para ver os comandos existentes")


                    print(f"A mensagem que será enviada é: {resposta}")

                    barra_texto = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
                    barra_texto.click()

                    #driver.execute_script("arguments[0].innerText = arguments[1];", barra_texto, mensagem)
                    #barra_texto.send_keys(Keys.SPACE)

                    action = ActionChains(driver)
                    for linha in resposta:
                        for letra in linha:
                            
                            if ord(letra) > 0xffff:
                                driver.execute_script("arguments[0].innerText += arguments[1];", barra_texto, letra)
                            
                            else:
                                barra_texto.send_keys(letra)

                            #sleep(random.uniform(0.1, 0.3))
                        action.key_down(Keys.SHIFT).send_keys(Keys.ENTER).key_up(Keys.SHIFT).perform()

                    #resposta_final = '\n'.join(resposta)
                    #pyperclip.copy(resposta_final)

                    #barra_texto.send_keys(Keys.CONTROL, 'v')
                    #sleep(0.7)
                    barra_texto.send_keys(Keys.ENTER)

                    barra_texto.send_keys(Keys.ENTER)
                    barra_texto.send_keys(Keys.ESCAPE)
                    del  resposta[:]#, resposta_final

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