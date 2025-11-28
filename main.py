import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# In-memory player storage
players = []

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to the Miraplexity Quick Tournament!\n"
        "Use /join to enter.\n"
        "Use /players to see who joined.\n"
        "Use /winner to pick the winner."
    )

# /join command
async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.first_name or "Player"
    if user not in players:
        players.append(user)
        await update.message.reply_text(f"{user} joined the tournament!")
    else:
        await update.message.reply_text(f"{user}, you're already in!")

# /players command
async def players_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not players:
        await update.message.reply_text("No players yet.")
        return

    output = "\n".join(f"{i+1}. {p}" for i, p in enumerate(players))
    await update.message.reply_text("Current players:\n" + output)

# /winner command
async def winner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not players:
        await update.message.reply_text("No players to choose from.")
        return

    # Pick 1st player by order they joined
    win = players[0]
    await update.message.reply_text(f"The winner is: {win} 🏆")
    players.clear()

# MAIN BOT START
async def main():
    token = os.environ["TELEGRAM_BOT_TOKEN"]

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("join", join))
    app.add_handler(CommandHandler("players", players_list))
    app.add_handler(CommandHandler("winner", winner))

    print("Bot is live.")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
