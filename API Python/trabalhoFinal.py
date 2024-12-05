from pymongo import MongoClient
from bson import ObjectId

# Conexão com o MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["trabalhoFinal"]

def menu_principal():
    while True:
        print("\nMenu Principal:")
        print("1 - Registro de Usuário")
        print("2 - Login Usuário")
        print("3 - Registro de Agente")
        print("4 - Login Agente")
        print("5 - Admin")
        print("Digite qualquer outro valor para sair")
        opcao = input("Sua opção: ")

        if opcao == "1":
            registrar_usuario()
        elif opcao == "2":
            login_usuario()
        elif opcao == "3":
            registrar_agente()
        elif opcao == "4":
            login_agente()
        elif opcao == "5":
            admin_menu()
        else:
            print("Saindo...")
            break

# Funcionalidades de Usuário
def registrar_usuario():
    cpf = input("\nDigite o CPF do usuário: ")
    
    # Verificar se o usuário já está cadastrado
    usuario_existente = db.usuarios.find_one({"cpf": cpf})
    if usuario_existente:
        print("Usuário já cadastrado! Retorne para a tela de login.")
        return

    nome = input("Digite o nome do usuário: ")
    dtnasc = input("Digite a data de nascimento (dd-mm-aaaa): ")
    telefone = input("Digite o telefone: ")
    email = input("Digite o e-mail: ")
    password = input("Digite uma senha: ")

    try:
        db.usuarios.insert_one({
            "cpf": cpf,
            "nome": nome,
            "dtnasc": dtnasc,
            "telefone": telefone,
            "email": email,
            "password": password
        })
        print("Usuário registrado com sucesso!")
    except Exception as e:
        print(f"Erro ao registrar usuário: {e}")

def login_usuario():
    cpf = input("\nDigite seu CPF: ")
    usuario = db.usuarios.find_one({"cpf": cpf})
    if usuario:
        password = input("Digite sua senha: ")
        if usuario["password"] == password:
            print(f"Bem-vindo(a), {usuario['nome']}!")
            menu_usuario(usuario)
        else:
            print("Senha incorreta!")
    else:
        print("Usuário não encontrado.")

def menu_usuario(usuario):
    while True:
        print("\nMenu do Usuário:")
        print("1 - Cadastrar objeto")
        print("2 - Remover objeto")
        print("3 - Lista de objetos")
        print("4 - Registrar ocorrência")
        print("5 - Remover ocorrência")
        print("6 - Lista de ocorrências")
        print("7 - Informações da conta")
        print("8 - Editar conta")
        print("9 - Remover conta")
        print("Digite qualquer outro valor para sair")
        opcao = input("Sua opção: ")

        if opcao == "1":
            cadastrar_objeto(usuario)
        elif opcao == "2":
            remover_objeto(usuario)
        elif opcao == "3":
            listar_objetos(usuario)
        elif opcao == "4":
            registrar_ocorrencia(usuario)
        elif opcao == "5":
            remover_ocorrencia(usuario)
        elif opcao == "6":
            listar_ocorrencias(usuario)
        elif opcao == "7":
            mostrar_informacoes(usuario, "usuario")
        elif opcao == "8":
            editar_conta(usuario, "usuario")
        elif opcao == "9":
            remover_conta(usuario, "usuario")
            break
        else:
            break

def cadastrar_objeto(usuario):
    num_serie = input("\nDigite o número de série do objeto: ")
    
    usuario_existente = db.usuarios.find_one({
        "cpf": usuario["cpf"],
        "objetos.num_serie": num_serie
    })
    if usuario_existente:
        print("Erro: Já existe um objeto com esse número de série!")
        return
    
    marca = input("Digite a marca do objeto: ")
    modelo = input("Digite o modelo do objeto: ")
    cor = input("Digite a cor do objeto: ")
    categoria = input("Digite a categoria do objeto (bicicleta, notebook...): ")
    observacoes = input("Digite as observações do objeto: ")
    try:
        db.usuarios.update_one(
            {"cpf": usuario["cpf"]},
            {"$push": {
                "objetos":{
                "num_serie": num_serie,
                "marca": marca,
                "modelo": modelo,
                "cor": cor,
                "categoria": categoria,
                "observacoes": observacoes
                }
            }}
        )
        print("Objeto cadastrado com sucesso!")
    except Exception as e:
        print(f"Erro ao cadastrar objeto: {e}")

def remover_objeto(usuario):
    listar_objetos(usuario)
    num_serie_remover = input("\nDigite o número de série do objeto que deseja remover: ")

    usuario_existente = db.usuarios.find_one({"cpf": usuario["cpf"]})
        
    if usuario_existente:
        # Busca o objeto com o número de série informado
        objeto_remover = next((obj for obj in usuario_existente.get("objetos", []) if obj["num_serie"] == num_serie_remover), None)
        
        if objeto_remover:
            db.usuarios.update_one(
                {"cpf": usuario["cpf"]},
                {"$pull": {"objetos": {"num_serie": num_serie_remover}}}
            )
            print(f"Objeto com número de série {num_serie_remover} removido com sucesso!")
        else:
            print("Objeto não encontrado com o número de série informado.")
    else:
        print("Usuário não encontrado.")

def listar_objetos(usuario):
    usuario_existente = db.usuarios.find_one({"cpf": usuario["cpf"]})
    
    if usuario_existente:
        objetos = usuario_existente.get("objetos", [])
        
        if objetos:
            print("\nLista de Objetos Cadastrados:")
            for i, objeto in enumerate(objetos, 1):
                print(f"Objeto {i} - \n Número de Série: {objeto['num_serie']} \n Marca: {objeto['marca']} \n Modelo: {objeto['modelo']} \n Cor: {objeto['cor']} \n Categoria: {objeto['categoria']} \n Observações: {objeto['observacoes']}\n")
        else:
            print("Nenhum objeto cadastrado para este usuário.")
    else:
        print("Usuário não encontrado.")

def registrar_ocorrencia(usuario):
    listar_objetos(usuario)
    try:
        num_serie_objeto = input("Digite o número de série do objeto relacionado à ocorrência: ")

        # Verificar se o número de série existe para o usuário
        objeto = db.usuarios.find_one(
            {"cpf": usuario["cpf"], "objetos.num_serie": num_serie_objeto},
            {"objetos.$": 1}
        )

        if not objeto:
            print("Número de série não encontrado para este usuário. Verifique e tente novamente.")
            return

        # Verificar se já existe uma ocorrência registrada para o número de série
        ocorrencia_existente = db.ocorrencias.find_one({"num_serie_objeto": num_serie_objeto})
        if ocorrencia_existente:
            print("Já existe uma ocorrência registrada para este número de série. Não é possível duplicar.")
            return

        # Solicitar informações da ocorrência
        data = input("Digite a data da ocorrência (dd-mm-aaaa): ")
        rua = input("Digite o nome da rua onde ocorreu: ")
        numero = input("Digite o número: ")
        bairro = input("Digite o bairro: ")
        descricao = input("Descreva a ocorrência: ")

        # Inserir a ocorrência no banco de dados
        db.ocorrencias.insert_one({
            "cpf_usuario": usuario["cpf"],
            "num_serie_objeto": num_serie_objeto,
            "data": data,
            "local": {
                "rua": rua,
                "numero": numero,
                "bairro": bairro
            },
            "descricao": descricao,
            "providencias": []
        })

        print("Ocorrência registrada com sucesso!")
    except Exception as e:
        print(f"Erro ao registrar ocorrência: {e}")


def remover_ocorrencia(usuario):
    listar_ocorrencias(usuario)
    try:
        id_ocorrencia = input("\nDigite o ID da ocorrência que deseja remover: ")

        # Converter o ID
        try:
            id_ocorrencia = ObjectId(id_ocorrencia)
        except Exception:
            print("\nID inválido. Certifique-se de que está inserindo um ID correto.")
            return

        # Verificar se o ID da ocorrência é válido e pertence ao usuário
        ocorrencia = db.ocorrencias.find_one({
            "_id": id_ocorrencia,
            "cpf_usuario": usuario["cpf"]
        })

        if ocorrencia:
            print("Solicitação enviada ao Administrador!")
        else:
            print("Ocorrência não encontrada ou não pertence a este usuário.")
    except Exception as e:
        print(f"Erro ao processar a remoção da ocorrência: {e}")

def listar_ocorrencias(usuario):
    try:
        ocorrencias_cursor = db.ocorrencias.find({"cpf_usuario": usuario["cpf"]})

        lista_ocorrencias = list(ocorrencias_cursor)

        if len(lista_ocorrencias) == 0:  # Verifica se não há ocorrências
            print("\nNenhuma ocorrência encontrada para este usuário.")
            return

        print("\nOcorrências registradas:")
        for idx, ocorrencia in enumerate(lista_ocorrencias, start=1):
            print(f"\nOcorrência {idx}:")
            print(f"  ID: {ocorrencia['_id']}")
            print(f"  Número de série do objeto: {ocorrencia.get('num_serie_objeto', 'N/A')}")
            print(f"  Data: {ocorrencia.get('data', 'N/A')}")
            local = ocorrencia.get('local', {})
            print(f"  Endereço: {local.get('rua', 'N/A')}, {local.get('numero', 'N/A')}, {local.get('bairro', 'N/A')},")
            print(f"  Descrição: {ocorrencia.get('descricao', 'N/A')}")
            providencias = ocorrencia.get('providencias', [])
            print(f"  Providências:")
            for prov in providencias:
                print(f"    Agente {prov.get('matricula_agente', 'N/A')}: {prov.get('descricao', 'N/A')}")

    except Exception as e:
        print(f"Erro ao listar ocorrências: {e}")

#Funcionalidade para usuário e agente
def mostrar_informacoes(entidade, tipo):
    try:
        if tipo == "usuario":
            print("\nInformações do Usuário:")
            print(f"  CPF: {entidade['cpf']}")
            print(f"  Nome: {entidade['nome']}")
            print(f"  Data de Nascimento: {entidade['dtnasc']}")
            print(f"  Telefone: {entidade['telefone']}")
            print(f"  Email: {entidade['email']}")
        elif tipo == "agente":
            print("\nInformações do Agente:")
            print(f"  Matrícula: {entidade['matricula']}")
            print(f"  Nome: {entidade['nome']}")
    except Exception as e:
        print(f"Erro ao exibir informações: {e}")

#Funcionalidade para usuário e agente
def editar_conta(entidade, tipo):
    try:
        if tipo == "usuario":
            print("\nEditar Informações do Usuário: (deixe em branco para manter o atual)")
            novo_nome = input("Digite o novo nome: ") or entidade["nome"]
            novo_telefone = input("Digite o novo telefone: ") or entidade["telefone"]
            novo_email = input("Digite o novo email: ") or entidade["email"]

            db.usuarios.update_one(
                {"cpf": entidade["cpf"]},
                {"$set": {
                    "nome": novo_nome,
                    "telefone": novo_telefone,
                    "email": novo_email
                }}
            )
            print("Informações atualizadas com sucesso!")
        elif tipo == "agente":
            print("\nEditar Informações do Agente: (deixe em branco para manter o atual)")
            novo_nome = input("Digite o novo nome: ") or entidade["nome"]
            nova_password = input("Digite a nova senha: ") or entidade["password"]

            db.agentes.update_one(
                {"matricula": entidade["matricula"]},
                {"$set": {
                    "nome": novo_nome,
                    "password": nova_password
                }}
            )
            print("Informações atualizadas com sucesso!")
    except Exception as e:
        print(f"Erro ao editar informações: {e}")

#Funcionalidade para usuário e agente
def remover_conta(entidade, tipo):
    try:
        confirmacao = input("\nTem certeza que deseja remover sua conta? (s/n): ").lower()
        if confirmacao == "s":
            if tipo == "usuario":
                db.usuarios.delete_one({"cpf": entidade["cpf"]})
                print("Conta de usuário removida com sucesso!")
            elif tipo == "agente":
                db.agentes.delete_one({"matricula": entidade["matricula"]})
                print("Conta de agente removida com sucesso!")
        else:
            print("Operação cancelada.")
    except Exception as e:
        print(f"Erro ao remover conta: {e}")

#Funcionalidades de Agente
def registrar_agente():
    matricula = input("\nDigite a matrícula do agente: ")
    
    # Verificar se o agente já está cadastrado
    usuario_existente = db.agentes.find_one({"matricula": matricula})
    if usuario_existente:
        print("Agente já cadastrado! Retorne para a tela de login.")
        return
    
    nome = input("Digite o nome do agente: ")
    password = input("Digite uma senha de acesso: ")
    
    try:
        db.agentes.insert_one({
            "matricula": matricula,
            "nome": nome,
            "password": password
        })
        print("Agente registrado com sucesso!")
    except Exception as e:
        print(f"Erro ao registrar agente: {e}")

def login_agente():
    matricula = input("\nDigite sua matrícula: ")
    agente = db.agentes.find_one({"matricula": matricula})
    if agente:
        password = input("Digite sua senha: ")
        if agente["password"] == password:
            print(f"Bem-vindo(a), {agente['nome']}!")
            menu_agente(agente)
        else:
            print("Senha incorreta!")
    else:
        print("Agente não encontrado.")

def menu_agente(agente):
    while True:
        print("\nMenu de Agente:")
        print("1 - Lista de ocorrências")
        print("2 - Atender ocorrência")
        print("3 - Minhas ocorrências")
        print("4 - Atualizar providências de ocorrências")
        print("5 - Informações da conta")
        print("6 - Editar conta")
        print("7 - Remover conta")
        print("Digite qualquer outro valor para sair")
        opcao = input("Sua opção: ")

        if opcao == "1":
            listar_todas_ocorrencias()
        elif opcao == "2":
            atender_ocorrencia(agente)
        elif opcao == "3":
            listar_ocorrencias_agente(agente)
        elif opcao == "4":
            atualizar_providencias_ocorrencia(agente)
        elif opcao == "5":
            mostrar_informacoes(agente, "agente")
        elif opcao == "6":
            editar_conta(agente, "agente")
        elif opcao == "7":
            remover_conta(agente, "agente")
            break
        else:
            print("Saindo do menu do agente.")
            break

def listar_todas_ocorrencias():
    try:
        ocorrencias = db.ocorrencias.find()
        for ocorrencia in ocorrencias:
            print(f"\nID: {ocorrencia['_id']}")
            print(f"CPF do Usuário: {ocorrencia['cpf_usuario']}")
            print(f"Número de Série do Objeto: {ocorrencia['num_serie_objeto']}")
            print(f"Data: {ocorrencia['data']}")
            print(f"Local: {ocorrencia['local']['rua']}, Número {ocorrencia['local']['numero']}, Bairro {ocorrencia['local']['bairro']}")
            print(f"Descrição: {ocorrencia['descricao']}")
            
            providencias = ocorrencia.get('providencias', [])
            if providencias:
                print("Providências:")
                for idx, providencia in enumerate(providencias, start=1):
                    print(f"  {idx}. Matrícula Agente: {providencia['matricula_agente']}")
                    print(f"     Descrição: {providencia['descricao']}")
            else:
                print("Providências: Nenhuma providência registrada")
            
            print("-" * 30)
    except Exception as e:
        print(f"Erro ao listar ocorrências: {e}")

def atender_ocorrencia(agente):
    listar_todas_ocorrencias()
    id_ocorrencia = input("\nDigite o ID da ocorrência que deseja atender: ")
    
    try:
        #Verificar e converter o ID fornecido para ObjectId
        if not ObjectId.is_valid(id_ocorrencia):
            print("ID inválido. Certifique-se de que está inserindo um ID correto.")
            return
        
        id_ocorrencia = ObjectId(id_ocorrencia)
        ocorrencia = db.ocorrencias.find_one({"_id": id_ocorrencia})
        
        if not ocorrencia:
            print("Ocorrência não encontrada.")
            return
        
        descricao_providencia = input("Digite a descrição da providência: ")
        db.ocorrencias.update_one(
            {"_id": id_ocorrencia},
            {"$push": {"providencias": {"matricula_agente": agente["matricula"], "descricao": descricao_providencia}}}
        )
        
        print("Providência adicionada com sucesso!")
    
    except Exception as e:
        print(f"Erro ao atender ocorrência: {e}")

def listar_ocorrencias_agente(agente):
    try:
        ocorrencias = db.ocorrencias.find({"providencias.matricula_agente": agente["matricula"]})
        for ocorrencia in ocorrencias:
            print(f"\nID: {ocorrencia['_id']}")
            print(f"CPF do Usuário: {ocorrencia['cpf_usuario']}")
            print(f"Número de Série do Objeto: {ocorrencia['num_serie_objeto']}")
            print(f"Data: {ocorrencia['data']}")
            print(f"Local: Rua {ocorrencia['local']['rua']}, Número {ocorrencia['local']['numero']}, Bairro {ocorrencia['local']['bairro']}")
            print(f"Descrição: {ocorrencia['descricao']}")

            providencias = ocorrencia.get('providencias', [])
            if providencias:
                print("Providências:")
                for idx, providencia in enumerate(providencias, start=1):
                    print(f"  {idx}. Agente Matrícula: {providencia['matricula_agente']}")
                    print(f"     Descrição: {providencia['descricao']}")
            else:
                print("Providências: Nenhuma providência registrada")
            
            print("-" * 30)
    except Exception as e:
        print(f"Erro ao listar ocorrências do agente: {e}")

def atualizar_providencias_ocorrencia(agente):
    listar_ocorrencias_agente(agente)
    id_ocorrencia = input("\nDigite o ID da ocorrência que deseja atualizar: ")
    try:
        #Verificar e converter o ID fornecido para ObjectId
        if not ObjectId.is_valid(id_ocorrencia):
            print("ID inválido. Certifique-se de que está inserindo um ID correto.")
            return
        
        id_ocorrencia = ObjectId(id_ocorrencia)
        ocorrencia = db.ocorrencias.find_one({"_id": id_ocorrencia})
        
        if not ocorrencia:
            print("Ocorrência não encontrada ou você não tem autorização para atualizar esta ocorrência.")
            return
        
        nova_descricao = input("Digite a nova descrição para a providência: ")
        db.ocorrencias.update_one(
            {"_id": id_ocorrencia, "providencias.matricula_agente": agente["matricula"]},
            {"$set": {"providencias.$.descricao": nova_descricao}}
        )
        print("Providência atualizada com sucesso!")
    except Exception as e:
        print(f"Erro ao atualizar providências: {e}")

def admin_menu():
    while True:
        print("\nMenu de Admin:")
        print("1 - Relatório de Usuários e seus Objetos")
        print("2 - Relatório de Agentes e suas Ocorrências")
        print("3 - Relatório de Usuários e suas Ocorrências")
        print("Digite qualquer outro valor para sair")
        opcao = input("Sua opção: ")

        if opcao == "1":
            relatorio_usuarios_objetos()
        elif opcao == "2":
            relatorio_agentes_ocorrencias()
        elif opcao == "3":
            relatorio_ocorrencias_por_usuarios()
        else:
            print("Saindo do menu de Admin.")
            break


def relatorio_usuarios_objetos():
    try:
        usuarios = db.usuarios.find()
        print("\nRelatório de Usuários e seus Objetos:")
        for usuario in usuarios:
            print(f"CPF: {usuario['cpf']}")
            print(f"Nome: {usuario['nome']}")
            print("Objetos:")
            objetos = usuario.get("objetos", [])
            if objetos:
                for obj in objetos:
                    print(f"  - Número de Série: {obj['num_serie']}, Marca: {obj['marca']}, Modelo: {obj['modelo']}")
            else:
                print("  Nenhum objeto cadastrado.")
            print("-" * 30)
    except Exception as e:
        print(f"Erro ao gerar relatório de usuários e objetos: {e}")


def relatorio_agentes_ocorrencias():
    try:
        agentes = db.agentes.find()
        print("\nRelatório de Agentes e suas Ocorrências:")
        for agente in agentes:
            print(f"Matrícula: {agente['matricula']}")
            print(f"Nome: {agente['nome']}")
            print("Ocorrências atendidas:")
            
            ocorrencias = db.ocorrencias.find({"providencias.matricula_agente": agente["matricula"]})
            ocorrencias_list = list(ocorrencias)
                        
            if ocorrencias_list:  # Verifica se existem ocorrências
                for ocorrencia in ocorrencias_list:
                    print(f"  - ID da Ocorrência: {ocorrencia['_id']}")
                    print(f"    Data: {ocorrencia['data']}")
                    print(f"    Descrição: {ocorrencia['descricao']}")
                    print(f"    Local: Rua {ocorrencia['local']['rua']}, Número {ocorrencia['local']['numero']}, Bairro {ocorrencia['local']['bairro']}")
                    print("    Providências do Agente:")
                    
                    providencias_agente = [
                        p for p in ocorrencia['providencias']
                        if p['matricula_agente'] == agente["matricula"]
                    ]
                    
                    if providencias_agente:
                        for providencia in providencias_agente:
                            print(f"      - {providencia['descricao']}")
                    else:
                        print("      Nenhuma providência registrada.")
            else:
                print("  Nenhuma ocorrência atendida.")
            print("-" * 30)
    except Exception as e:
        print(f"Erro ao gerar relatório de agentes e ocorrências: {e}")

def relatorio_ocorrencias_por_usuarios():
    try:
        # Agrupar ocorrências por CPF e buscar no banco
        usuarios_ocorrencias = {}
        ocorrencias = db.ocorrencias.find()

        # Organiza as ocorrências por CPF de usuário, sem duplicações
        for ocorrencia in ocorrencias:
            cpf_usuario = ocorrencia['cpf_usuario']
            if cpf_usuario not in usuarios_ocorrencias:
                usuarios_ocorrencias[cpf_usuario] = {
                    'nome': db.usuarios.find_one({"cpf": cpf_usuario})["nome"],
                    'ocorrencias': []
                }
            # Adiciona a ocorrência apenas se não for duplicada
            if ocorrencia not in usuarios_ocorrencias[cpf_usuario]['ocorrencias']:
                usuarios_ocorrencias[cpf_usuario]['ocorrencias'].append(ocorrencia)

        print("\nRelatório das Ocorrências de Usuários:")
        
        # Exibe as ocorrências agrupadas por usuário
        for cpf_usuario, data in usuarios_ocorrencias.items():
            print(f"\nUsuário: {data['nome']} (CPF: {cpf_usuario})")
            for i, ocorrencia in enumerate(data['ocorrencias'], start=1):
                print(f"Ocorrência {i} -")
                print(f"  ID: {ocorrencia['_id']}")
                print(f"  Número de Série do Objeto: {ocorrencia['num_serie_objeto']}")
                
                # Buscando o objeto
                usuario = db.usuarios.find_one({"cpf": cpf_usuario})
                objeto = None
                if usuario:
                    for obj in usuario.get("objetos", []):
                        if obj['num_serie'] == ocorrencia['num_serie_objeto']:
                            objeto = obj
                            break
                        
                if objeto:
                    print(f"  Objeto: {objeto.get('categoria', 'Desconhecido')}, {objeto.get('marca', 'Desconhecida')}, {objeto.get('modelo', 'Desconhecido')}, {objeto.get('cor', 'Desconhecida')}")
                else:
                    print(f"  Objeto: Não encontrado no banco de dados.")
                                   
                print(f"  Data: {ocorrencia['data']}")
                print(f"  Local: {ocorrencia['local']['rua']}, Número {ocorrencia['local']['numero']}, Bairro {ocorrencia['local']['bairro']}")
                print(f"  Descrição: {ocorrencia['descricao']}")
                
                # Verifica e exibe as providências
                providencias = ocorrencia.get("providencias", [])
                print("  Providências:")
                if providencias:
                    for providencia in providencias:
                        print(f"    - Agente: {providencia['matricula_agente']}, Descrição: {providencia['descricao']}")
                else:
                    print("    Nenhuma providência registrada.")
                
            print("-" * 30)

    except Exception as e:
        print(f"Erro ao gerar relatório de ocorrências de usuários: {e}")

if __name__ == "__main__":
    menu_principal()