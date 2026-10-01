"""Configurações compartilhadas entre o produtor e o consumidor."""

# Endereço do broker ActiveMQ (protocolo STOMP)
HOST = "localhost"
PORTA_STOMP = 61613

# Credenciais padrão do ActiveMQ
USUARIO = "admin"
SENHA = "admin"

# Fila usada na demonstração. O prefixo /queue/ indica uma FILA (ponto a ponto).
# Trocando para /topic/... a mensagem vira publish/subscribe (todos recebem).
FILA = "/queue/pedidos"
