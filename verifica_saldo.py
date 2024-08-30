import os
import pandas as pd
import multiprocessing as mp
from functools import lru_cache

# Caminho da pasta onde os arquivos estão localizados
address_dir = os.path.expanduser('~/Documentos/address')

@lru_cache(maxsize=None)
def list_txt_files(directory):
    """Lista todos os arquivos .txt na pasta especificada."""
    return [f for f in os.listdir(directory) if f.endswith('.txt')]

def process_file_chunk(file_path, chunk_size=1000):
    """Processa um arquivo em blocos e retorna os dados em blocos."""
    try:
        chunks = pd.read_csv(file_path, skiprows=1, names=["address", "balance"], on_bad_lines='skip', chunksize=chunk_size, low_memory=False)
        return chunks
    except Exception as e:
        print(f"Erro ao processar o arquivo {file_path}: {e}")
        return []

def display_chunks(chunks):
    """Exibe os dados dos blocos conforme são carregados e calcula os totais."""
    try:
        total_addresses = 0
        total_balance = 0.0

        for chunk in chunks:
            # Converte a coluna 'balance' para numérico, forçando erros a NaN
            chunk['balance'] = pd.to_numeric(chunk['balance'], errors='coerce')
            
            # Remove linhas com valores NaN na coluna 'balance'
            chunk = chunk.dropna(subset=['balance'])

            # Exibe o bloco atual
            print("\nDados carregados:")
            print(chunk.to_string(index=False))  # Mostra todos os dados do bloco

            # Atualiza totais
            total_addresses += len(chunk)
            total_balance += chunk['balance'].sum()

        return total_addresses, total_balance
    except Exception as e:
        print(f"Erro ao exibir os dados: {e}")
        return 0, 0

def process_all_files(directory):
    """Processa todos os arquivos na pasta especificada e retorna os totais."""
    total_addresses = 0
    total_balance = 0.0
    files = list_txt_files(directory)

    for file in files:
        file_path = os.path.join(directory, file)
        print(f"\nProcessando arquivo: {file}")
        chunks = process_file_chunk(file_path)
        if chunks:
            addresses, balance = display_chunks(chunks)
            total_addresses += addresses
            total_balance += balance
        else:
            print(f"Arquivo {file} está vazio ou não pôde ser carregado corretamente.")

    return total_addresses, total_balance

def main():
    # Lista todos os arquivos .txt na subpasta address
    files = list_txt_files(address_dir)

    # Mostra as opções para o usuário
    print("Escolha uma opção:")
    print("1. Carregar um arquivo específico")
    print("2. Carregar todos os arquivos")

    option = int(input("Digite o número da opção desejada: "))

    if option == 1:
        # Mostra os arquivos disponíveis e pede para o usuário escolher um
        print("\nArquivos disponíveis:")
        for i, file in enumerate(files):
            print(f"{i + 1}. {file}")

        file_index = int(input("Escolha o número do arquivo que deseja carregar: ")) - 1
        selected_file = os.path.join(address_dir, files[file_index])

        # Processa e exibe os dados do arquivo em blocos
        chunks = process_file_chunk(selected_file)
        if chunks:
            total_addresses, total_balance = display_chunks(chunks)

            print(f"\nTotal de endereços: {total_addresses}")
            print(f"Saldo total em BTC: {total_balance:.8f}")
        else:
            print("O arquivo está vazio ou não pôde ser carregado corretamente.")

    elif option == 2:
        # Processa todos os arquivos na pasta
        total_addresses, total_balance = process_all_files(address_dir)

        print(f"\nTotal de endereços: {total_addresses}")
        print(f"Saldo total em BTC: {total_balance:.8f}")

    else:
        print("Opção inválida. Por favor, escolha 1 ou 2.")

if __name__ == "__main__":
    main()
