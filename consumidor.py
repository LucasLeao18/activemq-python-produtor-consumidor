"""
CONSUMIDOR de mensagens.

Fica "escutando" a fila /queue/pedidos. Sempre que o broker entrega uma mensagem,
o método on_message é chamado, o pedido é "processado" e o consumidor confirma (ACK).
Sem o ACK, o ActiveMQ considera a mensagem não processada e pode reentregá-la.

Uso:
    python consumidor.py                # consumidor chamado "Consumidor-1"
    python consumidor.py --nome Cozinha # dá um nome (útil para rodar vários ao mesmo tempo)
    python consumidor.py --demora 2     # simula 2s de processamento por mensagem

Pressione Ctrl+C para encerrar.
"""

import argparse
import json
import time

import stomp

import config


class OuvinteDePedidos(stomp.ConnectionListener):
    """Recebe os eventos da conexão (mensagens, erros, desconexão)."""

    def __init__(self, conexao, nome, demora):
        self.conexao = conexao
        self.nome = nome
        self.demora = demora
        self.recebidas = 0

    def on_message(self, frame):
        self.recebidas += 1
        try:
            pedido = json.loads(frame.body)
            descricao = (f"pedido #{pedido['id']}: {pedido['quantidade']}x {pedido['produto']} "
                         f"para {pedido['cliente']} (criado {pedido['criado_em']})")
        except (ValueError, KeyError, TypeError):
            descricao = f"texto: {frame.body}"

        print(f"[{self.nome}] Recebido {descricao}")
        time.sleep(self.demora)  # simula o tempo de processamento

        # Confirma ao broker que a mensagem foi processada -> ela sai da fila
        self.conexao.ack(frame.headers["message-id"], frame.headers["subscription"])
        print(f"[{self.nome}]   OK processado (total: {self.recebidas})")

    def on_error(self, frame):
        print(f"[{self.nome}] ERRO do broker: {frame.body}")

    def on_disconnected(self):
        print(f"[{self.nome}] Desconectado do broker.")


def main():
    parser = argparse.ArgumentParser(description="Consumidor de mensagens ActiveMQ")
    parser.add_argument("--nome", default="Consumidor-1", help="nome exibido nos logs")
    parser.add_argument("--demora", type=float, default=1.0, help="segundos para processar cada mensagem")
    args = parser.parse_args()

    # 1) Conecta no broker e registra o "ouvinte"
    conexao = stomp.Connection([(config.HOST, config.PORTA_STOMP)])
    conexao.set_listener("pedidos", OuvinteDePedidos(conexao, args.nome, args.demora))
    conexao.connect(config.USUARIO, config.SENHA, wait=True)

    # 2) Se inscreve na fila
    #    ack=client-individual -> nós confirmamos cada mensagem manualmente
    #    prefetchSize=1        -> pega uma mensagem por vez (divide melhor entre vários consumidores)
    conexao.subscribe(
        destination=config.FILA,
        id=1,
        ack="client-individual",
        headers={"activemq.prefetchSize": "1"},
    )
    print(f"[{args.nome}] Aguardando mensagens em {config.FILA} ... (Ctrl+C para sair)")

    # 3) Mantém o programa vivo; as mensagens chegam em outra thread via on_message
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        conexao.disconnect()


if __name__ == "__main__":
    main()
