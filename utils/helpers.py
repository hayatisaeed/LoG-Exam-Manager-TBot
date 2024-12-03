from db.db_setup import get_db_session
from db.models import User


async def check_user_role(update, context, allowed_roles):
    user_id = str(update.effective_user.id)

    with get_db_session() as session:
        user = session.query(User).filter_by(user_id=user_id).first()

        if not user:
            await update.message.reply_text("You are not registered. Contact an admin.")
            return False

        if user.role not in allowed_roles:
            await update.message.reply_text(f"Unauthorized! Allowed roles: {', '.join(allowed_roles)}.")
            return False

    return True
