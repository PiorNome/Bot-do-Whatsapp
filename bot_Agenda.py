import sqlite3, os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep

# Isso cria o arquivo do banco se não existir e conecta a ele
conexao = sqlite3.connect('cronograma.db')
cursor = conexao.cursor()

# Criando a tabela (Lógica SQL)
# O ID é automático, assim você não precisa se preocupar em numerar
cursor.execute('''
CREATE TABLE IF NOT EXISTS eventos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data_evento TEXT NOT NULL,
    materia TEXT NOT NULL,
    tipo TEXT NOT NULL,
    descricao TEXT
)
''')
conexao.commit()
# Configurações para não precisar de QR Code toda hora
chrome_options = Options()
caminho_atual = os.getcwd()
localizacao_cookie = os.path.join(caminho_atual, "cookie")
chrome_options.add_argument(f"--user-data-dir={localizacao_cookie}")

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
        sleep(0.3)
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
                sleep(2)
            else:
                # Se não houver nada, o bot fica em silêncio
                pass
        except Exception as e:
            print(f"Erro na patrulha: {e}")
    
except KeyboardInterrupt:
    print(bolinha)
    print("Fechando o bot")
except Exception as Erro:
    print(f"Aconteceu um erro inesperado: {Erro}")



driver.close()
conexao.close()