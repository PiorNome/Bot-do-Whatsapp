import os, sqlite3, json
from datetime import datetime, date, timedelta
from dotenv import load_dotenv
load_dotenv()
def decidir_destino(texto:str, numero_celular:str) -> tuple[str, any]:
    print(f"[Função: decidir_destino]")
    print(f"Recebeu {texto}")
    comandos = ['agendar', 'status', 'hoje', 'amanha', 'tutorial']
    comandos_ajuda = ['ajuda', 'ajudar','h','sos']
    lista_strs = texto.split()
    numeros = os.getenv('ADMINS')
    ADMINS = numeros.split(' , ')
    print(f"Mensagem separada como: {lista_strs}")

    print(f"Comando da mensagem é: {lista_strs[0]}")

    if lista_strs[0] in comandos:
        if lista_strs[0] == 'agendar':
            comando = 'agendar'

            print(f"Entrou como comando agendar")
            retorna = ''
            if not numero_celular in ADMINS:
                print(f"O número {numero_celular} não é ADMIN")
                return (comando, 'sem_permissão')
            print(f"O número {numero_celular} é ADMIN")
            erros = adicionar_bd(texto)
            print(f"Função adicionar_bd retornou: {erros}")

            if erros[0] == -1:
                return (comando, 'falta_agrs')

            for i in erros:
                retorna += str(i)
            print(f"Será retornado: {comando} e {retorna}")
            print("[Acabou a função decidir_destino]")
            return (comando,retorna)
        
        elif lista_strs[0] == 'status' or lista_strs[0] == 'hoje' or lista_strs[0] == 'amanha' or lista_strs[0] == 'amanhã':
            comando = lista_strs[0]
            print(f"O comando usado para ver os eventos foi: \"{comando}\"")
            print("Buscando eventos")
            resultados = buscar_eventos(comando)
            print('Eventos pegos')
            print("[Acabou a função decidir_destino]")
            return (comando,resultados)
        
    elif lista_strs[0] in comandos_ajuda:
        print("[Acabou a função decidir_destino]")
        return ('ajudar', None)
    
    print("[Acabou a função decidir_destino]")
    return ('Najudar', None)

def adicionar_bd(texto:str) -> tuple[int]:
    print(f"[Função: adicionar_bd]")
    
    with open('constantes.json', 'r', encoding='utf-8') as f:
        MATERIAS = json.load(f)

    print("pegou as materias")
    retorna = [0, 0, 0] # se algum for igual a 1, significa que deu erro. Data é o 1º elemento, materia é o 2º elemento e o tipo é o 3º elemento
    
    texto = texto[7:]

    informacoes = texto.split("|")
    print(f"Separou as informações")
    qntd = len(informacoes) # A quantidade de partes que tem
    if qntd >= 3:
        data = informacoes[0].strip()
        materia = informacoes[1].strip()
        tipo = informacoes[2].strip()

        descricao = 'Vazio'
        if qntd > 3:
            descricao = ''
            descricao = "|".join(informacoes[3:]).strip()
            print(f"Adicionou a descrição: {descricao}")
    
        # O bot vai verivicar se a data está certá
        # O bot tenta aceitar tanto 25/04/26 quanto 25/04/2026
        formatos = ("%d/%m/%y", "%d/%m/%Y")
    
        try:
            data_objeto = datetime.strptime(data, formatos[0])
            print("Data valida")
        except:
            try:
                data_objeto = datetime.strptime(data, formatos[1])
                print("Data valida")
            except:
                print("Data invalida")
                retorna[0] = 1
        
        encontrou_materia = False
        for materia_key in MATERIAS.keys():
            if materia in MATERIAS[materia_key]:
                materia = materia_key
                encontrou_materia = True
                print(f"Encontro a matéria: {materia}")
                break
        if not encontrou_materia:
            print("Não encontrou a matéria")
            retorna[1] = 1
        
        if not tipo in ('prova', 'trabalho', 'vazio', 'atividade', 'lição'):
            print("Não encontrou um tipo valido")
            retorna[2] = 1

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
    return [-1]

def buscar_eventos(quando:str='') -> list[tuple]:
    print('[Função buscar_eventos]')
    conexao = sqlite3.connect('cronograma.db')
    print('Conexão feita')
    curso = conexao.cursor()
    
    try:
        if quando == '' or quando == 'status':
            data = date.today()
            print(f"Pegou a viriavel data: {data}")
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
        
        resultados = curso.fetchall()
    except Exception as e:
        print(f'Erro no buscar_eventos: {e}')
    finally:
        conexao.close()
    print('[acabou a função buscar_eventos]')
    return resultados