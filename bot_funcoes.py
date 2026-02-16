def decidir_destino(texto:str) -> str:
    comandos = ['agendar']
    comandos_ajuda = ['ajuda','h','sos']
    lista_strs = texto.split()
    if lista_strs[0].lower() in comandos:
        return 'sucesso'
    if lista_strs[0].lower() in comandos_ajuda:
        return 'ajudar'
    return 'Najudar'

def adicionar_bd(lista:list[str]) -> str:
    pass