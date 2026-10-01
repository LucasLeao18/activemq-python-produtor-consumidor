"""
PRODUTOR de mensagens.

Conecta no ActiveMQ e envia pedidos (em JSON) para a fila /queue/pedidos.
O produtor NÃO sabe quem vai consumir: ele só entrega a mensagem ao broker e segue a vida.

Uso:
    python produtor.py                 # envia 5 pedidos de exemplo
    python produtor.py -n 20           # envia 20 pedidos
    python produtor.py -m "Olá fila!"  # envia uma mensagem de texto livre
"""

import argparse
import json
import random
import time
from datetime import datetime

import stomp

import config

PRODUTOS = ["Pizza", "Hambúrguer", "Sushi", "Açaí", "Pastel", "Coxinha"]
CLIENTES = ["Ana", "Bruno", "Carla", "Diego", "Elisa", "Felipe"]


def criar_pedido(numero):
    return {
        "id": numero,
        "cliente": random.choice(CLIENTES),
        "produto": random.choice(PRODUTOS),
        "quantidade": random.randint(1, 3),
        "criado_em": datetime.now().strftime("%H:%M:%S"),
    }


def main():
    parser = argparse.ArgumentParser(description="Produtor de mensagens ActiveMQ")
    parser.add_argument("-n", "--quantidade", type=int, default=5, help="quantos pedidos enviar")
    parser.add_argument("-m", "--mensagem", help="envia um texto livre em vez de pedidos")
    parser.add_argument("-i", "--intervalo", type=float, default=0.5, help="segundos entre envios")
    args = parser.parse_args()

    # 1) Conecta no broker
    conexao = stomp.Connection([(config.HOST, config.PORTA_STOMP)])
    conexao.connect(config.USUARIO, config.SENHA, wait=True)
    print(f"[PRODUTOR] Conectado ao ActiveMQ em {config.HOST}:{config.PORTA_STOMP}")

    # 2) Envia as mensagens para a fila
    if args.mensagem:
        conexao.send(destination=config.FILA, body=args.mensagem, content_type="text/plain")
        print(f"[PRODUTOR] Enviado -> {config.FILA}: {args.mensagem}")
    else:
        for numero in range(1, args.quantidade + 1):
            pedido = criar_pedido(numero)
            conexao.send(
                destination=config.FILA,
                body=json.dumps(pedido, ensure_ascii=False),
                content_type="application/json",
                headers={"persistent": "true"},  # sobrevive a um restart do broker
            )
            print(f"[PRODUTOR] Enviado pedido #{pedido['id']}: "
                  f"{pedido['quantidade']}x {pedido['produto']} para {pedido['cliente']}")
            time.sleep(args.intervalo)

    # 3) Desconecta
    conexao.disconnect()
    print("[PRODUTOR] Pronto! Mensagens entregues ao broker.")


if __name__ == "__main__":
    main()
