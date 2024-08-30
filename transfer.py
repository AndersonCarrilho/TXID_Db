from mnemonic import Mnemonic
import bip32utils
import requests
import time

# Função para criar 286 wallets e exibir chaves WIF e endereços
def criar_wallets(rede):
    wallets = []
    mnemo = Mnemonic("english")
    for i in range(286):
        # Gerar frase mnemônica e semente
        words = mnemo.generate(strength=256)
        seed = mnemo.to_seed(words)
        
        # Gerar chave privada e derivar endereço Bitcoin usando BIP32
        bip32_root_key_obj = bip32utils.BIP32Key.fromEntropy(seed)
        private_key_wif = bip32_root_key_obj.WalletImportFormat()
        address = bip32_root_key_obj.Address()
        
        wallets.append({'mnemonic': words, 'private_key_wif': private_key_wif, 'address': address})
        
        # Exibir a chave WIF e endereço da wallet criada
        print(f"Wallet {i+1}:")
        print(f"Mnemonic: {words}")
        print(f"Private Key (WIF): {private_key_wif}")
        print(f"Address: {address}\n")
        
    return wallets

# Função para simular a transferência
def simular_transferencia(valor_total, wallets, rede):
    print("\nEscolha a prioridade do gas 'fee':")
    print("1. Lenta (0.00000196 BTC)")
    print("2. Normal (0.00000286 BTC)")
    print("3. Urgente (0.00000512 BTC)")
    print("4. Extrema (0.00001000 BTC)")
    
    escolha = input("Digite a opção: ")
    prioridade_fee = 0
    
    if escolha == '1':
        prioridade_fee = 0.00000196
    elif escolha == '2':
        prioridade_fee = 0.00000286
    elif escolha == '3':
        prioridade_fee = 0.00000512
    elif escolha == '4':
        prioridade_fee = 0.00001000
    else:
        print("Opção inválida.")
        return
    
    print(f"Prioridade escolhida: {prioridade_fee} BTC")
    
    # Verificando saldo das wallets de gas e tentando realizar a transferência
    saldo_total = 0
    txid = None
    
    for wallet in wallets:
        address = wallet['address']
        wif = wallet['private_key_wif']
        
        # Consultando saldo da wallet
        response = requests.get(f"https://mempool.nixbitcoin.org/api/address/{address}")
        data = response.json()
        
        # Calculando o saldo disponível
        saldo_wallet = data['chain_stats']['funded_txo_sum'] - data['chain_stats']['spent_txo_sum']
        saldo_wallet_btc = saldo_wallet / 100000000  # Converter para BTC
        
        print(f"Wallet {address} possui saldo: {saldo_wallet_btc} BTC")
        
        # Se o saldo da wallet for suficiente para cobrir a taxa de gas
        if saldo_wallet_btc >= prioridade_fee:
            saldo_total += saldo_wallet_btc
            
            # Simulando envio da transação
            print(f"Enviando {prioridade_fee} BTC de gas 'fee' da wallet {address}...")
            time.sleep(1)  # Simulando tempo de envio
            
            # Aqui você implementaria a lógica de envio real utilizando a rede Bitcoin
            # Em vez disso, estamos simulando que a transação foi enviada com sucesso
            txid = "dummy_txid_" + address[-4:]  # Simulando um txid
            
            print(f"Transação enviada. TXID: {txid}\n")
            
            if saldo_total >= valor_total:
                break
    
    if txid:
        print(f"Transação realizada com sucesso. TXID: {txid}")
    else:
        print("Não foi possível completar a transação. Saldo insuficiente.")

# Função principal
def main():
    print("Sistema de transferência de Bitcoin")
    print("-------------------------------------")
    print("Escolha a rede:")
    print("1. Rede Real (MainNet)")
    print("2. Rede Teste (TestNet)")
    
    opcao_rede = input("Digite a opção: ")
    if opcao_rede == '1':
        rede = "bitcoin"
    elif opcao_rede == '2':
        rede = "testnet"
    else:
        print("Opção inválida.")
        return
    
    valor_total = float(input("Insira o valor a ser transferido (em BTC): "))
    
    print("\nEscolha a opção para a carteira de destino:")
    print("1. Inserir Wallet Manualmente")
    print("2. Criar Wallet")
    
    opcao_wallet = input("Digite a opção: ")
    if opcao_wallet == '1':
        endereco_destino = input("Insira o endereço de destino: ")
    elif opcao_wallet == '2':
        # Criar 286 wallets
        wallets = criar_wallets(rede)
        endereco_destino = wallets[0]['address']  # Usar o primeiro endereço como exemplo
    else:
        print("Opção inválida.")
        return
    
    print(f"Endereço de destino: {endereco_destino}")
    
    # Simular transferência utilizando wallets de gas "fee"
    simular_transferencia(valor_total, wallets, rede)

if __name__ == "__main__":
    main()
