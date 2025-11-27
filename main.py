import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext
from supabase import create_client, Client

# ------------------------------
# ENVIRONMENT VARIABLES (Render)
# ------------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ------------------------------
# BASIC COMMAND: /start
# ------------------------------
async def start(update: Update, context: CallbackContext):
    user = update.effective_user

    await update.message.reply_text(
        f"Welcome to Miraplexity Marketplace, {user.first_name}!\n\n"
        "Available commands:\n"
        "/shop - View store items\n"
        "/buy <ItemName> - Purchase items\n"
        "/inventory - View your items\n"
        "/join - Enter the Cyber Pool Cup tournament\n"
    )

# ------------------------------
# SHOP: /shop
# ------------------------------
async def shop(update: Update, context: CallbackContext):
    items = supabase.table("marketplace").select("*").execute()

    if not items.data:
        await update.message.reply_text("Shop is empty.")
        return

    msg = "🏪 *Miraplexity Marketplace*\n\n"
    for item in items.data:
        msg += (
            f"• *{item['name']}*\n"
            f"  Rarity: {item['rarity']}\n"
            f"  Effect: {item['effect']}\n"
            f"  Price: {item['price']}\n\n"
        )

    await update.message.reply_text(msg, parse_mode="Markdown")

# ------------------------------
# BUY: /buy ItemName
# ------------------------------
async def buy(update: Update, context: CallbackContext):
    if len(context.args) == 0:
        await update.message.reply_text("Usage: /buy ItemName")
        return

    item_name = " ".join(context.args)
    user_id = str(update.effective_user.id)

    # Fetch item from marketplace
    item = supabase.table("marketplace").select("*").eq("name", item_name).execute()
    if not item.data:
        await update.message.reply_text("Item not found.")
        return

    # Fetch player wallet
    profile = supabase.table("players").select("*").eq("username", user_id).execute()

    if not profile.data:
        # Create profile if doesn't exist
        supabase.table("players").insert({
            "username": user_id,
            "wallet": 9999,
            "tournament_id": "00000000-0000-0000-0000-000000000000"
        }).execute()
        profile = supabase.table("players").select("*").eq("username", user_id).execute()

    wallet = profile.data[0]["wallet"]
    price = item.data[0]["price"]

    if wallet < price:
        await update.message.reply_text("Not enough money.")
        return

    # Deduct cost
    supabase.table("players").update({
        "wallet": wallet - price
    }).eq("username", user_id).execute()

    # Add item to inventory
    supabase.table("inventory").insert({
        "player_id": profile.data[0]["id"],
        "item_id": item.data[0]["id"],
        "quantity": 1
    }).execute()

    await update.message.reply_text(f"You bought *{item_name}*!", parse_mode="Markdown")

# ------------------------------
# INVENTORY: /inventory
# ------------------------------
async def inventory(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)

    profile = supabase.table("players").select("*").eq("username", user_id).execute()
    if not profile.data:
        await update.message.reply_text("You have no items yet.")
        return

    player_id = profile.data[0]["id"]

    inv = supabase.table("inventory")\
        .select("*, marketplace(name, rarity)")\
        .eq("player_id", player_id)\
        .execute()

    if not inv.data:
        await update.message.reply_text("Your inventory is empty.")
        return

    msg = "🎒 *Your Inventory*\n\n"
    for entry in inv.data:
        msg += f"• {entry['marketplace']['name']} ({entry['marketplace']['rarity']})\n"

    await update.message.reply_text(msg, parse_mode="Markdown")

# ------------------------------
# JOIN TOURNAMENT: /join
# ------------------------------
async def join(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)

    tournaments = supabase.table("tournaments").select("*").execute()

    if not tournaments.data:
        # Create default tournament
        supabase.table("tournaments").insert({
            "name": "Cyber Pool Cup",
            "entry_fee": 10,
            "status": "open",
            "prize_pool": 0
        }).execute()
        tournaments = supabase.table("tournaments").select("*").execute()

    t = tournaments.data[0]

    supabase.table("players").insert({
        "username": user_id,
        "wallet": 500,
        "tournament_id": t["id"]
    }).execute()

    await update.message.reply_text(
        f"You joined *{t['name']}*!",
        parse_mode="Markdown"
    )

# ------------------------------
# RUN BOT
# ------------------------------
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("shop", shop))
    app.add_handler(CommandHandler("buy", buy))
    app.add_handler(CommandHandler("inventory", inventory))
    app.add_handler(CommandHandler("join", join))

    print("Miraplexity Marketplace Bot is running...")
    app.run_polling()
