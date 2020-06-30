import MetaTrader5 as mt5
# exibimos dados sobre o pacote MetaTrader5
print("MetaTrader5 package author: ",mt5.__author__)
print("MetaTrader5 package version: ",mt5.__version__)
 
# estabelecemos a conexão ao MetaTrader 5
if not mt5.initialize():
    print("initialize() failed, error code =",mt5.last_error())
    quit()
 
# imprimimos informações sobre a versão do MetaTrader 5
print(mt5.version())
# conectamo-nos à conta de negociação sem especificar senha e servidor
account=1000349177
authorized=mt5.login(account)  # a senha será retirada do banco de dados do terminal, se especificado lembrar os dados de conexão
if authorized:
    print("connected to account #{}".format(account))
else:
    print("failed to connect at account #{}, error code: {}".format(account, mt5.last_error()))
 
# agora conectamo-nos a outra conta de negociação indicando senha
account=25115284
authorized=mt5.login(account, password="gqrtz0lbdm")
if authorized:
    # exibimos os dados sobre a conta de negociação como estão
    print(mt5.account_info())
    # exibimos os dados da conta de negociação como uma lista
    print("Show account_info()._asdict():")
    account_info_dict = mt5.account_info()._asdict()
    for prop in account_info_dict:
        print("  {}={}".format(prop, account_info_dict[prop]))
else:
    print("failed to connect at account #{}, error code: {}".format(account, mt5.last_error()))
 
# concluímos a conexão ao terminal MetaTrader 5
mt5.shutdown()