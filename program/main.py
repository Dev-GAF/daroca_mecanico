import pyodbc
import pandas as pd
from datetime import datetime, timedelta
import os

def umTexto (solicitacao, mensagem, valido):
    digitouDireito=False
    while not digitouDireito:
        txt=input(solicitacao)

        if txt not in valido:
            print(mensagem,'- Favor redigitar...')
        else:
            digitouDireito=True

    return txt

def opcaoEscolhida (mnu):
    print ()

    opcoesValidas=[]
    posicao=0
    while posicao<len(mnu):
        print (posicao+1,') ',mnu[posicao],sep='')
        opcoesValidas.append(str(posicao+1))
        posicao+=1

    print()
    return umTexto('Qual é a sua opção? ', 'Opção inválida', opcoesValidas)

def connect():
    
    try:
        global connection
        connection = pyodbc.connect(
            driver = "{SQL Server}", #fabricante
            server = "regulus.cotuca.unicamp.br", #maquina onde esta o banco de dados
            database = "BD24551", #banco de dados
            uid = "BD24551", #LOGIN
            pwd = "BD24551" #SENHA
        ) # xxxxx é seu RA
        return True
    except:
        return False

def esta_cadastrado_OrdemServico (numeroOrdemServico):
    # cursor e um objeto que permite que 
    #nosso programa executre comandos SQL
    #la no sevidor
    cursor = connection.cursor()
    
    command = f"SELECT * FROM daRoca.OrdemServico WHERE numeroOrdemServico = {numeroOrdemServico}"
     
    try:
        #tentar executar o comando no banco de dados
        cursor.execute(command)
        #como select não altera nada no BD, não faz sentido pensar
        #em aplicar as alterações; por isso não tem cursor.commit()
        dados_selecionados=cursor.fetchall() #fetchall da uma listona
                                             #contendo 0 ou mais listinhas;
                                             #cada listinha seria uma linha
                                             #trazida pelo select;
                                             #neste caso, dará uma listona
                                             #contendo 0 ou 1 listinha(s);
                                             #isso pq ou nao tem o nome
                                             #procurado, ou tem 1 só vez
        return [True,dados_selecionados]
    except:
        #em caso de erro ele vai retornar falso 
        return [False,[]]
    
def escolherCentro():
    print("\n[1]. Campinas")
    print("[2]. Ribeirão Preto")      
    print("[3]. São Paulo")
    while True:
        try:
            centro = int(input("\nDigite o centro que deseja realizar o serviço: "))
        
            if centro == 1:
                print("Você esta designando uma Ordem de Serviço para Campinas.")
                break
            elif centro == 2:
                print("Você esta designando uma Ordem de Serviço para Ribeirão Preto")
                break
            elif centro == 3:
                print("Você esta designado uma Ordem de Serviço para São Paulo")
                break
            else:
                print("Erro! Digite somente opções de 1 a 3!")
        except ValueError:
            print("Erro! Digite somente números!")
            
    return centro

def atribuirServico():
    global atribuicoes  
    
    digitouDireito = False
    while not digitouDireito:
        while True:
            try:
                cursor = connection.cursor()
                mecanico_id = int(input("\nDigite o ID do mecânico: "))
                
                command = f"SELECT * FROM daRoca.Mecanico WHERE codigoMecanico = '{mecanico_id}'"
    
                cursor.execute(command)
                result = cursor.fetchone()
                
                if result is None:
                    print("Mecânico Não Encontrado.")
                    return
                else:
                    print("Mecânico Encontrado/a")
                    digitouDireito = True
                    break
            except ValueError:
                print("Por favor, digite um ID de mecânico válido.")
            
    centro_mecanico = result[1]
    centro_desejado = escolherCentro()
    
    if centro_mecanico != centro_desejado:
        print("Não foi possível atribuir o serviço a esse mecânico, pois ele não pertence ao centro desejado.")
        return 
    else:
        print("Centro atribuído com sucesso.")
        
    if mecanico_id not in mecanico_horas:
        mecanico_horas[mecanico_id] = 0
        
        atribuicoes.append({
            'Mecânico': result[2],
            'Tempo acumulado': '0',
            'Hora de serviço': '08h00 - 08h15',
            'Descrição': 'Análise de ordem de serviço'
        })

    if mecanico_horas[mecanico_id] >= 10:
        print("Este mecânico já possui 10 horas de serviço atribuídas.")
        return
    
    cursor.execute("SELECT numeroOrdemServico, tipoManutencao FROM daRoca.OrdemServico WHERE statuss = 'APROG'")
    ordens_servico = cursor.fetchall()
    
    if not ordens_servico:
        print("\nNão há ordens de serviço disponíveis.")
        return
    
    corretivas = [os for os in ordens_servico if os[1] == 'Manutenção corretiva'] 
    preventivas = [os for os in ordens_servico if os[1] == 'Manutenção preventiva']
    
    ordens_servico = corretivas + preventivas
    
    if ordens_servico == 0:
        print("Nenhuma ordem de serviço disponível!")
        return
    else:
        print("\nOrdens de Serviço disponíveis:")
    for os in ordens_servico:
        print(f"Ordem de Serviço: {os[0]}, Tipo de Manutenção: {os[1]}")
    while True:
        try:
            numero_ordem_servico = int(input("\nDigite o número da Ordem de Serviço que deseja atribuir: "))
            break
        except ValueError:
            print("Erro! Digite somente números!")
    
    ordem = next((os for os in ordens_servico if os[0] == numero_ordem_servico), None)
    if ordem is None:
        print("Ordem de Serviço não encontrada.")
        return
    
    tipo_manutencao = ordem[1]
    if tipo_manutencao == "Manutenção corretiva":
        horas_servico = 2
    elif tipo_manutencao == "Manutenção preventiva":
        if mecanico_horas[mecanico_id] + 1.5 <= 10:
            horas_servico = 1.5
        elif mecanico_horas[mecanico_id] + 1 <= 10:
            horas_servico = 1
        else:
            print("Não é possível atribuir essa ordem de serviço, pois excederia o limite de 10 horas.")
            return
    
    
    if 3 <= mecanico_horas[mecanico_id] < 5 and (mecanico_horas[mecanico_id] + horas_servico) >= 5:
        atribuicoes.append({
            'Mecânico': result[2],
            'Tempo acumulado': f"{mecanico_horas[mecanico_id]} e {mecanico_horas[mecanico_id] + 1}",
            'Hora de serviço': f"{(datetime(1900, 1, 1, 8) + timedelta(hours=mecanico_horas[mecanico_id])).strftime('%Hh%M')} - {(datetime(1900, 1, 1, 8) + timedelta(hours=mecanico_horas[mecanico_id] + 1)).strftime('%Hh%M')}",
            'Descrição': 'Almoço'
        })
        mecanico_horas[mecanico_id] += 1  # adicionar 1 hora para almoço
    
    
    inicio_servico = timedelta(hours=8) + timedelta(hours=mecanico_horas[mecanico_id])
    fim_servico = inicio_servico + timedelta(hours=horas_servico)
    
    if (datetime(1900, 1, 1) + fim_servico).hour > 18:
        print("Não é possível atribuir essa ordem de serviço, pois excederia o limite de horário do mecânico (até as 18h).")
        return
    
    
    atribuicoes.append({
        'Mecânico': result[2],
        'Tempo acumulado': f"{mecanico_horas[mecanico_id]} e {mecanico_horas[mecanico_id] + horas_servico - 1}" if horas_servico > 1 else str(mecanico_horas[mecanico_id]),
        'Hora de serviço': f"{(datetime(1900, 1, 1) + inicio_servico).strftime('%Hh%M')} - {(datetime(1900, 1, 1) + fim_servico).strftime('%Hh%M')}",
        'Descrição': f'#{numero_ordem_servico} - {tipo_manutencao}'
    })
    mecanico_horas[mecanico_id] += horas_servico
    
    cursor.execute("INSERT INTO daRoca.AtribuicaoServico (codigoMecanico, numeroOrdemServico) VALUES (?, ?)", (mecanico_id, numero_ordem_servico))
    cursor.execute(f"UPDATE daRoca.OrdemServico SET statuss = 'atribuida' WHERE numeroOrdemServico = {numero_ordem_servico}")
    connection.commit()
    print("Serviço atribuído com sucesso.")
    
    exportarParaExcel()
    
def exportarParaExcel():
    
    global atribuicoes

    df_atribuicoes = pd.DataFrame(atribuicoes)

    nome_arquivo_excel = 'atribuicoes_ordem_de_servico.xlsx'

    try:
        df_atribuicoes.to_excel(nome_arquivo_excel, index=False)
        print(f'Dados exportados com sucesso para {nome_arquivo_excel}')
    except Exception as e:
        print(f'Erro ao exportar para Excel: {e}')
        
def excluirServicoMecanico():
    digitouDireito = False
    while not digitouDireito:
        while True:
            try:
                numeroOrdemServico = int(input("\nDigite o código da Ordem de serviço: "))
                break
            except ValueError:
                print("Erro! Digite somente números naturais!")
        
        resposta = esta_cadastrado_OrdemServico(numeroOrdemServico)
        sucessoNoAcessoAoBD = resposta[0]
        dados_selecionados = resposta[1]

        if not sucessoNoAcessoAoBD or not dados_selecionados:
            while True:
                print('Ordem de serviço inexistente...\n')
                print("(1) - Reescrever Ordem de Serviço")
                print("(2) - Voltar ao menu")
                try:
                    opcao = int(input("\nO Que Deseja Realizar: "))
                    if opcao == 1:
                        return excluirOrdemDeServico()
                    elif opcao == 2:
                        return  
                    else:
                        print("Opção inválida. Por favor, escolha uma opção válida.")
                except ValueError:
                    print("Digite somente opções 1 ou 2!")
        else:
            digitouDireito = True

        print("Ordem de Serviço:", dados_selecionados[0][0])
        print()

        resposta = umTexto('Deseja realmente excluir? ', 'Você deve digitar S ou N', ['s', 'S', 'n', 'N'])
        
        if resposta in ['s', 'S']:
            try:
                cursor = connection.cursor()
                
                command = "DELETE FROM daRoca.AtribuicaoServico WHERE numeroOrdemServico = ?"
                cursor.execute(command, (numeroOrdemServico,))
                connection.commit()
                print('Remoção de Atribuição de Serviço realizada com sucesso!')
                
                command = "DELETE FROM daRoca.OrdemServico WHERE numeroOrdemServico = ?"
                cursor.execute(command, (numeroOrdemServico,))
                connection.commit()
                print('Remoção de Ordem de Serviço realizada com sucesso!')
                
            except Exception as e:
                print("Remoção mal sucedida!", e)
        else:
            print('Remoção não realizada!')
        
def incluirServicoMecanico():
    opcoes = ['Atribuir',\
              'Excluir',\
              'Voltar']
    
    opcao = 7
    while opcao != 3:
        opcao = opcaoEscolhida(opcoes)
        if opcao == '1':
            atribuirServico()
        elif opcao == '2':
            excluirServicoMecanico()
        elif opcao == '3':
            break
        
    return menu

def incluirOrdemDeServico():
    digitouDireito = False
    while not digitouDireito:
        while True:
            try:
                numeroOrdemServico = int(input("\nDigite o código da Ordem de serviço: "))
                break
            except ValueError:
                print("Erro! Digite somente números naturais!")
        resposta = esta_cadastrado_OrdemServico(numeroOrdemServico)
        sucessoNoAcessoAoBD = resposta[0]
        dados_selecionados = resposta[1]

        if not sucessoNoAcessoAoBD or dados_selecionados:
            print('Ordem de Serviço já existente - Favor redigitar...')
        elif numeroOrdemServico <= -1:
            print("Erro! Digite um código de 0 para cima!")
        else:
            digitouDireito = True

            codigoVeiculo = input("Digite o código do veículo: ")
            tipoManutencao = input("Digite o tipo de manutenção: ")
            criadaNoDia = input("Digite a data de criação (AAAA-MM-DD): ")
            criadaNaHora = input("Digite a hora de criação (HH:MM:SS): ")
            tempoEstimado = input("Digite o tempo estimado: ")
            statuss = input("Digite o status: ")

            try:
                cursor = connection.cursor()

                command = """
                    INSERT INTO daRoca.OrdemServico 
                    (numeroOrdemServico, codigoVeiculo, tipoManutencao, criadaNoDia, criadaNaHora, tempoEstimado, statuss) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """
                cursor.execute(command, (numeroOrdemServico, codigoVeiculo, tipoManutencao, criadaNoDia, criadaNaHora, tempoEstimado, statuss))
                
                connection.commit()
                print("Cadastro realizado com sucesso!")
            except Exception as e:
                print("\nCadastro mal sucedido!", e)
                
def procurarOrdemServico():
    digitouDireito = False
    while not digitouDireito:
        numeroOrdemServico = input('\nDigite o código da Ordem de serviço...: ')
        resposta = esta_cadastrado_OrdemServico(numeroOrdemServico)
        sucessoNoAcessoAoBD = resposta[0]
        dados_selecionados = resposta[1]
                   
        if sucessoNoAcessoAoBD and dados_selecionados:
            print('Encontrada')
            print('Esses são os dados disponíveis:\n')
            print("Código Veículo...:", dados_selecionados[0][1])
            print("Tipo Manutenção...:", dados_selecionados[0][2])
            print("Criada no Dia...:", dados_selecionados[0][3])
            print("Criada na Hora...:", dados_selecionados[0][4])
            print("Tempo Estimado...:", dados_selecionados[0][5])
            print("Status...", dados_selecionados[0][6])
            return
        else: 
            print('Ordem de Serviço não cadastrada!')
            while True:
                print("1 - Incluir Ordem de Serviço")
                print("2 - Reescrever")    
                print("3 - Voltar ao menu")
                try:
                    opcao = int(input("\nO Que Deseja Realizar: "))
                    
                    if opcao == 1:
                        incluirOrdemDeServico()
                        break
                    elif opcao == 2:
                        break
                    elif opcao == 3:
                        return  
                    else:
                        print("Opção inválida. Por favor, escolha uma opção válida.")
                except ValueError:
                    print("Digite somente opções de 1 a 3!")

def atualizarOrdemDeServico():
    while True:
        try:
            numeroOrdemServico = int(input("\nDigite o código da Ordem de serviço: "))
            break
        except ValueError:
            print("Erro! Digite somente números naturais!")
    
    resposta = esta_cadastrado_OrdemServico(numeroOrdemServico)
    sucessoNoAcessoAoBD = resposta[0]
    dados_selecionados = resposta[1]

    if not sucessoNoAcessoAoBD or not dados_selecionados:
        print("Ordem de serviço não cadastrada!\n")
        while True:
            print("1 - Incluir Ordem Serviço")
            print("2 - Reescrever")
            print("3 - Voltar ao Menu")
            o = input("\nO Que Deseja Realizar: ")
            if o == "1":
                incluirOrdemDeServico()
                return
            elif o == "2":
                break
            elif o == "3":
                return

    campos_disponiveis = {
        '1': 'codigoVeiculo',
        '2': 'tipoManutencao',
        '3': 'criadaNoDia',
        '4': 'criadaNaHora',
        '5': 'tempoEstimado',
        '6': 'statuss'
    }
    #Usamos chatGPT aqui:
    print("Campos disponíveis para atualização:\n")
    for k, v in campos_disponiveis.items():
        print(f"{k}) {v}")
    print("7) Finalizar")

    campo = input("\nDigite um Campo (1 a 7): ")
    if campo == '7':
        return
    
    if campo in campos_disponiveis:
        novo_valor = input(f"Digite o novo valor para {campos_disponiveis[campo]}: ")
        
        try:
            cursor = connection.cursor()
            
            command = f"UPDATE daRoca.OrdemServico SET {campos_disponiveis[campo]} = ? WHERE numeroOrdemServico = ?"
            cursor.execute(command, (novo_valor, numeroOrdemServico))
            connection.commit()

            print("\nAtualização realizada com sucesso!")
        except Exception as e:
            print("\nErro ao atualizar Ordem de Serviço:", e)
    else:
        print("Campo inválido!")

def listarOrdemDeServico():
    cursor = connection.cursor()
    command = "SELECT * FROM daRoca.OrdemServico"
    try:
        cursor.execute(command)
        dados_selecionados = cursor.fetchall()
        if dados_selecionados:
            print("\nEssas são todas as Ordens de Serviço encontradas cadastradas:")
            for i in range(len(dados_selecionados)):
                print()
                print(f"Ordem Serviço...:{dados_selecionados[i][0]}")
                print(f"Código Veículo...:{dados_selecionados[i][1]}")
                print(f"Tipo Manutenção...:{dados_selecionados[i][2]}")
                print(f"Criada no Dia...:{dados_selecionados[i][3]}")
                print(f"Criada na Hora...:{dados_selecionados[i][4]}")
                print(f"Tempo estimado...:{dados_selecionados[i][5]}")
                print(f"Status...:{dados_selecionados[i][6]}")
                
        else:
            print("Não há Ordens de Serviço cadastradas")
    except Exception as e:
        print("Erro ao listar Ordens de Serviço:", e)

def excluirOrdemDeServico():
    digitouDireito = False
    while not digitouDireito:
        while True:
            try:
                numeroOrdemServico = int(input("\nDigite o código da Ordem de serviço: "))
                break
            except ValueError:
                print("Erro! Digite somente números naturais!")
        
        resposta = esta_cadastrado_OrdemServico(numeroOrdemServico)
        sucessoNoAcessoAoBD = resposta[0]
        dados_selecionados = resposta[1]

        if not sucessoNoAcessoAoBD or not dados_selecionados:
            while True:
                print('Ordem de serviço inexistente...\n')
                print("(1) - Reescrever Ordem de Serviço")
                print("(2) - Voltar ao menu")
                try:
                    opcao = int(input("\nO Que Deseja Realizar: "))
                    if opcao == 1:
                        return excluirOrdemDeServico()
                    elif opcao == 2:
                        return  
                    else:
                        print("Opção inválida. Por favor, escolha uma opção válida.")
                except ValueError:
                    print("Digite somente opções 1 ou 2!")
        else:
            digitouDireito = True

        print("Ordem de Serviço:", dados_selecionados[0][0])
        print()

        resposta = umTexto('Deseja realmente excluir? ', 'Você deve digitar S ou N', ['s', 'S', 'n', 'N'])

    if resposta in ['s', 'S']:
        try:
            cursor = connection.cursor()
            command = "DELETE FROM daRoca.OrdemServico WHERE numeroOrdemServico = ?"
            cursor.execute(command, (numeroOrdemServico,))
            connection.commit()
            print('Remoção realizada com sucesso!')
        except Exception as e:
            print("Remoção mal sucedida!", e)
    else:
        print('Remoção não realizada!')

def ordemDeServico():
    
    escolherCentro()
    
    opcoes = ['Incluir',\
              'Procurar',\
              'Atualizar',\
              'Listar',\
              'Excluir',\
              'Voltar']
    
    opcao = 7
    while opcao != 6:
        opcao = opcaoEscolhida(opcoes)
        if opcao == '1':
            incluirOrdemDeServico()
        elif opcao == '2':
            procurarOrdemServico()
        elif opcao == '3':
            atualizarOrdemDeServico()
        elif opcao == '4':
            listarOrdemDeServico()
        elif opcao == '5':
            excluirOrdemDeServico()
        elif opcao == '6':
            break
        
    return menu

def esta_cadastrado_mecanico (codigoMecanico):
    # cursor e um objeto que permite que 
    #nosso programa executre comandos SQL
    #la no sevidor
    cursor = connection.cursor()
    
    command = f"SELECT * FROM daRoca.Mecanico WHERE codigoMecanico = {codigoMecanico}"
     
    try:
        #tentar executar o comando no banco de dados
        cursor.execute(command)
        #como select não altera nada no BD, não faz sentido pensar
        #em aplicar as alterações; por isso não tem cursor.commit()
        dados_selecionados=cursor.fetchall() #fetchall da uma listona
                                             #contendo 0 ou mais listinhas;
                                             #cada listinha seria uma linha
                                             #trazida pelo select;
                                             #neste caso, dará uma listona
                                             #contendo 0 ou 1 listinha(s);
                                             #isso pq ou nao tem o nome
                                             #procurado, ou tem 1 só vez
        return [True,dados_selecionados]
    except:
        #em caso de erro ele vai retornar falso 
        return [False,[]]

def incluirMecanico():
    digitouDireito = False
    while not digitouDireito:
        while True:
            try:
                codigoMecanico = int(input('\nCódigo.....: '))
                if codigoMecanico <= -1:
                    print("Erro! Digite um número maior ou igual a 0!")
                    return incluirMecanico()
                break
            except ValueError:
                print("Erro! Digite somente um número natural!")

        resposta = esta_cadastrado_mecanico(codigoMecanico)
        sucessoNoAcessoAoBD = resposta[0]
        dados_selecionados = resposta[1]

        if not sucessoNoAcessoAoBD or dados_selecionados != []:
            print('Pessoa já existente - Favor redigitar...')
        else:
            digitouDireito = True

    codigoCentroDistribuicao = input('Código Centro de Distribuição..........: ')
    nomeMecanico = input('Nome.....: ')
    inicioTurno = input('Início Turno (HH:MM).....: ')
    fimTurno = input('Fim Turno (HH:MM).....: ')
    inicioAlmoco = input('Início Almoço (HH:MM).....: ')
    fimAlmoco = input('Fim Almoço (HH:MM).....: ')
    
    try:
        
        inicioTurno = datetime.strptime(inicioTurno, '%H:%M').time()
        fimTurno = datetime.strptime(fimTurno, '%H:%M').time()
        inicioAlmoco = datetime.strptime(inicioAlmoco, '%H:%M').time()
        fimAlmoco = datetime.strptime(fimAlmoco, '%H:%M').time()

        # cursor é um objeto que permite que 
        # nosso programa execute comandos SQL
        # lá no servidor
        cursor = connection.cursor()

        command = "INSERT INTO daRoca.Mecanico " + \
                  "(codigoMecanico,codigoCentroDistribuicao,nomeMecanico,inicioTurno,fimTurno,inicioAlmoco,fimAlmoco) " + \
                  "VALUES" + \
                  f"('{codigoMecanico}','{codigoCentroDistribuicao}','{nomeMecanico}','{inicioTurno}','{fimTurno}','{inicioAlmoco}','{fimAlmoco}')"

        cursor.execute(command)
        connection.commit()  # Confirmar as alterações no banco de dados
        print("Cadastro realizado com sucesso!")
    except Exception as e:
        print("Cadastro mal sucedido:", e)

    return codigoMecanico

def procurarMecanico():
    digitouDireito = False
    while not digitouDireito:
        codigoMecanico = input('\nCódigo Mecânico...: ')
        resposta = esta_cadastrado_mecanico(codigoMecanico)
        sucessoNoAcessoAoBD = resposta[0]
        dados_selecionados = resposta[1]
                   
        if sucessoNoAcessoAoBD and dados_selecionados:
            print('Encontrado/a')
            print('Esses são os dados disponíveis:\n')
            print("Código Centro de Distribuição...:", dados_selecionados[0][1])
            print("Nome Mecânico...:", dados_selecionados[0][2])
            print("Início Turno...:", dados_selecionados[0][3])
            print("Fim Turno...:", dados_selecionados[0][4])
            print("Início Almoço...:", dados_selecionados[0][5])
            print("Fim Almoço...:", dados_selecionados[0][6])
            return
        else: 
            print('Pessoa Não cadastrada')
            while True:
                print(''' 
                    1 - Incluir cadastro
                    2 - Reescrever id
                    3 - Voltar ao menu ''')
                try:
                    opcao = int(input("\nO Que Deseja Realizar: "))
                    
                    if opcao == 1:
                        incluirMecanico()
                        break
                    elif opcao == 2:
                        break
                    elif opcao == 3:
                        return  
                    else:
                        print("Opção inválida. Por favor, escolha uma opção válida.")
                except ValueError:
                    print("Digite somente opções de 1 a 3!")

def atualizarMecanico():
    codigoMecanico = input('\nDigite o ID do cadastro a ser atualizado: ')
    resposta = esta_cadastrado_mecanico(codigoMecanico)
    sucessoNoAcessoAoBD = resposta[0]
    dados_selecionados = resposta[1]

    if not sucessoNoAcessoAoBD or not dados_selecionados:
        print("Pessoa não cadastrada!\n")
        while True:
            print("1 - Incluir Contato")
            print("2 - Reescrever ID")
            print("3 - Voltar ao Menu")
            o = input("\nO Que Deseja Realizar: ")
            if o == "1":
                incluirMecanico()
                return
            elif o == "2":
                atualizarMecanico()
            elif o == "3":
                return
            
    print("Campos disponíveis para atualização:\n")
    print("1) Código Centro de Distribuição")
    print("2) Nome Mecânico")
    print("3) Início Turno")
    print("4) Fim Turno")
    print("5) Inicio Almoço")
    print("6) Fim Almoço")  
    print("7) Finalizar")
    
    atualizacao = ['codigoCentroDistribuicao','nomeMecanico','inicioTurno', 'fimTurno', 'inicioAlmoco', 'fimAlmoco']
    
    campo = input("\nDigite um Campo (1-7): ")
    if campo == '7':
        return menu
    else:
        novo_valor = input("Digite o novo valor: ")
        
        try:
            cursor = connection.cursor()

            command = f"UPDATE daRoca.Mecanico SET {atualizacao[int(campo) - 1]} = ? WHERE codigoMecanico = ?"
            cursor.execute(command, (novo_valor, codigoMecanico))
            connection.commit()

            print("\nAtualização realizada com sucesso!")
        except Exception:
            print("\nErro ao atualizar mecânico:")
            
        return menu

def listarMecanico():
    cursor = connection.cursor()
    command = "SELECT * FROM daRoca.Mecanico"
    try:
        cursor.execute(command)
        dados_selecionados = cursor.fetchall()
        if dados_selecionados:
            print("Esses são todos os dados encontrados Disponiveis:")
            for i in range(len(dados_selecionados)):
                print()
                print(f"Id Mecânico...{dados_selecionados[i][0]}")
                print(f"Código Centro de Distribuição...{dados_selecionados[i][1]}")
                print(f"Nome Mecânico...{dados_selecionados[i][2]}")
                print(f"Início Turno...{dados_selecionados[i][3]}")
                print(f"Fim Turno...{dados_selecionados[i][4]}")
                print(f"Início Almoço...{dados_selecionados[i][5]}")
                print(f"Fim Almoço...{dados_selecionados[i][6]}")
                
        else:
            print("Não ha dados cadastrados")
    except Exception as e:
        print("Erro ao listar contatos:", e)

def excluirMecanico():
    digitouDireito = False
    while not digitouDireito:
        codigoMecanico = input('\nCódigo Mecânico...: ')
        resposta = esta_cadastrado_mecanico(codigoMecanico)
        sucessoNoAcessoAoBD = resposta[0]
        dados_selecionados = resposta[1]

        if not sucessoNoAcessoAoBD or not dados_selecionados:
            while True:
                print('Pessoa inexistente...\n')
                print("(1) - Reescrever Id")
                print("(2) - Voltar ao menu")
                try:
                    opcao = int(input("\nO Que Deseja Realizar: "))
                    
                    if opcao == 1:
                        return excluirMecanico()
                    elif opcao == 2:
                        return  
                    else:
                        print("Opção inválida. Por favor, escolha uma opção válida.")
                except ValueError:
                    print("Digite somente opções 1 ou 2!")
        else:
            digitouDireito = True

        print("Código Centro de Distribuição...:",dados_selecionados[0][1])
        print("Nome Mecânico...",dados_selecionados[0][2])
        print("Início Turno...",dados_selecionados[0][3])
        print("Fim Turno...",dados_selecionados[0][4])
        print("Início Almoço...",dados_selecionados[0][5])
        print("Fim Almoço...",dados_selecionados[0][6])
        print()

        resposta = umTexto('Deseja realmente excluir? ', 'Você deve digitar S ou N', ['s', 'S', 'n', 'N'])

    if resposta in ['s', 'S']:
        try:
            # cursor é um objeto que permite que 
            # nosso programa execute comandos SQL
            # lá no servidor
            cursor = connection.cursor()

            command = f"DELETE FROM daroca.Mecanico WHERE codigoMecanico={codigoMecanico}"

            cursor.execute(command)
            connection.commit()
            print('Remoção realizada com sucesso!')
        except Exception:
            print("Remoção mal sucedida!")
    else:
        print('Remoção não realizada!')

def mecanico():
    opcoes = ['Incluir',\
              'Procurar',\
              'Atualizar',\
              'Listar',\
              'Excluir',\
              'Voltar']
    
    opcao = 7
    while opcao != 6:
        opcao = opcaoEscolhida(opcoes)
        if opcao == '1':
            incluirMecanico()
        elif opcao == '2':
            procurarMecanico()
        elif opcao == '3':
            atualizarMecanico()
        elif opcao == '4':
            listarMecanico()
        elif opcao == '5':
            excluirMecanico()
        elif opcao == '6':
            break
        
    return menu

# daqui para cima, definimos subprogramas (módulos)
# daqui para baixo, implementamos o programa

mecanico_horas = {}

sucessoNoAcessoAoBD = connect()
if not sucessoNoAcessoAoBD:
    print("Falha ao conectar-se ao SQL Server")
    exit() # encerra o programa
    
atribuicoes = []
    
menu=['Ordem de Serviço',\
      'Atribuir Ordem de Serviço Para Mecânico',\
      'Mecânico',\
      'Sair do Programa']

opcao=7
while opcao!=4:
    opcao = int(opcaoEscolhida(menu))

    if opcao==1:
        ordemDeServico()
    elif opcao==2:
        incluirServicoMecanico()
    elif opcao==3:
        mecanico()
        
connection.close()
print('OBRIGADO POR USAR ESTE PROGRAMA!')
