from db.db_setup import get_db_session
from db.models import User
from utils.helpers import check_user_role


async def show_users(update, context):
    with get_db_session() as session:
        users = session.query(User).all()
        user_list = "\n".join([f"{user.name} ({user.role})" for user in users])
        await update.message.reply_text(f"Users:\n{user_list}")
