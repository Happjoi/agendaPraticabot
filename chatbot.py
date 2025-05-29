# Instale as dependências necessárias:
# pip install python-telegram-bot python-dotenv

import logging
from datetime import datetime
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters
)
import sqlite3
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')  

# Configurações
DB_NAME = "agendamentos.db"

# Estados da conversa
DATA, DESCRICAO = range(2)
ESCOLHER_EVENTO = range(1)  

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Inicializar banco de dados
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS eventos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER NOT NULL,
            data TEXT NOT NULL,
            descricao TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Adicionar evento ao banco
def add_evento(chat_id, data, descricao):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO eventos (chat_id, data, descricao) VALUES (?, ?, ?)",
        (chat_id, data, descricao)
    )
    conn.commit()
    conn.close()

# Listar eventos do usuário
def list_eventos(chat_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, data, descricao FROM eventos WHERE chat_id = ? ORDER BY data",
        (chat_id,)
    )
    eventos = cursor.fetchall()
    conn.close()
    return eventos

# Remover evento
def remove_evento(id_evento, chat_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM eventos WHERE id = ? AND chat_id = ?",
        (id_evento, chat_id)
    )
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    return rows_affected

# Comandos do bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_html(
        rf"Olá {user.mention_html()}! Sou seu assistente de agendamento. 🤖\n\n"
        "🔹 Use /agendar para adicionar um novo evento\n"
        "🔹 Use /listar para ver seus compromissos\n"
        "🔹 Use /remover para excluir um evento\n"
        "🔹 Use /ajuda para ajuda"
    )

async def ajuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
📋 *Comandos disponíveis:*
/start - Inicia o bot
/agendar - Adiciona novo evento
/listar - Mostra seus compromissos
/remover - Remove um evento
/ajuda - Mostra esta ajuda
/cancelar - Cancela operação em andamento

📅 *Formato da data:*
DD/MM/AAAA ou DD/MM (para ano atual)
Exemplo: 25/12/2024 ou 25/12
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def agendar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📅 Por favor, informe a data do evento (formato DD/MM ou DD/MM/AAAA):"
    )
    return DATA

async def receber_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data_str = update.message.text.strip()
        partes = data_str.split('/')
        
        # Validar e formatar data
        if len(partes) == 2:  # DD/MM
            dia, mes = map(int, partes)
            ano = datetime.now().year
        elif len(partes) == 3:  # DD/MM/AAAA
            dia, mes, ano = map(int, partes)
        else:
            raise ValueError("Formato inválido")
            
        # Criar objeto de data para validação
        data_obj = datetime(ano, mes, dia)
        context.user_data['data'] = data_obj.strftime("%d/%m/%Y")
        
        await update.message.reply_text("✏️ Agora informe a descrição do evento:")
        return DESCRICAO
        
    except (ValueError, TypeError, IndexError):
        await update.message.reply_text(
            "⚠️ *Formato inválido!*\n"
            "Use DD/MM ou DD/MM/AAAA\n"
            "Exemplo: 25/12 ou 25/12/2024\n\n"
            "Por favor, tente novamente:",
            parse_mode='Markdown'
        )
        return DATA

async def receber_descricao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    descricao = update.message.text.strip()
    data = context.user_data['data']
    chat_id = update.effective_chat.id
    
    # Salvar no banco de dados
    add_evento(chat_id, data, descricao)
    
    await update.message.reply_text(
        f"✅ *Evento agendado com sucesso!*\n\n"
        f"📅 Data: {data}\n"
        f"📝 Descrição: {descricao}\n\n"
        "Use /listar para ver todos seus eventos",
        parse_mode='Markdown'
    )
    return ConversationHandler.END

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Operação cancelada.")
    context.user_data.clear()
    return ConversationHandler.END

async def listar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    eventos = list_eventos(chat_id)
    
    if not eventos:
        await update.message.reply_text("📭 Você não tem eventos agendados.")
        return
    
    resposta = "📋 *Seus eventos agendados:*\n\n"
    for idx, (id_evento, data, descricao) in enumerate(eventos, 1):
        resposta += f"{idx}. 📅 *{data}*\n   ➡️ {descricao}\n\n"
    
    await update.message.reply_text(resposta, parse_mode='Markdown')

# NOVA FUNCIONALIDADE: REMOVER EVENTOS
async def remover(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    eventos = list_eventos(chat_id)
    
    if not eventos:
        await update.message.reply_text("📭 Você não tem eventos agendados para remover.")
        return ConversationHandler.END
    
    # Formatar lista de eventos com números
    resposta = "🗑️ *Selecione o evento para remover:*\n\n"
    for idx, (id_evento, data, descricao) in enumerate(eventos, 1):
        resposta += f"{idx}. 📅 *{data}*\n   ➡️ {descricao}\n\n"
    
    resposta += "🔢 *Digite o número do evento que deseja remover:*"
    await update.message.reply_text(resposta, parse_mode='Markdown')
    
    # Armazenar a lista de eventos no contexto para referência
    context.user_data['eventos'] = eventos
    return ESCOLHER_EVENTO

async def receber_escolha_remover(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        escolha = int(update.message.text.strip())
        chat_id = update.effective_chat.id
        eventos = context.user_data['eventos']
        
        # Validar escolha
        if escolha < 1 or escolha > len(eventos):
            await update.message.reply_text(
                f"⚠️ *Número inválido!* Escolha entre 1 e {len(eventos)}\n"
                "Por favor, tente novamente:",
                parse_mode='Markdown'
            )
            return ESCOLHER_EVENTO
        
        # Obter o ID do evento selecionado
        id_evento, data, descricao = eventos[escolha-1]
        
        # Remover do banco de dados
        rows_affected = remove_evento(id_evento, chat_id)
        
        if rows_affected > 0:
            await update.message.reply_text(
                f"✅ *Evento removido com sucesso!*\n\n"
                f"📅 Data: {data}\n"
                f"📝 Descrição: {descricao}",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text("⚠️ Evento não encontrado ou já removido.")
        
        return ConversationHandler.END
        
    except ValueError:
        await update.message.reply_text(
            "⚠️ *Entrada inválida!* Digite apenas o número do evento.\n"
            "Por favor, tente novamente:",
            parse_mode='Markdown'
        )
        return ESCOLHER_EVENTO

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Erro enquanto processava update:", exc_info=context.error)
    await update.message.reply_text("⚠️ Ocorreu um erro inesperado. Tente novamente.")

def main():
    # Verificar se o token foi configurado
    if not TOKEN:
        logger.error("Token não encontrado! Crie um arquivo .env com TELEGRAM_BOT_TOKEN")
        return
    
    # Inicializar banco de dados
    if not os.path.exists(DB_NAME):
        init_db()
    
    # Configurar aplicação
    application = Application.builder().token(TOKEN).build()
    
    # Conversação para agendamento
    conv_handler_agendar = ConversationHandler(
        entry_points=[CommandHandler('agendar', agendar)],
        states={
            DATA: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_data)],
            DESCRICAO: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_descricao)]
        },
        fallbacks=[CommandHandler('cancelar', cancelar)]
    )
    
    # Conversação para remoção
    conv_handler_remover = ConversationHandler(
        entry_points=[CommandHandler('remover', remover)],
        states={
            ESCOLHER_EVENTO: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_escolha_remover)]
        },
        fallbacks=[CommandHandler('cancelar', cancelar)]
    )
    
    # Registrar handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('ajuda', ajuda))
    application.add_handler(CommandHandler('listar', listar))
    application.add_handler(conv_handler_agendar)
    application.add_handler(conv_handler_remover)
    
    # Registrar handler de erros
    application.add_error_handler(error_handler)
    
    # Iniciar bot
    logger.info("Bot iniciado! Pressione Ctrl+C para parar.")
    application.run_polling()

if __name__ == '__main__':
    main()
