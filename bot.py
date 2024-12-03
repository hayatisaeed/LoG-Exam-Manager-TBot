from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from db.db_setup import get_db_session
from db.models import User
from config import BOT_TOKEN

from modules import admin, teacher, student, exam


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    with get_db_session() as session:
        user = session.query(User).filter_by(user_id=user_id).first()

    if not user:
        await update.message.reply_text(
            "Welcome to the Exam Bot! You are not registered in the system. Contact an administrator."
        )
    else:
        await update.message.reply_text(f"Welcome back, {user.name}! Your role is {user.role}.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Available commands:\n/start - Start the bot\n/help - Get help")  # normal user
    await update.message.reply_text("""Available commands:\n/start - Start the bot\n/help - Get help\n
    
    """)


async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if the user is authorized
    if not await check_user_role(update, context, allowed_roles=["admin"]):
        return  # Terminate if not authorized

    if len(context.args) < 3:
        await update.message.reply_text("Usage: /add_user <user_id> <name> <role>")
        return

    user_id, name, role = context.args[0], context.args[1], context.args[2]
    with get_db_session() as session:
        new_user = User(user_id=user_id, name=name, role=role)
        session.add(new_user)
        session.commit()
        await update.message.reply_text(f"User {name} added as {role}.")


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("users", admin.show_users))
    app.add_handler(CommandHandler("add_user", add_user))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
