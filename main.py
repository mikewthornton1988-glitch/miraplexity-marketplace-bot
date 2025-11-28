import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)
from supabase import create_client, Client

# ------------------------------------------------------
# ENVIRONMENT VARIABLES (Render)
# ------------------------------------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

CASHAPP = "$MichaelThornton40"

# ------------------------------------------------------
# BASIC START COMMAND
# ------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to Miraplexity Marketplace & Cyber Pool Cup!\n\n"
        "Commands:\n"
        "/join4 – Join $10 4-Player\n"
        "/join8 – Join $10 8-Player\n"
        "/paid – Mark your buy-in as paid\n"
        "/tables – Show active players\n"
        "/winner <id> – Set winner\n"
        "/profit – Show system profit\n\n"
        "Marketplace:\n"
        "/shop – View items\n"
        "/buy <item> – Buy item\n"
        "/inventory – Your items\n\n"
        f"Buy-ins are paid through CashApp: {CASHAPP}"
    )

# ------------------------------------------------------
# TOURNAMENT COMMANDS
# ------------------------------------------------------
async def join4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    supabase.table("players").insert({
        "user_id": user.id,
        "username": user.username,
        "table": "4player",
        "paid": False
    }).execute()

    await update.message.reply_text(
        f"You joined the $10 4-Player Table!\n\n"
        f"Send $10 to {CASHAPP}\n"
        f"Then type /paid"
    )

async def join8(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    supabase.table("players").insert({
        "user_id": user.id,
        "username": user.username,
        "table": "8player",
        "paid": False
    }).execute()

    await update.message.reply_text(
        f"You joined the $10 8-Player Table!\n\n"
        f"Send $10 to {CASHAPP}\n"
        f"Then type /paid"
    )

async def paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    supabase.table("players").update({"paid": True}).eq("user_id", user_id).execute()

    await update.message.reply_text("Payment verified! You are locked in.")

async def show_tables(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = supabase.table("players").select("*").execute().data

    if not data:
        await update.message.reply_text("No players yet.")
        return

    msg = "Active Players:\n\n"
    for p in data:
        msg += f"{p['user_id']} | {p['username']} | {p['table']} | Paid: {p['paid']}\n"

    await update.message.reply_text(msg)

async def winner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /winner <user_id>")
        return

    winner_id = context.args[0]

    supabase.table("winners").insert({
        "winner_id": winner_id,
        "amount": 30
    }).execute()

    await update.message.reply_text(
        f"Winner set: {winner_id}\n"
        f"Paid out $30."
    )

async def profit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    players = supabase.table("players").select("*").execute().data
    winners = supabase.table("winners").select("*").execute().data

    total_buyins = len(players) * 10
    total_payouts = len(winners) * 30
    net = total_buyins - total_payouts

    await update.message.reply_text(
        f"Total Buy-ins: ${total_buyins}\n"
        f"Payouts: ${total_payouts}\n"
        f"Net Profit: ${net}"
    )

# ------------------------------------------------------
# MARKETPLACE
# ------------------------------------------------------
async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Items for sale:\n"
        "spin – 100 coins\n"
        "boost – 300 coins\n"
        "skin – 500 coins\n\n"
        "Buy with /buy spin"
    )

async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /buy <item>")
        return

    item = context.args[0]
    user_id = update.effective_user.id

    supabase.table("inventory").insert({
        "user_id": user_id,
        "item": item
    }).execute()

    await update.message.reply_text(f"You purchased {item}!")

async def inventory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    items = supabase.table("inventory").select("*").eq("user_id", user_id).execute().data

    if not items:
        await update.message.reply_text("Your inventory is empty.")
        return

    msg = "Your Inventory:\n\n"
    for item in items:
        msg += f"- {item['item']}\n"

    await update.message.reply_text(msg)

# ------------------------------------------------------
# RUN BOT (THE CORRECT WAY FOR PTB 20.6)
# ------------------------------------------------------
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Tournament Commands
    app.add_handler(CommandHandler("join4", join4))
    app.add_handler(CommandHandler("join8", join8))
    app.add_handler(CommandHandler("paid", paid))
    app.add_handler(CommandHandler("tables", show_tables))
    app.add_handler(CommandHandler("winner", winner))
    app.add_handler(CommandHandler("profit", profit))

    # Marketplace Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("shop", shop))
    app.add_handler(CommandHandler("buy", buy))
    app.add_handler(CommandHandler("inventory", inventory))

    print("Miraplexity Beast Mode Bot is running...")
    app.run_polling()
