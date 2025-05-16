import random
import matplotlib.pyplot as plt
from collections import defaultdict, deque
from matplotlib.patches import Patch
from multiprocessing import Pool, cpu_count
import time

#FUNÇÕES AUXILIARES
#verificamos se a ordem das operações de cada job é respeitada no indivíduo, ou seja respeitados a ordem inter de cada job
def respeita_ordem(individuo, trabalhos):
    posicoes = defaultdict(list)
    for idx, job_id in enumerate(individuo):
        posicoes[job_id].append(idx)
    return all(posicoes[job_id]==sorted(posicoes[job_id]) for job_id in posicoes)

#FUNÇÕES DE AVALIAÇÃO
#wraper para avaliação paralela do makespan
def avaliar_individuo_mp(args):
    individuo, trabalhos, maquinas=args
    return calculo_tempo(individuo, trabalhos, maquinas)

#ALGORITMO GENÉTICO
#Geramos a população inicial de n indivíduos válidos
def criar_populacao(n, trabalhos):
    return [gerar_individuo(trabalhos) for _ in range(n)]

#avaliamos o makespan de um indivíduo
def avaliar_individuo(individuo, trabalhos, maquinas):
    return calculo_tempo(individuo, trabalhos, maquinas)

#crossover OX (Order Crossover) adaptado para restrições de ordem
def crossover(p1, p2, trabalhos):
    count_max={j: len(ops) for j, ops in enumerate(trabalhos)}
    count=defaultdict(int)
    size=len(p1)
    a, b=sorted(random.sample(range(size), 2))
    meio=p1[a:b]
    for j in meio:
        count[j]+=1
    resto=[]
    for j in p2:
        if count[j]<count_max[j]:
            resto.append(j)
            count[j]+=1
    filho=resto[:a]+meio + resto[a:]
    return filho if respeita_ordem(filho, trabalhos) else p1

#mutação por troca de posições que mantém a validade
def mutacao(ind):
    for _ in range(10): #tenta no máximo 10 trocas aleatórias
        i, j=sorted(random.sample(range(len(ind)), 2))
        novo=ind[:]
        novo[i], novo[j]=novo[j], novo[i]
        if respeita_ordem(novo, trabalhos):
            return novo
    return ind #se não entrar troca valida, ele recua para o indice anterior(atual) 

#Algoritmo genético local para refinamento
def ga_local(individuo, trabalhos, maquinas, geracoes=30, tam_pop=10):
    populacao=[individuo] + [mutacao(individuo) for _ in range(tam_pop-1)]
    for _ in range(geracoes):
        with Pool(processes=cpu_count()) as pool:
            args=[(ind, trabalhos, maquinas) for ind in populacao]
            tempos=pool.map(avaliar_individuo_mp, args)
        populacao=[ind for _, ind in sorted(zip(tempos, populacao))]
        nova=populacao[:2] #Pega os dois melhores (elitismo), para sempre pegar os melhores resultados possiveis
        while len(nova)<tam_pop:
            p1, p2=random.sample(populacao[:5], 2) #Seleção dos top 5, queremos refinar apenas os melhores
            f=crossover(p1, p2, trabalhos)
            if random.random()<0.5: #50% de chance de mutação, utilizamos isso para tentar manter a diversidade
                f=mutacao(f)
            nova.append(f)
        populacao=nova
    return min(populacao, key=lambda ind: calcular_makespan(ind, trabalhos, maquinas))

#BUSCA TABU 
#Geramos um indivíduo inicial válido com operações aleatórias
def gerar_individuo(trabalhos):
    individuo=[]
    for job_id, job in enumerate(trabalhos):
        individuo+=[job_id]*len(job) #Cria lista de operações por job
    random.shuffle(individuo)
    while not respeita_ordem(individuo, trabalhos): #verificar se respeitamos a ordem interna
        random.shuffle(individuo)
    return individuo

#Calcula o makespan de uma solução (tempo total de uma determianda ordem)
def calculo_tempo(individuo, jobs, numero_maquinas):
    indice_atual=[0]*len(jobs)
    tempo_maquina=[0]*numero_maquinas
    fim_job=[0]*len(jobs)
    for job_id in individuo:
        i=indice_atual[job_id]
        maquina, duracao=jobs[job_id][i]
        inicio=max(tempo_maquina[maquina], fim_job[job_id])
        fim=inicio + duracao
        tempo_maquina[maquina]=fim
        fim_job[job_id]=fim
        indice_atual[job_id]+=1
    return max(fim_job)
calcular_makespan=calculo_tempo 

#Geramos vizinhos válidos trocando operações na mesma máquina
def gerar_vizinhos(agenda_atual, trabalhos):
    vizinhos=[]
    maquina_por_posicao=[]
    contagem_operacoes_trabalho=defaultdict(int)
    #Mapeia uma determinada máquina para cada posição na agenda
    for posicao, id_trabalho in enumerate(agenda_atual):
        indice_operacao=contagem_operacoes_trabalho[id_trabalho]
        maquina=trabalhos[id_trabalho][indice_operacao][0]
        maquina_por_posicao.append(maquina)
        contagem_operacoes_trabalho[id_trabalho]+=1
    #Agrupa posições por máquina
    grupos_maquina=defaultdict(list)
    for posicao, maquina in enumerate(maquina_por_posicao):
        grupos_maquina[maquina].append(posicao)
    #Gera trocas entre operações da mesma máquina (testar combinações diferentes)
    for maquina, posicoes in grupos_maquina.items():
        if len(posicoes)<2:
            continue
        for i in range(len(posicoes)):
            for j in range(i + 1, len(posicoes)):
                pos_I=posicoes[i]
                pos_J=posicoes[j]
                #Só troca se forem jobs diferentes e mantiver a validade(ordem interna)
                if agenda_atual[pos_I]!=agenda_atual[pos_J]:
                    nova_agenda=agenda_atual.copy()
                    nova_agenda[pos_I], nova_agenda[pos_J]=nova_agenda[pos_J], nova_agenda[pos_I]
                    if respeita_ordem(nova_agenda, trabalhos):
                        vizinhos.append((nova_agenda, (pos_I, pos_J)))
    return vizinhos

#Implementação principal da Busca Tabu
def busca_tabu(solucao_inicial, trabalhos, numero_maquinas, max_iteracoes=300, tamanho_tabu=15):
    melhor_solucao=solucao_inicial.copy() #Melhor solução global
    solucao_atual=solucao_inicial.copy()  #Solução sendo explorada
    melhor_makespan=calculo_tempo(melhor_solucao, trabalhos, numero_maquinas)
    lista_tabu=deque(maxlen=tamanho_tabu) #Lista fifo de movimentos proibidos
    for _ in range(max_iteracoes):
        vizinhos=gerar_vizinhos(solucao_atual, trabalhos) #Gerar vizinhos válidos
        melhor_vizinho=None
        melhor_makespan_vizinho=float('inf')
        melhor_troca=None
        #Avaliar todos os vizinhos que não estão na lista Tabu
        for vizinho, troca in vizinhos:
            if troca in lista_tabu or (troca[1], troca[0]) in lista_tabu:
                continue  #Ignora movimentos na lista tabu
            makespan_vizinho=calculo_tempo(vizinho, trabalhos, numero_maquinas)
            if makespan_vizinho<melhor_makespan_vizinho:
                melhor_vizinho=vizinho
                melhor_makespan_vizinho=makespan_vizinho
                melhor_troca=troca
        if melhor_vizinho:
            #Atualiza solução atual (melhor solução atual)
            solucao_atual=melhor_vizinho
            #Atualiza melhor solução global se necessário
            if melhor_makespan_vizinho<melhor_makespan:
                melhor_solucao=melhor_vizinho.copy()
                melhor_makespan=melhor_makespan_vizinho
            #Adiciona movimento à lista tabu(movimentos proibidos)
            lista_tabu.append(melhor_troca)
    return melhor_solucao

#EXECUÇÃO PRINCIPAL
if __name__=='__main__':
    inicio=time.time()
    trabalho, maquinas=map(int, input("Digite a quantidade de maquinas e trabalhos: ").split())
    trabalhos=[]
    for i in range(trabalho):
        linha=input(f"Job {i}: ")
        numeros=list(map(int, linha.strip().split()))
        job = [(numeros[j], numeros[j+1]) for j in range(0, len(numeros), 2)]
        trabalhos.append(job)
    #Fluxo principal (ordem de execução)
    solucao_inicial=gerar_individuo(trabalhos)
    solucao_tabu=busca_tabu(solucao_inicial, trabalhos, maquinas)
    solucao_final=ga_local(solucao_tabu, trabalhos, maquinas)
    fim=time.time()

    #PROCESSAMENTO DA SOLUÇÃO
    #Inicializa variáveis para processamento
    tempos_maquinas=[0]*maquinas
    tempos_jobs=[0]*trabalho
    indice_op=[0]*trabalho #Índice único para controle das operações
    alocacao=defaultdict(list)
    #Popula alocacao com os dados reais
    for job_id in solucao_final:
        #Verificação de segurança
        op_idx=indice_op[job_id]
        maquina, duracao = trabalhos[job_id][op_idx]
        inicio=max(tempos_maquinas[maquina], tempos_jobs[job_id])
        fim=inicio+duracao
        alocacao[maquina].append((inicio, fim, f"J{job_id}-O{op_idx}"))
        tempos_maquinas[maquina]=fim
        tempos_jobs[job_id]=fim
        indice_op[job_id]+=1
    #Saída dos resultados
    print("\nMelhor makespan (GA + Tabu):", calculo_tempo(solucao_final, trabalhos, maquinas))
    print("Sequencia final:", solucao_final)
    print(f"Tempo total de execução: {fim-inicio:.2f} segundos")

    #ESCRITA EM ARQUIVO
    with open("resultado_final.txt", "w", encoding='utf-8') as arquivo:
        melhor_sequencia=[]
        indice_temp=[0]*trabalho 
        for job_id in solucao_final:
            op_idx=indice_temp[job_id]
            melhor_sequencia.append((job_id, op_idx))
            indice_temp[job_id]+=1
        arquivo.write("Melhor sequencia:\n")
        arquivo.write(str(melhor_sequencia) + "\n\n")
        arquivo.write(f"Makespan final: {calculo_tempo(solucao_final, trabalhos, maquinas)}\n")
        arquivo.write(f"Tempo total: {fim - inicio:.2f}s\n\n")
        
        arquivo.write("Detalhes por maquina:\n")
        for maq in range(maquinas):
            arquivo.write(f"\nMaquina {maq}:\n")
            operacoes=sorted(alocacao.get(maq, []), key=lambda x: x[0])
            for inicio, fim, nome in operacoes:
                arquivo.write(f"  {nome}: {inicio} - {fim}\n")

    #GERADOR DE GRÁFICO GANTT
    fig, ax=plt.subplots(figsize=(12, 6))
    cores=plt.cm.tab20.colors
    #Usa os dados já processados em alocacao
    for maq in range(maquinas):
        for inicio, fim, nome in sorted(alocacao[maq], key=lambda x: x[0]):
            job_id = int(nome.split('J')[1].split('-')[0])
            ax.barh(maq, fim - inicio, left=inicio, color=cores[job_id % len(cores)], edgecolor='black')
            ax.text((inicio + fim)/2, maq, nome, ha='center', va='center', fontsize=8)
    
    ax.set_yticks(range(maquinas))
    ax.set_yticklabels([f"Maquina {i}" for i in range(maquinas)])
    ax.set_xlabel("Tempo")
    ax.set_title("Grafico de Gantt - GA como busca local sobre Tabu")
    plt.tight_layout()
    plt.savefig("grafico_gantt_final.png")
    plt.show()