#!/bin/bash

echo "=========================================="
echo "       INICIANDO MONITORAMENTO"
echo "=========================================="
echo

# Ativa o ambiente virtual
source ~/Documentos/novo/venv/bin/activate

echo "------------------------------------------"
echo "  1/2 - SITES NORMAIS"
echo "------------------------------------------"
echo

python monitor_sites.py

STATUS_NORMAL=$?

echo
echo "=========================================="

if [ $STATUS_NORMAL -eq 0 ]; then
    echo "Monitoramento dos sites normais concluído."
else
    echo "ATENÇÃO: monitor_sites.py terminou com erro."
fi

echo "=========================================="
echo

echo "------------------------------------------"
echo "  2/2 - SITES .ONION"
echo "------------------------------------------"
echo

python monitor_onion.py

STATUS_ONION=$?

echo
echo "=========================================="

if [ $STATUS_ONION -eq 0 ]; then
    echo "Monitoramento .onion concluído."
else
    echo "ATENÇÃO: monitor_onion.py terminou com erro."
fi

echo "=========================================="
echo
echo "        MONITORAMENTO FINALIZADO"
echo "=========================================="