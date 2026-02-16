import os, sqlite3

def decidir_destino(texto:str, numero:str) -> str:
    comandos = ['agendar']
    comandos_ajuda = ['ajuda','h','sos']
    lista_strs = texto.split()
    ADMINS = os.getenv('ADMINS')

    if lista_strs[0].lower() in comandos:
        return 'sucesso'
    if lista_strs[0].lower() in comandos_ajuda:
        return 'ajudar'
    return 'Najudar'

def adicionar_bd(lista:list[str]) -> str:
    MATERIAS = os.getenv('MATERIAS')