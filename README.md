🤖 AgendaBot - Assistente de Agendamento para Telegram
Um chatbot simples para Telegram que ajuda você a gerenciar seus compromissos e eventos pessoais.

✨ Funcionalidades Principais
Adicionar eventos: /agendar para criar novos compromissos

Listar eventos: /listar para ver todos seus agendamentos

Remover eventos: /remover para excluir compromissos existentes

Ajuda rápida: /ajuda para ver todos os comandos disponíveis

Cancelamento: /cancelar para interromper operações em andamento

🚀 Como Usar
Adicione o bot no Telegram: @SeuAgendaBot

Comece com /start para iniciar

Comandos disponíveis:

/agendar - Adiciona novo evento
/listar - Mostra seus compromissos
/remover - Exclui um evento
/ajuda - Mostra ajuda
/cancelar - Cancela operação atual
📝 Exemplo de Uso:
/agendar
25/12
Natal em família

/listar
⚙️ Configuração Local (Para Desenvolvimento)
Pré-requisitos
Python 3.8+

Conta no Telegram

Token do Bot (obtido com @BotFather)

Passo a Passo
Clone o repositório:

bash
git clone https://github.com/seuusuario/agendabot.git
cd agendabot
Crie um ambiente virtual:

bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate    # Windows
Instale as dependências:

bash
pip install -r requirements.txt
Crie o arquivo de configuração:

bash
echo "TELEGRAM_BOT_TOKEN=seu_token_aqui" > .env
Execute o bot:

bash
python bot.py
📦 Estrutura do Projeto
.
├── bot.py             # Código principal do bot
├── .env               # Armazena o token (não versionado)
├── agendamentos.db    # Banco de dados SQLite (gerado automaticamente)
├── requirements.txt   # Dependências
└── README.md          # Este arquivo
