#!/bin/bash

# Fazendo a requisição e extraindo os endereços únicos, ignorando valores 'null'
addresses=$(curl -s -X GET "https://blockchain.info/unconfirmed-transactions?format=json" | jq -r '.txs[].out[].addr' | sort | uniq | grep -v "null")

# Mostrando os endereços
echo "$addresses"

# Contando o total de endereços
total=$(echo "$addresses" | wc -l)

# Mostrando o total
echo "Total de endereços: $total"
