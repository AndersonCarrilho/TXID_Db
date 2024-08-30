import os
import pandas as pd
import sqlite3
import multiprocessing as mp
from functools import lru_cache

# Caminho da pasta onde os arquivos estão localizados
address_dir = os.path.expanduser('~/Documentos/address')

# Função para listar arquivos .txt no diretório
@lru_cache(maxsize=None)
def list_txt_files(directory):
    return [f for f in os.listdir(directory) if f.endswith('.txt')]

# Função para processar blocos de arquivos
def process_file_chunk(file_path, chunk_size=1000):
    try:
        chunks = pd.read_csv(file_path, skiprows=1, names=["address", "balance"], on_bad_lines='skip', chunksize=chunk_size, low_memory=False)
        return chunks
    except Exception as e:
        print(f"Erro ao processar o arquivo {file_path}: {e}")
        return []

# Função para armazenar ou atualizar os dados no banco de dados
def store_in_database(data, conn):
    try:
        data['balance'] = pd.to_numeric(data['balance'], errors='coerce')
        data = data.dropna(subset=['balance'])

        print(f"Armazenando ou atualizando os dados no banco de dados:\n{data.head()}")

        # Inserir ou atualizar dados
        for index, row in data.iterrows():
            existing_entry = conn.execute("SELECT balance FROM addresses WHERE address = ?", (row['address'],)).fetchone()
            
            if existing_entry:
                # Se o balance for diferente, atualize
                if existing_entry[0] != row['balance']:
                    conn.execute("""
                        UPDATE addresses
                        SET balance = ?
                        WHERE address = ?
                    """, (row['balance'], row['address']))
                    print(f"Atualizado: {row['address']} com novo balance: {row['balance']}")
            else:
                # Se não existir, insira o novo address e balance
                conn.execute("""
                    INSERT INTO addresses (address, balance)
                    VALUES (?, ?)
                """, (row['address'], row['balance']))
                print(f"Inserido: {row['address']} com balance: {row['balance']}")

        conn.commit()  # Certifica-se de que as alterações sejam salvas
        
        # Confirma se as linhas foram inseridas ou atualizadas
        result = conn.execute("SELECT COUNT(*) FROM addresses").fetchone()
        print(f"Número total de linhas na tabela 'addresses': {result[0]}")
        
    except Exception as e:
        print(f"Erro ao armazenar os dados no banco de dados: {e}")

# Função para exibir os blocos e atualizar os totais
def display_chunks(chunks, conn):
    total_addresses = 0
    total_balance = 0.0

    for chunk in chunks:
        chunk['balance'] = pd.to_numeric(chunk['balance'], errors='coerce')
        chunk = chunk.dropna(subset=['balance'])

        print("\nDados carregados:")
        print(chunk.to_string(index=False))

        # Atualiza totais
        total_addresses += len(chunk)
        total_balance += chunk['balance'].sum()

        # Armazena ou atualiza os dados no banco de dados
        store_in_database(chunk, conn)

    return total_addresses, total_balance

# Função para processar todos os arquivos
def process_all_files(directory, conn):
    total_addresses = 0
    total_balance = 0.0
    files = list_txt_files(directory)

    for file in files:
        file_path = os.path.join(directory, file)
        print(f"\nProcessando o arquivo: {file_path}")
        chunks = process_file_chunk(file_path)
        if chunks:
            addresses, balance = display_chunks(chunks, conn)
            total_addresses += addresses
            total_balance += balance
        else:
            print(f"Arquivo {file} está vazio ou não pôde ser carregado corretamente.")

    return total_addresses, total_balance

# Função para consultar o saldo de um endereço específico
def query_address(conn, address):
    try:
        cursor = conn.execute("SELECT balance FROM addresses WHERE address = ?", (address,))
        result = cursor.fetchone()
        if result:
            print(f"Endereço: {address}\nSaldo: {result[0]:.8f} BTC")
        else:
            print(f"Endereço {address} não encontrado no banco de dados.")
    except Exception as e:
        print(f"Erro ao consultar o banco de dados: {e}")

# Função principal
def main():
    # Conecta ao banco de dados SQLite
    conn = sqlite3.connect('bitcoin_addresses.db')

    # Cria a tabela se não existir
    conn.execute("""
        CREATE TABLE IF NOT EXISTS addresses (
            address TEXT PRIMARY KEY,
            balance REAL
        )
    """)

    # Mostra as opções para o usuário
    print("Escolha uma opção:")
    print("1. Carregar um arquivo específico")
    print("2. Carregar todos os arquivos")
    print("3. Consultar saldo de um endereço")

    option = int(input("Digite o número da opção desejada: "))

    if option == 1:
        # Lista todos os arquivos .txt na subpasta address
        files = list_txt_files(address_dir)

        # Mostra os arquivos disponíveis e pede para o usuário escolher um
        print("\nArquivos disponíveis:")
        for i, file in enumerate(files):
            print(f"{i + 1}. {file}")

        file_index = int(input("Escolha o número do arquivo que deseja carregar: ")) - 1
        selected_file = os.path.join(address_dir, files[file_index])

        # Processa e exibe os dados do arquivo em blocos
        chunks = process_file_chunk(selected_file)
        if chunks:
            total_addresses, total_balance = display_chunks(chunks, conn)
            print(f"\nTotal de endereços: {total_addresses}")
            print(f"Saldo total em BTC: {total_balance:.8f}")
        else:
            print("O arquivo está vazio ou não pôde ser carregado corretamente.")

    elif option == 2:
        # Processa todos os arquivos na pasta
        total_addresses, total_balance = process_all_files(address_dir, conn)
        print(f"\nTotal de endereços: {total_addresses}")
        print(f"Saldo total em BTC: {total_balance:.8f}")

    elif option == 3:
        # Consulta um endereço específico
        address = input("Digite o endereço Bitcoin que deseja consultar: ")
        query_address(conn, address)

    else:
        print("Opção inválida. Por favor, escolha 1, 2 ou 3.")

    # Fecha a conexão com o banco de dados
    conn.close()

if __name__ == "__main__":
    main()
