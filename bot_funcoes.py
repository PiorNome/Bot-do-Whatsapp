import os, sqlite3, json
from time import sleep
from datetime import *
from dateutil.relativedelta import relativedelta
from neonize.client import NewClient
from neonize.utils import build_jid
from dotenv import load_dotenv
load_dotenv()
def decidir_destino(texto:str, numero_celular:str) -> tuple[str, any]:
    print(f"[Função: decidir_destino]")
    print(f"Recebeu {texto}")
    comandos = ['agendar', 'status', 'hoje', 'amanha', 'amanhã', 'tutorial', 'editar', 'semana', 'listar', 'deletar']
    lista_strs = texto.lower().split()
    numeros = os.getenv('REPRESENTATES')
    REPRESENTATES = numeros.split(' , ')
    print(f"Mensagem separada como: {lista_strs}")

    print(f"Comando da mensagem é: {lista_strs[0]}")

    
    print(f"A lista_strns tem {len(lista_strs)} de elementos")
    if lista_strs[0] in comandos:
        if lista_strs[0] == 'agendar':
            comando = 'agendar'
            print(f"Entrou como comando agendar")
            if not numero_celular in REPRESENTATES:
                print(f"O número {numero_celular} não é ADMIN")
                return (comando, 'sem_permissão')
            print(f"O número {numero_celular} é ADMIN")
            
            if "agendar" in texto: agendamentos = texto.split('agendar')[1:]
            elif "Agendar" in texto: agendamentos = texto.split('Agendar')[1:]
            elif "AGENDAR" in texto: agendamentos = texto.split('AGENDAR')[1:]
            else: return (comando, 'erro_escrita')
            print(f"Agendamentos separados assim: {agendamentos}")
            erros = []
            for evento in agendamentos:
                erros.append(adicionar_bd(evento.strip()))
            print(f"Função adicionar_bd retornou: {erros}")

            retorna = []
            ind_erro = ""
            for erro in erros:
                print(f"Peguei uma tupla: {erro}")
                if -1 in erro:
                        print(f'Tinha o valor -1, falta de argumentos')
                        retorna.append('falta_agrs')
                        continue
                
                ind_erro = str(erro[0]) + str(erro[1]) + str(erro[2])
                print(f"Variavel ind_erro: {ind_erro}")
                retorna.append(ind_erro)
                ind_erro = ""
            print(f"Será retornado: {comando} e {retorna}")
            print("[Acabou a função decidir_destino]")
            return (comando,tuple(retorna),)
        
        elif lista_strs[0] == 'status' or lista_strs[0] == 'hoje' or lista_strs[0] == 'amanha' or lista_strs[0] == 'amanhã' or lista_strs[0] == 'listar':
            comando = lista_strs[0]
            print(f"O comando usado para ver os eventos foi: \"{comando}\"")
            print("Buscando eventos")
            resultados = buscar_eventos(comando)
            print('Eventos pegos')
            print("[Acabou a função decidir_destino]")
            return (comando,resultados)

        elif lista_strs[0] == 'editar':
            print('Comando "editar" detectado')
            comando = 'editar'

            if not numero_celular in REPRESENTATES:
                print(f"O número {numero_celular} não é ADMIN")
                return (comando, 'sem_permissão')
            print('Esse numero é admin')
            print('Indo para a função para editar')
            resultado = editar_bd(texto)
            print(f"a função retornou: {resultado}")
            print("[Acabou a função decidir_destino]")
            return (comando, resultado,)
        
        elif lista_strs[0] == 'tutorial':
            print("Comando tutorial detectado")
            comando = 'tutorial'

            if len(lista_strs) > 1:
                print(f"Tem outro comando: {lista_strs[1]}")

                if lista_strs[1] in comandos:
                    print("Acho o segundo comando")
                    print("[Acabou a função decidir_destino]")
                    return (comando, lista_strs[1],)
                
                print('segundo comando não encontrado')
                print("[Acabou a função decidir_destino]")
                return (comando, 'nao_encontrado',)
            
            print("[Acabou a função decidir_destino]")
            return (comando, None,)
        
        elif lista_strs[0] == 'semana':
            # uma colinha para eu saber o indice
            "Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"
            #       0              1               2               3              4            5         6

            print('Comando Semana detectado')
            comando = 'semana'
            hoje = datetime.now()
            hoje_formatado = hoje.strftime("%Y-%m-%d")
            dia_semana = hoje.weekday()

            # Alvo é Sexta (4). Cálculo: (Alvo - Hoje) % 7
            dias_faltando = (4 - dia_semana) % 7

            print(f'Falta {dias_faltando} para a Sexta-Feira')

            # Se hoje for sexta e você quiser a da SEMANA QUE VEM, force 7 dias:
            if dias_faltando == 0: 
                dias_faltando = 7

            sexta = hoje + timedelta(days=dias_faltando)
            sexta_formatada = sexta.strftime("%Y-%m-%d")

            eventos_pegos = buscar_evento_semana(hoje_formatado, sexta_formatada)

            print('[Acabou a função decidir_destino]')
            return (comando, eventos_pegos)
        
        elif lista_strs[0] == 'deletar':
            comando = 'deletar'

            if not numero_celular in REPRESENTATES:
                print(f"O número {numero_celular} não é ADMIN")
                return (comando, 'sem_permissão')
            
            if not lista_strs[1].isdecimal():
                return "nao_decimal"
            
            qnt_deletado = comando_deletar(lista_strs[1])
            if qnt_deletado == -1:
                return (comando, 'falha_interna',)
            
            return (comando, qnt_deletado,)
        
    elif (qnt_lista_strs:= len(lista_strs)) in (2,3,):
        passa = False
        if qnt_lista_strs == 2:
            if (lista_strs[0] == "proximo" or lista_strs[0] == "próximo") and (lista_strs[1] == "mes" or lista_strs[1] == "mês"):
                print("Passou em 2 elementos")
                passa = True
        else:
            if (lista_strs[0] == "mes" or lista_strs[0] == "mês") and lista_strs[1] == "que" and lista_strs[2] == "vem":
                print("Passou em 3 elementos")
                passa = True
        
        if passa:
            comando = 'proximo_mes'
            hoje = datetime.now()
            proximo_mes = hoje + relativedelta(months=1)
            data = proximo_mes.strftime("%Y-%m")
            eventos= eventos_proximo_mes(data)
            return (comando, eventos,)
        
    print("[Acabou a função decidir_destino]")
    return ('Najudar', None)

def adicionar_bd(texto:str) -> tuple[int]:
    print(f"[Função: adicionar_bd]")
    
    with open('constantes.json', 'r', encoding='utf-8') as f:
        MATERIAS = json.load(f)

    print("pegou as materias")
    retorna = [0, 0, 0] # se algum for igual a 1, significa que deu erro. Data é o 1º elemento, materia é o 2º elemento e o tipo é o 3º elemento

    informacoes = texto.split(",")
    print(f"Separou as informações")
    qntd = len(informacoes) # A quantidade de partes que tem
    if qntd >= 3:
        data = informacoes[0].strip()
        tipo = informacoes[1].strip()
        materia = informacoes[2].strip()

        descricao = 'Vazio'
        if qntd > 3:
            descricao = ''
            descricao = ",".join(informacoes[3:]).strip()
            print(f"Adicionou a descrição: {descricao}")
    
        # O bot vai verivicar se a data está certá
        # O bot tenta aceitar tanto 25/04/26 quanto 25/04/2026
        formatos = ("%d/%m/%y", "%d/%m/%Y", "%d/%m")
    
        try:
            print(f"Data colocada pelo usuario: {data}")
            data_objeto = datetime.strptime(data, formatos[0])
            print("Data valida")
        except:
            try:
                data_objeto = datetime.strptime(data, formatos[1])
                print("Data valida")
            except:
                try:
                    data_objeto = datetime.strptime(data, formatos[2])
                    data_objeto = data_objeto.replace(year=2026)
                    print("Data valida")
                except:
                    print("Data invalida")
                    retorna[0] = 1
        
        encontrou_materia = False
        for materia_key in MATERIAS.keys():
            if materia.lower() in MATERIAS[materia_key]:
                materia = materia_key
                encontrou_materia = True
                print(f"Encontro a matéria: {materia}")
                break
        if not encontrou_materia:
            print("Não encontrou a matéria")
            retorna[1] = 1
        

        if not 1 in retorna:
            print("Salvando no Banco de Dados")
            sql = "INSERT INTO eventos(data_evento, materia, tipo, descricao) VALUES (?, ?, ?, ?)"
            valores = (data_objeto.date(), materia, tipo.title(), descricao)
            conexao = sqlite3.connect('cronograma.db')
            curso = conexao.cursor()
            curso.execute(sql, valores)
            print("Salvou no Banco de Dados")
            conexao.commit()
        print("[Acabou a função adicionar_bd]")
        return tuple(retorna)
    print("Por falta de argumentos, será retornado (-1)")
    print("[Acabou a função adicionar_bd]")
    return (-1,)

def buscar_evento_semana(hoje, sexta):
    print("[Função buscar_evento_semana]")
    conexao = sqlite3.connect('cronograma.db')
    print('Conexão feita')

    curso = conexao.cursor()
    curso.execute(
        """
            SELECT * FROM eventos
            WHERE data_evento BETWEEN ? AND ?
            ORDER BY data_evento ASC, materia ASC;
        """, (hoje, sexta,)
    )
    print('Comando dado')

    resultados = curso.fetchall()
    print('Resultados pegos')

    conexao.close()
    print("[Acabou a função buscar_evento_semana]")
    return resultados

def buscar_eventos(quando:str='') -> list[tuple]:
    print('[Função buscar_eventos]')
    conexao = sqlite3.connect('cronograma.db')
    print('Conexão feita')
    curso = conexao.cursor()
    
    try:
        if quando == '' or quando == 'status' or quando == 'listar':
            data = date.today()
            print(f"Pegou a variavel data: {data}")
            curso.execute(
                '''SELECT * FROM eventos
                WHERE data_evento >= ?
                ORDER BY data_evento ASC, materia ASC;''', (data,)
            )
        elif quando == 'hoje':
            hoje = date.today()
            print(f"Pegou a viriavel hoje: {hoje}")
            curso.execute(
                '''SELECT * FROM eventos
                WHERE data_evento = ?
                ORDER BY data_evento ASC, materia ASC;''', (hoje,)
            )
        elif quando == 'amanha' or quando == 'amanhã':
            amanha = date.today() + timedelta(days=1)
            print(f"Pegou a viriavel amanha: {amanha}")
            curso.execute(
                '''SELECT * FROM eventos
                WHERE data_evento = ?
                ORDER BY data_evento ASC, materia ASC;''', (amanha,)
            )
        elif quando == "tarefa":
            dia = date.today() + timedelta(days=1)
            print(f"Pegou a viriavel dia: {dia}")
            curso.execute(
                '''SELECT * FROM eventos
                WHERE data_evento >= ?
                ORDER BY data_evento ASC, materia ASC;''', (dia,)
            )
        
        resultados = curso.fetchall()
        print(f"Eventos pegos: {resultados}")
    except Exception as e:
        print(f'Erro no buscar_eventos: {e}')
    finally:
        curso.close()
        conexao.close()
    print('[acabou a função buscar_eventos]')
    return resultados

def editar_bd(texto:str):
    print("[Função editar_bd]")
    infos = [item.strip() for item in texto[6:].split(',')]
    print(f'texto separado: {infos}')

    if len(infos) > 3 and infos[1] not in ('descrição', 'descriçao', 'descricão', 'descricao',):
        print('Muitos argumentos')
        print('[Acabou função editar_bd]')
        return 'muitos_agrs'
    elif len(infos) < 3:
        print('Poucos argumentos')
        print('[Acabou função editar_bd]')
        return 'falta_agrs'

    id_evento = infos[0].strip()
    campo_alvo = infos[1].strip()
    novo_valor = infos[2].strip()
    print(f'id = {id_evento}\nCampo alvo = {campo_alvo}\nNovo valor = {novo_valor}')

    conexao = sqlite3.connect('cronograma.db')
    curso = conexao.cursor()
    curso.execute(
        '''SELECT id FROM eventos
        WHERE id = ?;''', (id_evento,))
    resultado = curso.fetchall()

    if not resultado:
        print('Não foi encontrado o id solicitado')
        conexao.close()
        print('[Acabou função editar_bd]')
        return 'id_invalido'

    if not campo_alvo in ('data_evento', 'data', 'evento_data','evento','materia','matéria','tipo','descrição', 'descriçao', 'descricão', 'descricao',):
        return 'campo_invalido'

    if campo_alvo in ('data_evento', 'data', 'evento_data',):
        formatos = ("%d/%m/%y", "%d/%m/%Y", "%d/%m")
    
        try:
            data_objeto = datetime.strptime(novo_valor, formatos[0])
            print("Data valida")
        except:
            try:
                data_objeto = datetime.strptime(novo_valor, formatos[1])
                print("Data valida")
            except:
                try:
                    data_objeto = datetime.strptime(novo_valor, formatos[2])
                    data_objeto = data_objeto.replace(year=2026)
                    print("Data valida")
                except:
                    print("Data invalida")
                    print('[Acabou função editar_bd]')
                    return 'data_invalido'
        
        curso.execute(
            '''UPDATE eventos SET data_evento = ?
            WHERE id = ?''', (data_objeto.date(), id_evento,))
        conexao.commit()
        conexao.close()
        print('Edição feito com sucesso')
        print('[Acabou função editar_bd]')
        return 'sucesso_data'
    
    if campo_alvo in ('materia','matéria',):
        with open('constantes.json', 'r', encoding='utf-8') as f:
            MATERIAS:dict = json.load(f)
        print('Matérias pegas')
        
        materia_pega = False
        for materia_corretor in MATERIAS.keys():
            if novo_valor in MATERIAS[materia_corretor]:
                materia = materia_corretor
                materia_pega = True
                print(f'A matéria é {materia}')
                break

        if not materia_pega:
            print('Não foi encontrada a matéria desejada')
            print('[Acabou função editar_bd]')
            return 'materia_invalido'
        
        curso.execute(
            '''UPDATE eventos SET materia = ?
            WHERE id = ?''', (materia, id_evento,))
        conexao.commit()
        conexao.close()
        print('Edição feito com sucesso')
        print('[Acabou função editar_bd]')
        return 'sucesso_materia'
    
    if campo_alvo in ('tipo',):
        curso.execute(
            '''UPDATE eventos SET tipo = ?
            WHERE id = ?''', (novo_valor.title(), id_evento,))
        conexao.commit()
        conexao.close()
        print('Edição feito com sucesso')
        print('[Acabou função editar_bd]')
        return 'sucesso_tipo'
    
    if campo_alvo in ('descrição', 'descriçao', 'descricão', 'descricao',):
        print('Entrou no caso de Descrição')
        novo_valor = ', '.join(infos[2:])
        curso.execute(
            '''UPDATE eventos SET descricao = ?
            WHERE id = ?''', (novo_valor, id_evento,))
        conexao.commit()
        conexao.close()
        print('Edição feito com sucesso')
        print('[Acabou função editar_bd]')
        return 'sucesso_descricao'
    print('Se por algum acaso, esse print aparecer, é porque deu um bug')
    print('\033[31mRESOLVA\033[0m')

def comando_deletar(id:str) -> int:
    print("[Função comando_deletar]")
    try:
        conexao = sqlite3.connect("cronograma.db")
        curso = conexao.cursor()

        curso.execute(
            '''DELETE FROM eventos WHERE id = ?''', (id,)
        )

        deletados = curso.rowcount
        conexao.commit()
    except:
        print("Falha ao tentar excluir")
        deletados = -1
    finally:
        curso.close()
        conexao.close()
    print("[Acabou função comando_deletar]")
    return deletados

def eventos_proximo_mes(ano_mes:str):
    print("[Função eventos_proximo_mes]")
    try:
        conexao = sqlite3.connect('cronograma.db')
        print("Conexão feita")
        curso = conexao.cursor()
        curso.execute(
            '''SELECT * FROM eventos WHERE data_evento >= ?''', (ano_mes,)
        )
        eventos = curso.fetchall()
        print(f"SQL retornou: {eventos}")
    except:
        print("Falha ao buscar proximo mês")
        eventos = None
    finally:
        curso.close()
        conexao.close()
    print("[Acabou função eventos_proximo_mes]")
    return eventos

def tarefa(client: NewClient):
    while True:
        agora = datetime.now()
        dia_da_semana = agora.weekday()  # Segunda=0, Sexta=4
        hora_atual = agora.strftime("%H:%M")
        if dia_da_semana == 4 and hora_atual == "14:05":
            amigo = build_jid(os.getenv("AMIGO"))
            with open('emojis_materias.json', 'r', encoding='utf-8') as f:
                materia_emojis = json.load(f)

            eventos_pegos = buscar_eventos("tarefa")
            domingo = datetime.now() + timedelta(days=2)

            mensagem = []
            meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
            if len(eventos_pegos) > 0: # eventos_pegos = (ID, Data, Matéria, Tipo, Descrição)
                
                mensagem.append('📅 CRONOGRAMA DA SEMANA')
                mensagem.append('━━━━━━━━━━━━━━━━━')

                data_antiga = datetime.now() + timedelta(days=1)
                primeira = True
                sabado = domingo + timedelta(days=6)
                proxima_semana = sabado + timedelta(days=1)
                fim_proxima = proxima_semana + timedelta(days=7)
                primeira_barra = False
                for infos in eventos_pegos:
                    parte_mensagem_enviara = []
                    print(f'Informação sendo colocado na resposta: {infos}')

                    data_atual = datetime.strptime(infos[1], "%Y-%m-%d")

                    if data_atual.date() <= sabado.date():
                        if not f'📍 *ESSA SEMANA* ({domingo.strftime("%d/%m")} - {sabado.strftime("%d/%m")}):' in mensagem:
                            mensagem.append(f'📍 *ESSA SEMANA* ({domingo.strftime("%d/%m")} - {sabado.strftime("%d/%m")}):')
                        
                        if primeira or data_atual.date() != data_antiga.date():
                            primeira = False
                            data_antiga = datetime.strptime(data_atual.strftime('%d/%m/%Y'), '%d/%m/%Y')
                            parte_mensagem_enviara.append(f'### {data_atual.strftime("%d/%m")}')


                        parte_mensagem_enviara.append(f'- {infos[3]} - {infos[2]} {materia_emojis[infos[2]]}')

                        mensagem.extend(parte_mensagem_enviara)
                        if infos[4] != 'Vazio':
                            descricao = infos[4].replace('\n', '\n> ')
                            mensagem.append(f'> {descricao}')

                    elif data_atual.date() <= fim_proxima.date():
                        if not f'📍 *PRÓXIMA SEMANA* ({proxima_semana.strftime("%d/%m")} - {fim_proxima.strftime("%d/%m")}):\n' in mensagem:
                            parte_mensagem_enviara.append(f'📍 *PRÓXIMA SEMANA* ({proxima_semana.strftime("%d/%m")} - {fim_proxima.strftime("%d/%m")}):\n')

                        if data_atual.date() != data_antiga.date():
                            primeira = False
                            data_antiga = datetime.strptime(data_atual.strftime('%d/%m/%Y'), '%d/%m/%Y')
                            parte_mensagem_enviara.append(f'### {data_atual.strftime("%d/%m")}')

                        parte_mensagem_enviara.append(f'{materia_emojis[infos[2]]} {infos[3]} - {infos[2]}')

                        mensagem.extend(parte_mensagem_enviara)
                        if infos[4] != 'Vazio':
                            descricao = infos[4].replace('\n', '\n> ')
                            mensagem.append(f'> {descricao}')
                    
                    else:
                        if not primeira_barra:
                            mensagem.append("━━━━━━━━━━━━━━━━━")
                            primeira_barra = True
                        if not f"📅 *{meses[int(data_atual.strftime('%m'))-1]}*" in mensagem:
                            mensagem.append(f"📅 *{meses[int(data_atual.strftime('%m'))-1]}*")
                        
                        parte_mensagem_enviara.append(f'{materia_emojis[infos[2]]} {data_atual.strftime("%d/%m")} {infos[3]} - {infos[2]}')

                        mensagem.extend(parte_mensagem_enviara)
                        if infos[4] != 'Vazio':
                            descricao = infos[4].replace('\n', '\n> ')
                            mensagem.append(f'> {descricao}')

                    mensagem.append('')

            else:
                mensagem.append("Não a nenhum evento programado")

            mensagem_final = '\n'.join(mensagem)

            client.send_message(amigo, mensagem_final+"\n\nPosso enviar?\nSe você quiser mandar uma mensagem no final, escreva assim: sim, [mensagem que você quer]")
            with open("confirmacao.txt", "w", encoding="utf-8") as confirmacao:
                confirmacao.write(f"{datetime.now().strftime('%d/%m/%Y')}")
            with open("cronograma.txt", "w", encoding="utf-8") as cronocrama:
                cronocrama.write(mensagem_final)
            sleep(120)
        sleep(20)

def exclucao_atutomatica():
    while True:
        try:
            conexao = sqlite3.connect('cronograma.db')
            curso = conexao.cursor()
            
            hoje = datetime.now().strftime("%Y-%m-%d")
            
            # O SQLite deleta tudo de uma vez só! (Note a vírgula depois do 'hoje')

            curso.execute(
                '''SELECT * FROM eventos WHERE data_evento < ?''', (hoje,)
            )
            eventos = curso.fetchall()

            resposta = []
            if len(eventos) > 0: # Resultado[1] = (ID, Data, Matéria, Tipo, Descrição)

                data_antiga = ''
                for infos in eventos:
                    parte_mensagem_enviara = []
                    print(f'Informação sendo colocado na resposta: {infos}')

                    data = infos[1]
                    if data_antiga != data:
                        data_antiga = data
                        data_formatada = f'{data[-2:]}/{data[5:7]}'
                        parte_mensagem_enviara.append(f'### *{data_formatada}*')

                    parte_mensagem_enviara.append(f'🆔: {infos[0]}')

                    parte_mensagem_enviara.append(f'- {infos[3]} - {infos[2]}')

                    resposta.extend(parte_mensagem_enviara)
                    if infos[4] != 'Vazio':
                        descricao = infos[4].replace('\n', '\n> ')
                        resposta.append(f'> {descricao}')
                    resposta.append('')

            

            curso.execute(
                '''DELETE FROM eventos WHERE data_evento < ?''', (hoje,)
            )
            
            # Extra: rowcount te diz quantas linhas foram apagadas
            deletados = curso.rowcount 
            print(f"Limpeza do BD: {deletados} eventos antigos foram apagados.")
            
            conexao.commit()
            if deletados > 0:
                logs_deletados = open("logs_deletados.txt", "a")
                resposta_final = '\n'.join(resposta)
                logs_deletados.write(f"{deletados} eventos foram deletados.\n\n{resposta_final}\n\n\n\n\n")
                logs_deletados.close()
        
        except Exception as e:
            print(f"Erro na limpeza do banco: {e}")
            
        finally:
            # O finally garante que a conexão vai fechar mesmo se der erro
            curso.close()
            conexao.close()

        # Dorme por 24 horas
        sleep(86400)
