import os, time, json, threading
import bot_funcoes
from datetime import datetime
from neonize.client import NewClient
from neonize.events import MessageEv, ConnectedEv
from neonize.utils import build_jid
from dotenv import load_dotenv
load_dotenv()
representates = os.getenv('REPRESENTATES')

hora_inicio = time.time()

client = NewClient("teste.db")

thread_cronograma = None

@client.event(ConnectedEv)
def on_connected(client: NewClient, event: ConnectedEv):
    global thread_cronograma
    # Só inicia a thread se ela ainda não existir
    if thread_cronograma is None or not thread_cronograma.is_alive():
        thread_cronograma = threading.Thread(target=bot_funcoes.tarefa, args=(client,), daemon=True)
        thread_cronograma.start()
        print("🚀 Thread de tarefas iniciada!")

with open('emojis_materias.json', 'r', encoding='utf-8') as f:
    materia_emojis = json.load(f)

# Usando o que o seu terminal encontrou: 'event'
@client.event(MessageEv)
def on_message(client: NewClient, event: MessageEv):
    print(f"Mensagem recebida do CHAT ID: {event.Info.MessageSource.Chat}")

    hora_mensagem = event.Info.Timestamp / 1000
    print(f"hora inicio: {hora_inicio}")
    print(f"hora mensagem: {hora_mensagem}")
    if hora_mensagem < hora_inicio:
        return

    # 2. Proteção contra mensagens vazias ou de sistema
    # Verifica se a mensagem realmente tem uma conversa de texto
    texto = event.Message.conversation or event.Message.extendedTextMessage.text or ""
    if not texto:
        return 
    
    # 3. Proteção contra o Status (Ignora mensagens que vem do Status)
    if event.Info.MessageSource.Chat.Server in ["broadcast", "g.us", "newsletter"]:
        return


    resposta = []
    # remetente_jid já é o objeto que o WhatsApp precisa para responder
    remetente_jid = event.Info.MessageSource.Chat
    numero = event.Info.MessageSource.Sender.User

    bot = os.getenv("BOT")

    if str(numero) == bot:
        print('Mensagem do proprio bot')
        return
    
    msg = event.Message
    texto = msg.conversation or (msg.extendedTextMessage and msg.extendedTextMessage.text) or ""

    # Pega a data e hora atual para o log fazer sentido
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    # 'a' = append (anexa no final do arquivo)
    # encoding='utf-8' = garante que acentos e emojis não deem erro
    with open("logs_mensagens.txt", "a", encoding="utf-8") as arquivo:
        arquivo.write(f"[{agora}]\nUser: {event.Info.MessageSource.Chat.User}\nServer: {event.Info.MessageSource.Chat.Server}\nMensagem: {texto}\n-----------------------------\n")

    with open("confirmacao.txt", "r", encoding="utf-8") as confirmacao:
        pass
        enviar = confirmacao.read()
    
    amigo = os.getenv("AMIGO")
    if datetime.now().strftime("%d/%m/%Y") == enviar and numero == amigo:
        texto = texto.strip()
        if texto.lower() in ["s","si","sm","sim","yes","y", "pode", "sin"]:
            client.send_message(remetente_jid, "Cronocrama Sendo enviado...")
            comunidade = build_jid(os.getenv("GRUPO_COMUNIDADE_TESTE"), "g.us")

            with open("cronograma.txt", "r", encoding="utf-8") as cronograma:
                mensagem = cronograma.read()

            time.sleep(2)
            client.send_message(comunidade, mensagem)
            time.sleep(1)

            client.send_message(remetente_jid, "Cronograma Enviado")
        else:
            client.send_message(remetente_jid, "Então o envio terá que ser manual")

        with open("confirmacao.txt", "w", encoding="utf-8") as desconfirmacao:
            desconfirmacao.write("Sei lá, só precisava tirar o que tava")
        with open("cronograma.txt", "r", encoding="utf-8") as descronograma:
            descronograma.write("Sei lá, só precisava tirar o que tava")
        return
    
    try:
        print(f'Pessoa mandou: {texto}')
        
        resultado:list[str, any] = bot_funcoes.decidir_destino(texto.lower(), numero)
        print(f"Função decidir_destino retornou: {resultado}")

        if resultado[0] == 'agendar':
            print("comando agendar detectado")

            if "1" in resultado[1]:
                if resultado[1][0] == "1":
                    resposta.append('O formato da *data* está *inválida*')
                    resposta.append('Tente um desses formatos:')
                    resposta.append('   *DD/MM/YY*')
                    resposta.append('   ou')
                    resposta.append('   *DD/MM/YYYY*')

                if resultado[1][1] == "1":
                    resposta.append('\n')
                    resposta.append('*Matéria não encontrada*')
                    resposta.append('Olhe no *suap* as matérias existentes')

                if resultado[1][2] == "1":
                    resposta.append('\n')
                    resposta.append('Tipo do evento inválido')
                    resposta.append('Só aceito prova, trabalho, atividade ou vazio')

            elif resultado[1] == 'falta_agrs':
                resposta.append('Não foi possivel agendar o evento por falta de informações')
                resposta.append('*Como Usar o comando*:')
                resposta.append("   agendar [data] , [tipo] , [materia] , [descrição(opcinal)]")
                resposta.append('―――――――――――――――――――――――')
                resposta.append("Dica:")
                resposta.append("   Use \"tutorial agendar\" para obter mais informações")

            elif resultado[1] == 'sem_permissão':
                resposta.append('Você não tem permissão para usar esse comando')
            
            else:
                resposta.append('Evento salvo com sucesso')

        elif resultado[0] == 'Najudar':
            resposta.append('Não entendi o comando usado!')
            resposta.append('Aqui vão os comandos que temos, e como usa-los.')
            resposta.append("")

            if numero in representates:
                resposta.append("   agendar [data] , [tipo] , [materia] , [descrição(opcinal)]")
                resposta.append("   editar [id] , [o campo que você que mudar] , [o valor que você quer]")
                resposta.append("   listar")

            resposta.append("   status")
            resposta.append("   hoje")
            resposta.append("   amanha")
            resposta.append("   semana")
            resposta.append("   tutorial")
            resposta.append('―――――――――――――――――――――――')
            resposta.append("obs: Não coloque as informações dentro de colchetes")
            resposta.append('―――――――――――――――――――――――')
            resposta.append("Dica:")
            resposta.append("   Se você usar \"tutorial [comando]\", você irar ver um tutorial mais completo do comando especificado")


        elif resultado[0] == 'status' or resultado[0] == 'hoje' or resultado[0] == 'amanha' or resultado[0] == 'amanhã' or resultado[0] == 'semana' or resultado[0] == 'listar':
            if resultado[1]: # Resultado[1] = (ID, Data, Matéria, Tipo, Descrição)

                data_antiga = ''
                for infos in resultado[1]:
                    parte_mensagem_enviara = []
                    print(f'Informação sendo colocado na resposta: {infos}')

                    data = infos[1]
                    if data_antiga != data:
                        data_antiga = data
                        data_formatada = f'{data[-2:]}/{data[5:7]}'
                        parte_mensagem_enviara.append(f'### *{data_formatada}*')

                    if resultado[0] == 'listar':
                        parte_mensagem_enviara.append(f'🆔: {infos[0]}')

                    parte_mensagem_enviara.append(f'- {infos[3]} - {infos[2]} {materia_emojis[infos[2]]}')

                    resposta.extend(parte_mensagem_enviara)
                    if infos[4] != 'Vazio':
                        descricao = infos[4].replace('\n', '\n> ')
                        resposta.append(f'> {descricao}')
                    resposta.append('')

            else:
                resposta.append("Não a nenhum evento programado")
        
        elif resultado[0] == 'editar':
            # Primeiro ele vê se deu sucesso, depois se deu errado
            if 'sucesso' in resultado[1]:
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
                    resposta.append('coloque dessa forma "editar [ID do evento] , [campo que você quer alterar] , [novo valor que você quer]"')
                elif resultado[1] == 'falta_agrs':
                    resposta.append('❌Você colocou menos informações que deveria')
                    resposta.append('coloque dessa forma "editar [ID do evento] , [campo que você quer alterar] , [novo valor que você quer]"')
        
        elif resultado[0] == 'tutorial':
            # Primeiro vai verivicar se a pessoa pediu só "tutorial"
            # Depois vai verificar se o segundo argumento é um comando invalido "tutorial comando_não_existente"
            # E por ultimo vai verificar se o segundo argumento é um comando valido "tutorial agendar"
            if resultado[1] is None:
                resposta.append("Aqui vai o tutorial de como me usar")
                resposta.append("")
                resposta.append("Como me usar?")

                if numero in representates:
                    resposta.append("   agendar [data] , [tipo] , [materia] , [descrição(opcinal)]")
                    resposta.append("   editar [id] , [o campo que você que mudar] , [o valor que você quer]")
                    resposta.append("   listar")
                
                resposta.append("   status")
                resposta.append("   hoje")
                resposta.append("   amanha")
                resposta.append("   semana")
                resposta.append("   tutorial")
                resposta.append('―――――――――――――――――――――――')
                resposta.append('Dica: ')
                resposta.append('   Você pode usar "*tutorial [comando]*" para saber mais sobre um comando especificado')
                resposta.append('―――――――――――――――――――――――')
                resposta.append("obs: Não coloque as informações dentro de colchetes")
            
            elif resultado[1] == 'nao_encontrado':
                resposta.append("Não entendi o comando que você queria ajuda")
                resposta.append("")
                resposta.append("*Como me usar?*")

                if numero in representates:
                    resposta.append("   agendar [data] , [tipo] , [materia] , [descrição(opcinal)]")
                    resposta.append("   editar [id] , [o campo que você que mudar] , [o valor que você quer]")
                    resposta.append("   listar")

                resposta.append("   status")
                resposta.append("   hoje")
                resposta.append("   amanha")
                resposta.append("   semana")
                resposta.append("   tutorial")
                resposta.append('―――――――――――――――――――――――')
                resposta.append("obs: Não coloque as informações dentro de colchetes")
                resposta.append('―――――――――――――――――――――――')
                resposta.append("Dica:")
                resposta.append("   Se você usar \"tutorial [comando]\", você irar ver um tutorial mais completo do comando especificado")

            elif resultado[1] in ('agendar', 'status', 'hoje', 'amanha', 'amanhã', 'semana', 'editar', 'tutorial', 'listar',):
                if resultado[1] == 'agendar':
                    resposta.append("Com o comando *agendar*, você registra uma nova atividade no cronograma.")
                    resposta.append("Para usar o comando *agendar* você precisa ser *ADMIN*")
                    resposta.append("*Como usar?*")
                    resposta.append("   agendar [data] , [tipo] , [materia] , [descrição(opcinal)]")
                    resposta.append("―――――――――――――――――――――――")
                    resposta.append("Dicas: ")
                    resposta.append("   Na *data* escreva dessa forma *DD/MM*, *DD/MM/YY* ou *DD/MM/YYYY*")
                    resposta.append("   Na *matéria*, é aceito alguns erros de escrita, como faltar um acento em algumas letras")
                    resposta.append("   Ainda na matéria, você pode escrever as abreviações que estão no suap")
                    resposta.append("   No *tipo* só será aceito algum desses *Prova, trabalho, atividade ou Vazio*")
                    resposta.append('   Na *descrição*, você pode escrever o que quiser ou simplesmente deixar em branco.')

                elif resultado[1] == 'listar':
                    resposta.append("Com o comando *listar* você vê tudo o que está por vir")
                    resposta.append("Mas diferente do comando status, o listar mostra o ID")
                    resposta.append('')
                    resposta.append("*Como usar?*")
                    resposta.append("   listar")
                    resposta.append("―――――――――――――――――――――――")
                    resposta.append("obs: Para usar você realmente só escreve \"listar\"")
                    

                elif resultado[1] == 'status':
                    resposta.append("Com o comando *status* você vê *tudo* o que está por vir")
                    resposta.append("*Como usar?*")
                    resposta.append("   status")
                    resposta.append("―――――――――――――――――――――――")
                    resposta.append("obs: Para usar você realmente só escreve \"Status\"")

                elif resultado[1] == 'hoje':
                    resposta.append("Com o comando *hoje* você vê *tudo* que vai ter *hoje*")
                    resposta.append("*Como usar?*")
                    resposta.append("   hoje")
                    resposta.append("―――――――――――――――――――――――")
                    resposta.append("obs: Para usar você realmente só escreve \"Hoje\"")

                elif resultado[1] == 'amanha' or resultado[1] == 'amanhã':
                    resposta.append("Com o comando *amanha* você vê *tudo* que vai ter *amanhã*")
                    resposta.append("*Como usar?*")
                    resposta.append("   amanha")
                    resposta.append("―――――――――――――――――――――――")
                    resposta.append("Dica: É aceito *amanha* ou *amanhã*")
                    resposta.append("―――――――――――――――――――――――")
                    resposta.append("obs: Para usar você realmente só escreve \"Amanhã\"")

                elif resultado[1] == 'semana':
                    resposta.append("Com o comando *semana* você vê *tudo* que vai nessa *semana*")
                    resposta.append("*Como usar?*")
                    resposta.append("   semana")
                    resposta.append("―――――――――――――――――――――――")
                    resposta.append("obs: Para usar você realmente só escreve \"Semana\"")

                elif resultado[1] == 'editar':
                    resposta.append("Com o comando *editar* você pode editar um evento que foi salvo")
                    resposta.append("Para usar o comando *editar* você precisa ser *ADMIN*")
                    resposta.append("")
                    resposta.append("*Como usar?*")
                    resposta.append("   editar [ID] , [campo] , [valor]")
                    resposta.append("―――――――――――――――――――――――")
                    resposta.append("Dica:")
                    resposta.append("   Use o comando *\"listar\"* para saber o ID do evento")
                    resposta.append("   No *campo*, você escreve o que você quer mudar, pode-ser data, matéria, tipo ou descrição")
                    resposta.append("> Use o comando \"tutorial agendar\" para saber os tipos validos")
                    resposta.append("   No *valor*, você escreve a nova informação que deve entrar no lugar.")


                elif resultado[1] == 'tutorial':
                    resposta.append("Com o comando *tutorial* você pode ver como usar os outros comandos")
                    resposta.append("*Como usar?*")
                    resposta.append("   tutorial")
                    resposta.append("   tutorial [comando]")
                    resposta.append("―――――――――――――――――――――――")
                    resposta.append("Dica:")
                    resposta.append("   Se você usar só \"*tutorial*\", você irar ver um tutorial basico de cada comando")
                    resposta.append("   Se você usar \"tutorial [comando]\", você irar ver um tutorial mais completo do comando especificado")
                    resposta.append("> Use \"*tutorial*\" para ver os comandos existentes")

        resposta_final = '\n'.join(resposta)

        client.send_message(remetente_jid, resposta_final)

        print(f"A mensagem que será enviada é: {resposta}")
    except:
        pass

client.connect()
