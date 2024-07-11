import discord
import os
import requests
import json
import aiohttp
import asyncio
import string
import random
from colorama import Fore, Style
from discord.ext import commands
from discord import app_commands
from discord_webhook import DiscordWebhook, DiscordEmbed  # Import necessary from discord_webhook
from datetime import datetime, timedelta, timezone

# Create a directory for backups if it doesn't exist
if not os.path.exists('backups'):
    os.makedirs('backups')



intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# Define forbidden keywords and banned links
forbidden_keywords = ["idiot", "stupid", "bitch", "retard", "scam", "scammer", "paste", "skid", "sk!d", "p&ste", "paster"]  # Replace with your list of forbidden keywords
banned_links = ["dsc.gg", "discord.gg", ".gg/"]  # Links to block

failed_users_file = "failed_users.json"

def load_failed_users():
    try:
        with open(failed_users_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_failed_users(failed_users):
    with open(failed_users_file, 'w') as f:
        json.dump(failed_users, f)

GUILD_ID = 1259908161364693114  # Example guild ID

# Webhook URL - Replace with your actual webhook URL
webhook_url = "https://discord.com/api/webhooks/1259943453475868724/JRCjtMmaxGZGq1M0ci4M1qIlFTH2_llYmt5nzDLf5gWgR0LE3WfBOsMqtthAOz0P6k85"

# MADE BY MOCHA 

# // The Bot's Status & Events. 

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

    # Sync slash commands
    synced_commands = await bot.tree.sync()
    print(f"Synced {len(synced_commands)} slash commands")

    for cmd in synced_commands:
        print(f"Synchronized command: {cmd.name}")  # Print each synchronized command

    # Update presence and handle reconnects
    await update_presence()

async def update_presence():
    try:
        await bot.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.playing, name="Predicting Stake by BetGenius!"))
    except discord.ConnectionClosed as e:
        print(f"Connection closed: {e}")
        await bot.close()
        await bot.start('YOUR_BOT_TOKEN')  # Replace with your bot token
    except Exception as e:
        print(f"Error updating presence: {e}")
    else:
        print("Presence updated successfully")

    # Schedule the next presence update
    await asyncio.sleep(60)  # Update presence every minute
    await update_presence()

@bot.event
async def on_member_join(member):
    welcome_embed = discord.Embed(
        title="Welcome to BetGenius™",
        description=(
            "Hello! Welcome to our Discord server. We're glad to have you here.\n"
            "Here are some things you might want to do first:\n\n"
            "> Before u start doing anything, u should VERIFY. \n> with restorecord bot to get role \n \n<:betgeniusdiscord:1259931788042702939> VERIFY-> ||[CLICK HERE TO VERIFY](https://restorecord.com/verify/BetGenius%E2%84%A2)||  \n\n "
            "**1.** Read the server rules. \n <:betgeniusarrow:1259931792706637956> <#1259943251721588839>\n"
            "**2.** Check our new latest updates.  \n <:betgeniusarrow:1259931792706637956> <#1259919629686538250>\n"
            "**3.** Check our cheap products on market \n <:betgeniusarrow:1259931792706637956> <#1259919837296332810>\n"
            "**4.** If you have any questions, feel free to ask in the ticket channel for support."
        ),
        color=0x0857b7
    )
    welcome_embed.set_thumbnail(url="https://i.imgur.com/SE4pWXt.png")  # URL obrázku pro embed

    try:
        await member.send(embed=welcome_embed)
    except discord.Forbidden:
        print(f"Cannot send welcome message to {member.name}")

# // input your User ID & Seller key | I Added a Fake one so Please Replace it.

allowed_user_ids = [1231148493062672394, 771037994354343956] # can include more than one
seller_key = "e4023df2776caccddb7f32c40518b0cf"

# // Generate Command, SLASH COMMAND
# // the Duration value is in Days!
product_details = {
    "predict": {"mask": "BetGenius™-PREDICT-******", "level": 1}

}
@bot.tree.command(name="generate", description="Generate a Product key")
@app_commands.choices(
    product=[
        app_commands.Choice(name="BetGenius Predictor", value="predict")
    ],
    duration=[
        app_commands.Choice(name="1 Day", value="1"),
        app_commands.Choice(name="3 Days", value="3"),
        app_commands.Choice(name="1 Week", value="7"),
        app_commands.Choice(name="1 Month", value="30"),
        app_commands.Choice(name="Lifetime", value="9999")
    ]
)
async def generate(interaction: discord.Interaction, product: str, duration: str, user: discord.Member):
    await interaction.response.defer(ephemeral=True)

    if interaction.user.id not in allowed_user_ids:
        await interaction.followup.send("You do not have access to generate keys.", ephemeral=True)
        return

    details = product_details[product]
    mask = details["mask"]
    level = details["level"]

    url = f"https://keyauth.win/api/seller/?sellerkey={seller_key}&type=add&expiry={duration}&mask={mask}&level={level}&amount=1&format=text"
    response = requests.get(url)
    key = response.text.upper()

    embed = discord.Embed(
        title="BetGenius | Key Generated",
        description=f"Your Key for `{product}` is:\n ```{key}```\n > Duration: `{duration}` Days\n > User: `{user.mention}` \n > Who Generated: `{interaction.user.mention}`",
        color=0x0857b7  # Change the color to your desired hex value
    )
    embed.set_footer(text="Made by BetGenius!")
    embed.set_thumbnail(url="https://i.imgur.com/SE4pWXt.png")  # Add your thumbnail URL here
    embed.set_image(url="https://i.imgur.com/tnpJCKH.gif")  # Add your image URL here

    # Send the Generated key to the user via DM
    await user.send(embed=embed)

    # Send the embed message to the webhook
    await send_to_webhook(embed)

    # Send a confirmation message to the original interaction
    await interaction.followup.send("The key has been generated and sent to the user via DM.", ephemeral=True)

async def send_to_webhook(embed):
    webhook = DiscordWebhook(url=webhook_url, username="BetGenius")

    # Convert Embed object to a dictionary
    embed_dict = embed.to_dict()

    # Create a new DiscordEmbed object from the dictionary
    discord_embed = DiscordEmbed(
        title=embed_dict.get('title', None),
        description=embed_dict.get('description', None),
        color=embed_dict.get('color', None)
        # Add other attributes as needed
    )

    # Set footer, thumbnail, and image if available
    footer = embed_dict.get('footer', {})
    if footer:
        discord_embed.set_footer(text=footer.get('text', None))

    thumbnail = embed_dict.get('thumbnail', {})
    if thumbnail:
        discord_embed.set_thumbnail(url=thumbnail.get('url', None))

    image = embed_dict.get('image', {})
    if image:
        discord_embed.set_image(url=image.get('url', None))

    # Add the DiscordEmbed object to the webhook
    webhook.add_embed(discord_embed)

    try:
        response = webhook.execute()
        print(f"Webhook response: {response}")  # Optionally print response for debugging
    except Exception as e:
        print(f"Failed to send webhook: {e}")



# MADE BY MOCHA # MADE BY MOCHA  # MADE BY MOCHA  # MADE BY MOCHA  

# RESET COMMAND 
@bot.tree.command(name="reset-key", description="HWID resets a key!")
async def reset_key(interaction: discord.Interaction, key: str):
    await interaction.response.defer()

    if interaction.user.id not in allowed_user_ids:
        await interaction.followup.send("Access Denied.")
        return

    url = f"https://keyauth.win/api/seller/?sellerkey={seller_key}&type=resetuser&user={key}"
    hwid_response = requests.get(url)
    hwid_message = hwid_response.json()["message"]

    reset_embed = discord.Embed(
       title="Medusa Auth | Key Reset",
       description="Key Reset Successful...\n Process exit with Code 200",
       color=0x0857b7  # Change the color to your desired hex value
   )
    reset_embed.set_footer(text="Made by Medusa!")
    reset_embed.set_thumbnail(url="https://i.imgur.com/SE4pWXt.png")  # Add your thumbnail URL here
    reset_embed.set_image(url="https://i.imgur.com/tnpJCKH.gif")  # Add your image URL here

    await interaction.followup.send(embed=reset_embed)

    # Send the embed message to the webhook
    await send_to_webhook(reset_embed)


# // Delete key.
@bot.tree.command(name="delete-key", description="Delete's a key.")
async def delete_key(interaction: discord.Interaction, key: str):
    await interaction.response.defer()

    if interaction.user.id not in allowed_user_ids:
        await interaction.followup.send("Access Denied.")
        return

    url = f"https://keyauth.win/api/seller/?sellerkey={seller_key}&type=del&key={key}"
    response = requests.get(url)
    message = response.json()["message"]

    delete_embed = discord.Embed(
        title="BetGenius Auth | Key Deleted",
        description=f"Key Deleted Successful...\n Process exit with Code 200",
        color=0x0857b7  # Change the color to your desired hex value
    )
    delete_embed.set_footer(text="Made by BetGenius!")
    delete_embed.set_thumbnail(url="https://i.imgur.com/SE4pWXt.png")  # Add your thumbnail URL here
    delete_embed.set_image(url="https://i.imgur.com/tnpJCKH.gif")  # Add your image URL here

    await interaction.followup.send(embed=delete_embed)

    # Send the embed message to the webhook
    await send_to_webhook(delete_embed)

# Název souboru, do kterého budeme ukládat
FILENAME = "activated_keys.json"

# Načtení aktivovaných klíčů ze souboru
def load_activated_keys():
    try:
        with open(FILENAME, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Funkce pro uložení aktivovaných klíčů do souboru
def save_activated_keys(activated_keys):
    with open(FILENAME, 'w') as f:
        json.dump(activated_keys, f, indent=4)  # Pro lepší čitelnost uložení jako formátovaný JSON


# Načtení aktivovaných klíčů při startu aplikace
activated_keys = load_activated_keys()
# Příkaz pro aktivaci produktového klíče
@bot.tree.command(name="activate", description="Activate a product key")
async def activate(interaction: discord.Interaction, key: str):
    await interaction.response.defer()

    # Check if key is already activated
    activated_keys = load_activated_keys()
    if key in activated_keys:
        await interaction.followup.send("This key has already been activated.")
        return

    # Verify the key using the API
    url = f"https://keyauth.win/api/seller/?sellerkey={seller_key}&type=info&key={key}"
    response = requests.get(url)
    key_info = response.json()

    try:
        if key_info.get("success"):
            level = int(key_info["level"])
            duration = key_info.get("duration")  # Get duration from API response

            # Mapping between level and role IDs
            role_ids = {
                1: 1259920362674720838  # PREDICT role ID
            }

            member = interaction.guild.get_member(interaction.user.id)
            role_id = role_ids.get(level)

            if role_id:
                role = interaction.guild.get_role(role_id)
                if role:
                    await member.add_roles(role)

                    # Get current UTC time as activation time
                    activation_time = datetime.now(timezone.utc).isoformat()

                    # Calculate expiry date based on activation time and duration
                    if duration is not None:
                        duration_seconds = int(duration)
                        expiry_date = (datetime.now(timezone.utc) + timedelta(seconds=duration_seconds)).isoformat()
                    else:
                        expiry_date = None

                    # Save key information to activated_keys dictionary
                    activated_keys[key] = {
                        "role_id": role.id,
                        "user_id": interaction.user.id,
                        "activation_time": activation_time,
                        "duration": duration,
                        "expiry_date": expiry_date
                    }

                    # Save updated activated keys to storage
                    save_activated_keys(activated_keys)

                    # Create and send embed message with role information
                    embed = discord.Embed(
                        title="BetGenius | Role Added",
                        description=f"Your role {role.mention} was added from key: ||```HIDDEN LOL```||",
                        color=0x0857b7
                    )
                    embed.set_footer(text="Made by BetGenius!")
                    embed.set_thumbnail(url="https://i.imgur.com/SE4pWXt.png")

                    await interaction.followup.send(embed=embed)

                    # Send embed message to webhook
                    await send_to_webhook(embed)
                else:
                    await interaction.followup.send("Role not found.")
            else:
                await interaction.followup.send("Invalid key level.")
        else:
            await interaction.followup.send("Invalid key or API response.")
    except KeyError as e:
        await interaction.followup.send(f"Error processing API response: {str(e)}")

# Instructions command
@bot.tree.command(name="instructions", description="Show instructions for using the bot")
async def instructions(interaction: discord.Interaction):
    await interaction.response.defer()

    embed = discord.Embed(
        title="BetGenius Instructions <:robotgg:1259975868739223604>",
        description="Here are the instructions for using BetGenius:",
        color=0x0857b7
    )
    embed.add_field(
        name="**1.** Activate product key",
        value="<:betgeniusarrow:1259931792706637956> Activate a product key to receive the Predictor role.",
        inline=False
    )
    embed.add_field(
        name="**2.** Get ROUND_ID from MyStake",
        value="<:betgeniusarrow:1259931792706637956> Retrieve the ROUND_ID from your current round on MyStake.",
        inline=False
    )
    embed.add_field(
        name="**3.** Play Miner or Towers",
        value="<:betgeniusarrow:1259931792706637956> Use the appropriate command for the game you want to play: \n",
        inline=False
    )
    embed.add_field(
        name="**/Miner:**",
        value="<:betgeniusarrow:1259931792706637956> /miner tiles: <number_of_tiles> round_id: <ROUND_ID>",
        inline=False
    )
    embed.add_field(
        name="**/Towers:**",
        value="<:betgeniusarrow:1259931792706637956> /towers round_id: <ROUND_ID>",
        inline=False
    )

    await interaction.followup.send(embed=embed)


# Simulace rolí a přístupových práv
allowed_roles = {
    'PREDICTOR': 1259920362674720838,
 
}

@bot.tree.command(name='ban', description='Ban a user with license and reason')
async def ban(interaction: discord.Interaction, user: discord.Member, license: str, reason: str):
    # Zde můžete provádět další ověření oprávnění, například zda máte správné role nebo oprávnění k banování uživatelů.

    try:
        # Provedení banu uživatele
        await user.ban(reason=reason)

        # Zpráva o úspěšném banu
        await interaction.response.send_message(f"{user.name} has been banned with license: {license}. Reason: {reason}", ephemeral=True)
    except discord.Forbidden:
        # Pokud nemůžete provést ban (např. nedostatek oprávnění)
        await interaction.response.send_message("I do not have permission to ban users.", ephemeral=True)
    except discord.HTTPException as e:
        # V případě jakéhokoli HTTPException (např. špatný request)
        await interaction.response.send_message(f"Failed to ban {user.name}. Error: {e}", ephemeral=True)

@bot.tree.command(name='broadcast', description='Sends an embed message to all server members.')
@app_commands.checks.has_permissions(administrator=True)
async def broadcast(interaction: discord.Interaction, message: str):
    broadcast_embed = discord.Embed(
        title="BetGenius NEWS",
        description=message,
        color=0x0857b7
    )

    failed_users = load_failed_users()

    for member in interaction.guild.members:
        if not member.bot:
            try:
                await member.send(embed=broadcast_embed)
            except discord.Forbidden:
                failed_users[member.id] = member.name

    save_failed_users(failed_users)

    await interaction.response.send_message("Broadcast message sent to all members.", ephemeral=True)

@broadcast.error
async def broadcast_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
    else:
        await interaction.response.send_message(f"An error occurred: {error}", ephemeral=True)


@bot.tree.command(name='broadcast_no_member', description='Sends an embed message to all server members without the Member role.')
@app_commands.checks.has_permissions(administrator=True)
async def broadcast_no_member(interaction: discord.Interaction, message: str):
    broadcast_embed = discord.Embed(
        title="BetGenius™ Announcer!",
        description=f"{message}\n\nIt looks like you are still not verified in our server, let's change it 💙 \n <:betgeniusdiscord:1259931788042702939> VERIFY-> ||[CLICK HERE TO VERIFY](https://restorecord.com/verify/BetGenius%E2%84%A2)|| " ,
        color=0x0857b7
    )

    failed_users = load_failed_users()
    member_role_id = 1259920315400585339

    for member in interaction.guild.members:
        if not member.bot and member_role_id not in [role.id for role in member.roles]:
            try:
                await member.send(embed=broadcast_embed)
            except discord.Forbidden:
                failed_users[member.id] = member.name

    save_failed_users(failed_users)

    await interaction.response.send_message("Broadcast message sent to all members without the Member role.", ephemeral=True)

@broadcast_no_member.error
async def broadcast_no_member_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
    else:
        await interaction.response.send_message(f"An error occurred: {error}", ephemeral=True)


def check_round_id_format(round_id):
    # Odstranění všech pomlček z round_id
    round_id = round_id.replace('-', '')

    # Kontrola, zda round_id má formát xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
    if len(round_id) == 32:
        return True
    return False
def save_generated_prediction(round_id, predicted_layout, client_seed=None):
    file_path = 'generated_pred.json'

    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = {"predictions": []}  # Handle case where file is empty or corrupted
    else:
        data = {"predictions": []}

    prediction_entry = {
        "round_id": round_id,
        "predicted_layout": predicted_layout
    }

    if client_seed:
        prediction_entry["client_seed"] = client_seed

    data["predictions"].append(prediction_entry)

    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

# Funkce pro nastavení Client Seed
async def set_client_seed(interaction: discord.Interaction, client_seed: str):
    # Zde by měl být kód pro kontrolu a nastavení Client Seed
    # Například uložení do databáze, případně kontroly validity
    await interaction.response.send_message(f"Client Seed set to: {client_seed}", ephemeral=True)

# Registrování příkazu /seed
@bot.tree.command(name="seed", description="Set the Client Seed for predictions")
@app_commands.checks.has_role(1259920362674720838)  # Nahraďte tímto skutečným ID rolí
async def set_seed(interaction: discord.Interaction, client_seed: str):
    await interaction.response.defer()

    # Zde můžete přidat další kontroly validity client_seed
    # Například kontrola, zda je client_seed ve správném formátu

    await set_client_seed(interaction, client_seed)

# Ošetření chyb pro příkaz /seed
@set_seed.error
async def seed_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.errors.MissingRole):
        await interaction.response.send_message("You do not have the required role to use this command.", ephemeral=True)
    else:
        await interaction.response.send_message("An error occurred while executing the command.", ephemeral=True)

def save_manual_result(round_id, correct_layout):
    file_path = 'game_results.json'
    
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
    else:
        data = {"games": []}
    
    data["games"].append({
        "round_id": round_id,
        "correct_layout": correct_layout
    })
    
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def load_game_results():
    file_path = 'game_results.json'

    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data["games"]
    else:
        return []

def analyze_results():
    results = load_game_results()

    grid_size = 5
    frequency_matrix = [[0 for _ in range(grid_size)] for _ in range(grid_size)]

    for result in results:
        layout = result["correct_layout"]
        for row in range(grid_size):
            for col in range(grid_size):
                if layout[row][col] == "❌":
                    frequency_matrix[row][col] += 1

    total_games = len(results)
    if total_games == 0:
        return [[0 for _ in range(grid_size)] for _ in range(grid_size)]

    probability_matrix = [[frequency / total_games for frequency in row] for row in frequency_matrix]

    return probability_matrix

@bot.tree.command(name="mines", description="Generates a mines game embed")
@app_commands.checks.has_role(1259920362674720838)  # Nahraďte tímto skutečným ID rolí
async def mines(interaction: discord.Interaction, tiles: int, round_id: str):
    await interaction.response.defer()

    # Kontrola formátu round_id
    if not check_round_id_format(round_id):
        await interaction.followup.send("Invalid round_id format. Expected format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
        return

    # Načítání správných layoutů z game_results.json
    game_results = load_game_results()
    correct_layouts = {result["round_id"]: result["correct_layout"] for result in game_results}

    # Vytvoření 5x5 mřížky
    grid = [["❌" for _ in range(5)] for _ in range(5)]

    # Náhodné umístění '✅' na mřížce na základě tiles
    positions = random.sample(range(25), min(tiles, 25))
    for pos in positions:
        row = pos // 5
        col = pos % 5
        grid[row][col] = "✅"

    # Ukládání predikce do generated_pred.json
    save_generated_prediction(round_id, ["".join(row) for row in grid])

    grid_str = "\n".join(["".join(row) for row in grid])

    # Výpočet úspěšného poměru na základě počtu '✅'
    total_tiles = 25
    successful_tiles = min(tiles, 25)
    success_rate = f"{(successful_tiles / total_tiles) * 100:.0f}%"

    mines_embed = discord.Embed(
        title=f"Mines Game - Round {round_id}",
        color=0x0857b7  # Změňte barvu na požadovanou hex hodnotu
    )
    mines_embed.add_field(name="<a:betgeniusgg:1259956737235095592> Mines Predicted:", value=f"```{grid_str}```", inline=False)
    mines_embed.add_field(name="<:success:1259957019780321390> Success Rate:", value=f"```{success_rate}```", inline=False)
    mines_embed.add_field(name="<:roundfly:1259957018274566155> Round Identifier:", value=f"```{round_id}```", inline=False)
    mines_embed.add_field(name="\n \nAdditional Information:", value="`The Results May Not Always Be A Winning Hit, \n Please Note These Are Predictions Calculated From Multiple Game Data & Loss Ratio`", inline=False)
    mines_embed.set_footer(text="Made by BetGenius!")
    mines_embed.set_thumbnail(url="https://i.imgur.com/SE4pWXt.png")  # Přidejte URL náhledu zde
    mines_embed.set_image(url="https://i.imgur.com/tnpJCKH.gif")  # Přidejte URL obrázku zde

    await interaction.followup.send(embed=mines_embed)

# Error handling for mines command
@mines.error
async def mines_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.errors.MissingRole):
        await interaction.response.send_message("You do not have the required role to use this command.", ephemeral=True)
    else:
        await interaction.response.send_message("An error occurred while executing the command.", ephemeral=True)

@bot.tree.command(name="save_result", description="Saves the correct layout for a mines game round")
@app_commands.checks.has_role(1259920362674720838)  # Nahraďte tímto skutečným ID rolí
async def save_result(interaction: discord.Interaction, round_id: str, correct_layout: str):
    await interaction.response.defer()

    # Rozdělení vstupního correct_layout podle čárek a odstranění mezer
    rows = correct_layout.split(",")
    clean_rows = [row.strip() for row in rows]

    # Kontrola formátu correct_layout
    if len(clean_rows) != 5 or any(len(row) != 5 for row in clean_rows):
        await interaction.followup.send("Invalid layout format. Each row must contain exactly 5 values separated by commas.")
        return

    # Příprava dat pro uložení do JSON souboru s ikonami namísto kódů Unicode
    game_data = {
        "round_id": round_id,
        "correct_layout": clean_rows
    }

    # Načtení stávajících dat, pokud existují
    try:
        with open("game_results.json", "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {"games": []}

    # Přidání nové hry do seznamu her
    data["games"].append(game_data)

    # Uložení aktualizovaných dat zpět do JSON souboru
    with open("game_results.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    await interaction.followup.send(f"Game result for round {round_id} successfully saved.")

# Error handling for save_result command
@save_result.error
async def save_result_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.errors.MissingRole):
        await interaction.response.send_message("You do not have the required role to use this command.", ephemeral=True)
    else:
        await interaction.response.send_message("An error occurred while executing the command.", ephemeral=True)



@bot.tree.command(name="towers", description="Generates a towers game embed")
@app_commands.checks.has_role(1259920362674720838)  # Nahraďte tímto skutečným ID rolí
async def towers(interaction: discord.Interaction, round_id: str):
    await interaction.response.defer()

    # Kontrola formátu round_id
    if not check_round_id_format(round_id):
        await interaction.followup.send("Invalid round_id format. Expected format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
        return

    # Vytvoření 8x3 mřížky
    grid = [["❌" for _ in range(3)] for _ in range(8)]
    
    # Náhodné umístění '✅' na mřížce
    positions = random.sample(range(24), random.randint(1, 24))  # Náhodný výběr mezi 1 a 24 pozicemi
    for pos in positions:
        row = pos % 8
        col = pos // 8
        grid[row][col] = "✅"

    grid_str = "\n".join(["".join(row) for row in grid])

    # Výpočet úspěšného poměru na základě počtu '✅'
    total_tiles = 24
    success_rate = f"{(len(positions) / total_tiles) * 100:.0f}%"

    towers_embed = discord.Embed(
        title=f"Towers Game - Round {round_id}",
        color=0x0857b7  # Změňte barvu na požadovanou hex hodnotu
    )
    towers_embed.add_field(name="<a:betgeniusgg:1259956737235095592> Towers Predicted:", value=f"```{grid_str}```", inline=False)
    towers_embed.add_field(name="<:success:1259957019780321390> Success Rate:", value=f"```{success_rate}```", inline=False)
    towers_embed.add_field(name="<:roundfly:1259957018274566155> Round Identifier:", value=f"```{round_id}```", inline=False)
    towers_embed.add_field(name="\n \nAdditional Information:", value="`The Results May Not Always Be A Winning Hit, \n Please Note These Are Predictions Calculated From Multiple Game Data & Loss Ratio`", inline=False)
    towers_embed.set_footer(text="Made by BetGenius!")
    towers_embed.set_thumbnail(url="https://i.imgur.com/SE4pWXt.png")  # Přidejte URL náhledu zde
    towers_embed.set_image(url="https://i.imgur.com/tnpJCKH.gif")  # Přidejte URL obrázku zde

    await interaction.followup.send(embed=towers_embed)

# Error handling for towers command
@towers.error
async def towers_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.errors.MissingRole):
        await interaction.response.send_message("You do not have the required role to use this command.", ephemeral=True)
    else:
        await interaction.response.send_message("An error occurred while executing the command.", ephemeral=True)

# Load activated keys from JSON file
def load_activated_keys():
    with open('activated_keys.json', 'r') as f:
        return json.load(f)

# Save activated keys to JSON file
def save_activated_keys(activated_keys):
    with open('activated_keys.json', 'w') as f:
        json.dump(activated_keys, f, indent=4)

@bot.tree.command(name="expiry", description="Check and remove roles based on key expiration")
@commands.has_permissions(administrator=True)
async def expiry(interaction: discord.Interaction):
    # Defer the initial response to prevent timeouts
    await interaction.response.defer()

    # Load activated keys
    activated_keys = load_activated_keys()

    # Current datetime in UTC
    current_datetime = datetime.now(timezone.utc)

    # Set to store users whose roles were removed
    users_roles_removed = set()

    # Create a list of keys to remove (to avoid modifying the dictionary during iteration)
    keys_to_remove = []

    # Check expiration for each activated key
    for key, details in activated_keys.items():
        expiry_date_str = details.get("expiry_date")

        if not expiry_date_str:
            continue

        # Convert expiry date from string to datetime object
        expiry_date = datetime.fromisoformat(expiry_date_str)

        # If expiry date is less than current datetime, remove roles
        if expiry_date < current_datetime:
            user_id = details["user_id"]
            role_id = details["role_id"]

            guild = interaction.guild
            member = guild.get_member(user_id)
            role = guild.get_role(role_id)

            if member and role:
                # Remove role from the user
                await member.remove_roles(role)
                users_roles_removed.add(member.display_name)

                # Send DM to the user
                try:
                    embed_dm = discord.Embed(
                        title="Predictor - Information",
                        description=f"Your Subscription Expired - Thank you for purchasing.\nHere is your discount on future purchase: ```PREDICTOR20```\nDiscount 20%",
                        color=0x0857b7  # Change color as needed
                    )
                    await member.send(embed=embed_dm)
                except Exception as e:
                    print(f"Failed to send DM to {member.display_name}: {e}")

            # Add the key to keys_to_remove list
            keys_to_remove.append(key)

    # Remove expired keys from activated_keys
    for key in keys_to_remove:
        del activated_keys[key]

    # Save updated activated keys to storage
    save_activated_keys(activated_keys)

    # Create embed message with information about removed roles
    if users_roles_removed:
        embed = discord.Embed(
            title="Role Removed due to Key Expiry",
            description=f"Roles were removed for the following users:\n\n- {', '.join(users_roles_removed)}",
            color=0x0857b7  # Change color as needed
        )
        await interaction.followup.send(embed=embed)
    else:
        await interaction.followup.send("No roles were removed.")

@expiry.error
async def expiry_error(interaction: discord.Interaction, error: Exception):
    if isinstance(error, commands.MissingPermissions):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
    else:
        await interaction.response.send_message(f"An error occurred: {error}", ephemeral=True)



def get_backup_choices():
    """Returns a list of backup choices from the backups directory."""
    backup_dirs = [d for d in os.listdir('backups') if os.path.isdir(os.path.join('backups', d))]
    backup_choices = []

    for backup_dir in backup_dirs:
        backup_files = [f for f in os.listdir(os.path.join('backups', backup_dir)) if f.endswith('.json')]
        for backup_file in backup_files:
            timestamp = backup_file.split('_')[1].split('.')[0]
            formatted_name = f"{backup_dir} | {timestamp}"
            backup_choices.append(app_commands.Choice(name=formatted_name, value=f"{backup_dir}/{timestamp}"))
    
    return backup_choices

async def create_backup(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    guild = interaction.guild
    guild_name = guild.name.replace(" ", "_")  # Replace spaces with underscores
    backup_dir = f"backups/{guild_name}"
    
    # Ensure the directory exists
    os.makedirs(backup_dir, exist_ok=True)
    
    # Create a unique filename with the current date and time in the new format
    timestamp = datetime.now().strftime("%Y%m%d-%H.%M.%S")
    backup_id = f"backup_{timestamp}"
    backup_filename = f"{backup_dir}/{backup_id}.json"

    backup_data = {
        "name": guild.name,
        "emoji": [emoji.name for emoji in guild.emojis],  # Save emoji names
        "roles": [],
        "channels": [],
        "settings": {
            "verification_level": guild.verification_level,
            "default_notifications": guild.default_notifications,
            "explicit_content_filter": guild.explicit_content_filter
        }
    }

    # Save roles
    for role in guild.roles:
        backup_data["roles"].append({
            "name": role.name,
            "permissions": role.permissions.value,
            "color": role.color.value,
            "hoist": role.hoist,
            "position": role.position,
            "managed": role.managed,
            "mentionable": role.mentionable
        })

    # Save channels
    for channel in guild.channels:
        channel_info = {
            "name": channel.name,
            "type": str(channel.type),
            "position": channel.position,
            "topic": channel.topic if isinstance(channel, discord.TextChannel) else None,
            "nsfw": channel.is_nsfw() if isinstance(channel, discord.TextChannel) else None,
            "bitrate": channel.bitrate if isinstance(channel, discord.VoiceChannel) else None,
            "user_limit": channel.user_limit if isinstance(channel, discord.VoiceChannel) else None,
            "category": channel.category.name if isinstance(channel, discord.TextChannel) and channel.category else None
        }
        backup_data["channels"].append(channel_info)

    # Save emojis
    # Create backup_dir/emojis folder if it doesn't exist
    emojis_dir = f"{backup_dir}/emojis"
    os.makedirs(emojis_dir, exist_ok=True)

    for emoji in guild.emojis:
        extension = 'gif' if emoji.animated else 'png'
        emoji_save_path = f'{emojis_dir}/{emoji.name}.{extension}'  # Save by name
        async with aiohttp.ClientSession() as session:
            async with session.get(emoji.url) as resp:
                if resp.status == 200:
                    with open(emoji_save_path, 'wb') as f:
                        f.write(await resp.read())

    # Save server icon (if available)
    if guild.icon:
        images_dir = f"{backup_dir}/images"
        icon_save_path = f'{images_dir}/server_icon.png'
        os.makedirs(images_dir, exist_ok=True)
        async with aiohttp.ClientSession() as session:
            async with session.get(guild.icon.url) as resp:
                if resp.status == 200:
                    with open(icon_save_path, 'wb') as f:
                        f.write(await resp.read())
        backup_data["logo_url"] = guild.icon.url  # Store URL for loading backup

    # Check for boost level and apply vanity link
    if guild.premium_tier >= 3 and guild.vanity_url_code:
        backup_data["vanity_url"] = guild.vanity_url_code

    with open(backup_filename, 'w') as f:
        json.dump(backup_data, f, indent=4)

    embed = discord.Embed(
        title="🟢 Success",
        description=f"```/backup action:Load backup_id: {guild_name} | {timestamp}```",
        color=0x00ff00  # Green color
    )
    await interaction.followup.send(embed=embed, ephemeral=True)
    await interaction.user.send(embed=embed)  # Send the embed to the user as a direct message

async def load_backup(interaction: discord.Interaction, backup_id: str):
    await interaction.response.defer(ephemeral=True)

    guild_name, timestamp = backup_id.split(' | ')
    guild_name = guild_name.replace(" ", "_")
    backup_file = f"backup_{timestamp}.json"
    backup_path = f'backups/{guild_name}/{backup_file}'

    try:
        with open(backup_path, 'r') as f:
            backup_data = json.load(f)
    except FileNotFoundError:
        await interaction.followup.send("Backup not found.", ephemeral=True)
        return

    guild = interaction.guild

    # Restore roles
    role_mapping = {}
    for role_data in backup_data["roles"]:
        role = await guild.create_role(
            name=role_data["name"],
            permissions=discord.Permissions(role_data["permissions"]),
            color=discord.Color(role_data["color"]),
            hoist=role_data["hoist"],
            mentionable=role_data["mentionable"]
        )
        role_mapping[role_data["name"]] = role

    # Restore channels
    for channel_data in backup_data["channels"]:
        if channel_data["type"] == "category":
            await guild.create_category(
                name=channel_data["name"],
                position=channel_data["position"]
            )
        elif channel_data["type"] == "text":
            category = discord.utils.get(guild.categories, name=channel_data["category"]) if channel_data["category"] else None
            await guild.create_text_channel(
                name=channel_data["name"],
                category=category,
                position=channel_data["position"],
                topic=channel_data["topic"],
                nsfw=channel_data["nsfw"]
            )
        elif channel_data["type"] == "voice":
            category = discord.utils.get(guild.categories, name=channel_data["category"]) if channel_data["category"] else None
            await guild.create_voice_channel(
                name=channel_data["name"],
                category=category,
                position=channel_data["position"],
                bitrate=channel_data["bitrate"],
                user_limit=channel_data["user_limit"]
            )

    # Restore emojis
    emojis_folder = f'backups/{guild_name}/emojis'
    for emoji_name in backup_data["emoji"]:  # Use backed-up emoji names
        emoji_file_path = f'{emojis_folder}/{emoji_name}.png'
        if not os.path.exists(emoji_file_path):  # Check for animated emoji
            emoji_file_path = f'{emojis_folder}/{emoji_name}.gif'
        try:
            with open(emoji_file_path, 'rb') as f:
                emoji_bytes = f.read()
            await guild.create_custom_emoji(name=emoji_name, image=emoji_bytes)
        except FileNotFoundError:
            continue  # Skip if the emoji file doesn't exist

    # Restore guild name, logo/banner, and emoji
    if backup_data.get("logo_url"):
        icon_path = f'backups/{guild_name}/images/server_icon.png'
        with open(icon_path, 'rb') as f:
            icon_bytes = f.read()
        await guild.edit(name=backup_data["name"], icon=icon_bytes)

    # Apply vanity URL if available and boost level is sufficient
    if "vanity_url" in backup_data and guild.premium_tier >= 3:
        try:
            await guild.edit(vanity_code=backup_data["vanity_url"])
        except discord.errors.Forbidden:
            pass  # Handle if bot doesn't have permission to edit vanity URL

    embed = discord.Embed(
        title="🟢 Success",
        description=f"Successfully loaded backup with the id `{backup_id}`.",
        color=0x00ff00  # Green color
    )
    await interaction.followup.send(embed=embed, ephemeral=True)

@bot.tree.command(name="backup", description="Create or load a server backup")
@app_commands.choices(
    action=[
        app_commands.Choice(name="Create", value="create"),
        app_commands.Choice(name="Load", value="load")
    ]
)
@app_commands.describe(
    action="Action to perform",
    backup_id="ID of the backup to load (required for Load action)"
)
async def backup(interaction: discord.Interaction, action: app_commands.Choice[str], backup_id: str = None):
    if action.value == 'create':
        await create_backup(interaction)
    elif action.value == 'load' and backup_id:
        await load_backup(interaction, backup_id)
    else:
        if action.value == 'load' and not backup_id:
            await interaction.response.send_message("You must provide a backup ID to load.", ephemeral=True)
        else:
            await interaction.response.send_message("Invalid action.", ephemeral=True)

@backup.autocomplete("backup_id")
async def backup_id_autocomplete(interaction: discord.Interaction, current: str):
    backups = get_backup_choices()
    return [option for option in backups if current.lower() in option.name.lower()]

@backup.error
async def backup_error(interaction: discord.Interaction, error: Exception):
    if not interaction.response.is_done():
        await interaction.response.send_message(f"An error occurred: {error}", ephemeral=True)
    else:
        await interaction.followup.send(f"An error occurred: {error}", ephemeral=True)




@bot.tree.command(name="delete_all", description="Delete all text and voice channels on the server")
@commands.has_permissions(administrator=True)
async def delete_all(ctx):
    """Deletes all text and voice channels on the server."""
    for channel in ctx.guild.channels:
        await channel.delete()
    await ctx.send('All channels have been deleted.')


@bot.tree.command(name="nuke", description="Delete all messages in the current text channel")
@commands.has_permissions(administrator=True)
async def nuke(ctx):
    """Deletes all messages in the current text channel."""
    await ctx.channel.purge(limit=None)
    await ctx.send('Nuked this channel!', delete_after=5)


@bot.event
async def on_message(message):
    if message.author.bot:
        return  # Ignore messages from bots

    content = message.content.lower()

   # Kontrola zakázaných slov
    for keyword in forbidden_keywords:
        if keyword in content:
            await message.delete()
            embed = discord.Embed(
                title="⚠️ WARN",
                description=f"{message.author.mention}, your message was deleted for containing a forbidden keyword.",
                color=discord.Color.orange()
            )
            await message.author.send(embed=embed)  # Zpráva je poslána jako DM
            return

    await bot.process_commands(message)

  # Kontrola zakázaných odkazů
    for link in banned_links:
        if link in content:
            await message.delete()
            embed = discord.Embed(
                title="⚠️ WARN",
                description=f"{message.author.mention}, posting links to {link} is not allowed in this server.",
                color=discord.Color.orange()
            )
            await message.author.send(embed=embed)  # Zpráva je poslána jako DM
            return

    await bot.process_commands(message)

bot.run("MTI1OTk0MjI1OTA3NjUwMTYzNQ.GmrRjl.4aANYlePKyNGXSkMI1ETVYCrNhdWOLM-26zbco") # // replace with the actual bot token.
