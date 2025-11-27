import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# in-memory tables
tournaments = {
    "4": {"players": [], "buyin": 10, "payouts": [30], "max": 4},   # $40 in, $30 out, $10 profit
    "8": {"players": [], "buyin": 20, "payouts": [100, 40], "max": 8},  # $160 in, $140 out, $20 profit
}

profit_total = 0

def uname(update: Update):
    u = update.effective_user
    return u.username or f"{u.first_name}_{u.id}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎱 Miraplexity Pool Tournaments\n\n"
        "Commands:\n"
        "/join4 - Join 4-player $10 table\n"
        "/join8 - Join 8-player $20 table\n"
        "/paid - Confirm payment\n"
        "/winner <username> - Set winner\n"
        "/winner2 <username> - Set 2nd place (8-player only)\n"
        "/tables - Show tables\n"
        "/profit - Show today's profit"
    )

async def join4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = uname(update)
    t = tournaments["4"]
    if user in t["players"]:
        return await update.message.reply_text("You're already in the 4-player table.")
    if len(t["players"]) >= t["max"]:
        return await update.message.reply_text("4-player table is full.")
    t["players"].append(user)
    await update.message.reply_text(f"@{user} joined the 4-player table ({len(t['players'])}/4).\nSend $10 to Cash App and type /paid")

async def join8(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = uname(update)
    t = tournaments["8"]
    if user in t["players"]:
        return await update.message.reply_text("You're already in the 8-player table.")
    if len(t["players"]) >= t["max"]:
        return await update.message.reply_text("8-player table is full.")
    t["players"].append(user)
    await update.message.reply_text(f"@{user} joined the 8-player table ({len(t['players'])}/8).\nSend $20 to Cash App and type /paid")

async def paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = uname(update)
    await update.message.reply_text(
        f"💵 @{user} marked as PAID.\nHost will verify on Cash App."
    )

async def winner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global profit_total
    if not context.args:
        return await update.message.reply_text("Use: /winner <username>")
    winner_name = context.args[0].lstrip("@")
    for size, t in tournaments.items():
        if winner_name in t["players"]:
            total_in = len(t["players"]) * t["buyin"]
            payout = t["payouts"][0]
            house_profit = total_in - payout
            profit_total += house_profit
            await update.message.reply_text(
                f"🏆 Winner: @{winner_name}\n"
                f"Payout: ${payout}\n"
                f"House profit: ${house_profit}"
            )
            t["players"].clear()
            return
    await update.message.reply_text("That user is not in any table.")

async def winner2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Use: /winner2 <username>")
    winner_name = context.args[0].lstrip("@")
    t = tournaments["8"]
    if winner_name not in t["players"]:
        return await update.message.reply_text("That user is not on the 8-player table.")
    await update.message.reply_text(
        f"🥈 Second place: @{winner_name}\n"
        f"Payout: ${t['payouts'][1]}"
    )

async def tables(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "🎱 Current Tables:"
    for size, t in tournaments.items():
        msg += f"\n\n{size}-PLAYER ({len(t['players'])}/{t['max']}):\n"
        if t["players"]:
            for p in t["players"]:
                msg += f" • @{p}\n"
        else:
            msg += " (empty)\n"
    await update.message.reply_text(msg)

async def profit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"💰 Total house profit: ${profit_total}")

if __name__ == "__main__":
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("join4", join4))
    app.add_handler(CommandHandler("join8", join8))
    app.add_handler(CommandHandler("paid", paid))
    app.add_handler(CommandHandler("winner", winner))
    app.add_handler(CommandHandler("winner2", winner2))
    app.add_handler(CommandHandler("tables", tables))
    app.add_handler(CommandHandler("profit", profit))
    print("Miraplexity Tournament Bot LIVE")
    app.run_polling()
