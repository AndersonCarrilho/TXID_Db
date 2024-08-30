#!/bin/bash

# Nome do arquivo onde serão salvos os endereços com saldo maior que 0.0001 BTC
output_file="wallets_com_saldo.txt"
temp_file="temp_wallets_com_saldo.txt"

# Verificar se o arquivo de saída já existe e carregar seus dados em um array associativo
declare -A wallet_data
if [ -f "$output_file" ]; then
  while IFS=',' read -r address balance; do
    wallet_data["$address"]=$balance
  done < <(tail -n +2 "$output_file") # Ignora o cabeçalho
fi

# Função para consultar o saldo final de um endereço com reintentos
get_balance() {
  local addr=$1
  local balance=0
  local urls=("https://blockstream.info/api/address/$addr"
              "https://blockchain.info/rawaddr/$addr"
              "https://btcbook.guarda.co/api/v2/address/$addr")
  local max_retries=3

  for url in "${urls[@]}"; do
    local attempt=0

    while [ $attempt -lt $max_retries ]; do
      response=$(curl -s --max-time 10 "$url")

      if echo "$response" | jq . >/dev/null 2>&1; then
        balance=$(echo "$response" | jq -r '
          if .chain_stats then 
            .chain_stats.funded_txo_sum - .chain_stats.spent_txo_sum
          elif .final_balance then 
            .final_balance
          elif .balance then 
            .balance
          else 
            empty 
          end')

        if [[ -n "$balance" && "$balance" != "null" ]]; then
          break 2
        fi
      else
        echo "Erro ao processar a resposta da URL: $url" >&2
        echo "Resposta recebida: $response" >&2
      fi

      attempt=$((attempt + 1))
      echo "Tentativa $attempt de $max_retries falhou para $url. Repetindo em 5 segundos..." >&2
      sleep 5
    done
  done

  btc_balance=$(awk "BEGIN {print $balance/100000000}")
  echo "$btc_balance"
}

# Fazendo a requisição e extraindo os endereços únicos, ignorando valores 'null'
addresses=$(curl -s -X GET "https://blockchain.info/unconfirmed-transactions?format=json" | jq -r '.txs[].out[].addr' | sort | uniq | grep -v "null")

total=$(echo "$addresses" | wc -l)
echo "Total de endereços: $total"

# Loop para consultar o saldo de cada endereço
while read -r addr; do
  balance=$(get_balance "$addr")

  min_balance="0.0001"
  if awk "BEGIN {exit !($balance > $min_balance)}"; then
    if [[ -n "${wallet_data[$addr]}" ]]; then
      if [[ "${wallet_data[$addr]}" != "$balance" ]]; then
        echo "Atualizando saldo do endereço: $addr, Novo saldo: $balance BTC"
        wallet_data["$addr"]=$balance
      fi
    else
      echo "Adicionando novo endereço: $addr, Saldo: $balance BTC"
      wallet_data["$addr"]=$balance
    fi
  fi
done <<< "$addresses"

# Escrever os dados atualizados no arquivo de saída
{
  echo "address,balance"
  for address in "${!wallet_data[@]}"; do
    echo "$address,${wallet_data[$address]}"
  done
} > "$output_file"
