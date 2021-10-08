import pandas as pd
import win32com.client as win32
import pathlib
import time


emails = pd.read_excel(r'Bases de Dados\Emails.xlsx')
lojas = pd.read_csv(r'Bases de Dados\Lojas.csv', encoding='latin1', sep=';')
vendas = pd.read_excel(r'Bases de Dados\Vendas.xlsx')


vendas = vendas.merge(lojas, on='ID Loja')

dicionario_lojas = {}
for loja in lojas['Loja']:
    dicionario_lojas[loja] = vendas.loc[vendas['Loja'] == loja, :]


dia_indicador = vendas['Data'].max()

time.sleep(3)

caminho_backup = pathlib.Path(r'Backup Arquivos Lojas')
arquivo_pasta_backup = caminho_backup.iterdir()
lista_nome_backup = [arquivo.name for arquivo in arquivo_pasta_backup]

for loja in dicionario_lojas:
    if loja not in lista_nome_backup:
        nova_pasta = caminho_backup / loja
        nova_pasta.mkdir()

    nome_arquivo = f'{dia_indicador.month}_{dia_indicador.day}_{loja}.xlsx'
    local_arquivo = caminho_backup / loja / nome_arquivo
    dicionario_lojas[loja].to_excel(local_arquivo)


meta_faturamento_dia = 1000
meta_faturamento_ano = 1650000
meta_qtdeprodutos_dia = 4
meta_qtdeprodutos_ano = 120
meta_tictkmedio_dia = 500
meta_tictkmedio_ano = 500

for loja in dicionario_lojas:
    vendas_loja = dicionario_lojas[loja]
    vendas_loja_dia = vendas_loja.loc[vendas_loja['Data'] == dia_indicador, :]

    faturamento_ano = vendas_loja['Valor Final'].sum()

    faturamento_dia = vendas_loja_dia['Valor Final'].sum()

    qtde_produtos_anos = len(vendas_loja['Produto'].unique())

    qtde_produtos_dia = len(vendas_loja_dia['Produto'].unique())

    valor_venda = vendas_loja.groupby('Código Venda').sum()
    tictk_medio_ano = valor_venda['Valor Final'].mean()

    valor_venda_dia = vendas_loja_dia.groupby('Código Venda').sum()
    tictk_medio_dia = valor_venda_dia['Valor Final'].mean()

    outlook = win32.Dispatch('outlook.application')

    nome = emails.loc[emails['Loja'] == loja, 'Gerente'].values[0]
    mail = outlook.CreateItem(0)
    mail.To = emails.loc[emails['Loja'] == loja, 'E-mail'].values[0]
    mail.Subject = f'OnePage Dia {dia_indicador.day}/{dia_indicador.month} - loja {loja}'

    if faturamento_dia >= meta_faturamento_dia:
        cor_fat_dia = 'green'
    else:
        cor_fat_dia = 'red'

    if faturamento_ano >= meta_faturamento_ano:
        cor_fat_ano = 'green'
    else:
        cor_fat_ano = 'red'

    if qtde_produtos_dia >= meta_qtdeprodutos_dia:
        cor_qntd_dia = 'green'
    else:
        cor_qntd_dia = 'red'

    if qtde_produtos_anos >= meta_qtdeprodutos_ano:
        cor_qntd_ano = 'green'
    else:
        cor_qntd_ano = 'red'

    if tictk_medio_dia >= meta_tictkmedio_dia:
        cor_ticket_dia = 'green'
    else:
        cor_ticket_dia = 'red'

    if tictk_medio_ano >= meta_tictkmedio_ano:
        cor_ticket_ano = 'green'
    else:
        cor_ticket_ano = 'red'

    mail.HTMLBody = f''' 
    <p>Bom Dia, {nome}</p>

    <p>O resultado de ontem <strong>({dia_indicador.day}/{dia_indicador.month})</strong> da <strong> loja {loja}</strong> foi:<p>

    <table>
      <tr>
        <th>Indicador</th>
        <th>Valor dia</th>
        <th>Meta dia</th>
        <th>Cenário dia</th>

      </tr>
      <tr>
        <td>Faturamento</td>
        <td style="text-align: center">R${faturamento_dia:.2f}</td>
        <td style="text-align: center">R${meta_faturamento_dia:.2f}</td>
        <td style="text-align: center"><font color="{cor_fat_dia}">◙</font></td>

      </tr>
      <tr>
        <td>Diversidade de Produtos</td>
        <td style="text-align: center">{qtde_produtos_dia}</td>
        <td style="text-align: center">{meta_qtdeprodutos_dia}</td>
        <td style="text-align: center"><font color="{cor_qntd_dia}">◙</td>
      </tr>
      <tr>
        <td>Ticket Médio</td>
        <td style="text-align: center">R${tictk_medio_dia:.2f}</td>
        <td style="text-align: center">R${meta_tictkmedio_dia:.2f}</td>
        <td style="text-align: center"><font color="{cor_ticket_dia}">◙</td>
      </tr>
    </table>
    <br>
    <table>
      <tr>
        <th>Indicador</th>
        <th>Valor Ano</th>
        <th>Meta Ano</th>
        <th>Cenário Ano</th>

      </tr>
      <tr>
        <td>Faturamento</td>
        <td style="text-align: center">R${faturamento_ano:.2f}</td>
        <td style="text-align: center">R${meta_faturamento_ano:.2f}</td>
        <td style="text-align: center"><font color="{cor_fat_ano}">◙</font></td>

      </tr>
      <tr>
        <td>Diversidade de Produtos</td>
        <td style="text-align: center">{qtde_produtos_anos}</td>
        <td style="text-align: center">{meta_qtdeprodutos_ano}</td>
        <td style="text-align: center"><font color="{cor_qntd_ano}">◙</td>
      </tr>
      <tr>
        <td>Ticket Médio</td>
        <td style="text-align: center">R${tictk_medio_ano:.2f}</td>
        <td style="text-align: center">R${meta_tictkmedio_ano:.2f}</td>
        <td style="text-align: center"><font color="{cor_ticket_ano}">◙</td>
      </tr>
    </table>



    <p>segue em anexo a planinha com todos os dados para mais detalhes.</p>

    <p>Qualquer dúvida estou a disposição.</p>
    <p>Att., Tomé</p>

    '''

    attachment = pathlib.Path.cwd() / caminho_backup / loja / f'{dia_indicador.month}_{dia_indicador.day}_{loja}.xlsx'
    mail.Attachments.Add(str(attachment))

    mail.Send()


faturamento_lojas = vendas.groupby('Loja')[['Loja', 'Valor Final']].sum()
faturamento_lojas_ano = faturamento_lojas.sort_values(by='Valor Final', ascending=False)


nome_arquivo = f'{dia_indicador.month}_{dia_indicador.day}_Ranking Anual.xlsx'
faturamento_lojas_ano.to_excel(r'Backup Arquivos Lojas\{}'.format(nome_arquivo))

vendas_dia = vendas.loc[vendas['Data'] == dia_indicador, :]
faturamento_lojas_dia = vendas_dia.groupby('Loja')[['Loja', 'Valor Final']].sum()
faturamento_lojas_dia = faturamento_lojas_dia.sort_values(by='Valor Final', ascending=False)


nome_arquivo = f'{dia_indicador.month}_{dia_indicador.day}_Ranking Dia.xlsx'
faturamento_lojas_dia.to_excel(r'Backup Arquivos Lojas\{}'.format(nome_arquivo))

outlook = win32.Dispatch('outlook.application')

mail = outlook.CreateItem(0)
mail.To = emails.loc[emails['Loja'] == 'Diretoria', 'E-mail'].values[0]
mail.Subject = f'Ranking Dia {dia_indicador.day}/{dia_indicador.month}'
mail.Body = f'''
Prezados, Bom dia

Melhor loja do Dia em Faturamento: Loja {faturamento_lojas_dia.index[0]} com Faturamento R$ {faturamento_lojas_dia.iloc[0, 0]:,.2f}
Pior loja do Dia em Faturamento: Loja {faturamento_lojas_dia.index[-1]} com Faturamento R$ {faturamento_lojas_dia.iloc[-1, 0]:,.2f}

Melhor loja do Ano em Faturamento: Loja {faturamento_lojas_ano.index[0]} com Faturamento R$ {faturamento_lojas_ano.iloc[0, 0]:,.2f}
Pior loja do Ano em Faturamento: Loja {faturamento_lojas_ano.index[-1]} com Faturamento R$ {faturamento_lojas_ano.iloc[-1, 0]:,.2f}

segue em anexos os rankings do ano e do dia de todas as loja  

Qualquer dúvida estou a disposição

att., 
Tomé 
'''


attachment = pathlib.Path.cwd() / caminho_backup / f'{dia_indicador.month}_{dia_indicador.day}_Ranking Anual.xlsx'
mail.Attachments.Add(str(attachment))
attachment = pathlib.Path.cwd() / caminho_backup / f'{dia_indicador.month}_{dia_indicador.day}_Ranking Dia.xlsx'
mail.Attachments.Add(str(attachment))

mail.Send()

print(f'E-MAIL da Diretoria enviado com sucesso')
