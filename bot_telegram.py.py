from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import requests

# Función para encontrar los mejores héroes para contrarrestar según un rol
async def heroe_rol(update: Update, context: CallbackContext):
    if len(context.args) < 2:
        await update.message.reply_text(
            "Por favor, proporciona el nombre de un héroe y un rol. Ejemplo: /heroe_rol Axe support"
        )
        return

    input_hero = context.args[0].lower()
    input_role = " ".join(context.args[1:]).lower()  # Concatenar el resto de los argumentos como rol completo

    # Mapear roles personalizados
    role_map = {
        "hard support": "support",  # Mapear "hard support" a "support"
        "offlaner": "offlane",      # Mapear "offlaner" a "offlane"
        "midlaner": "mid"           # Mapear "midlaner" a "mid"
    }

    # Mapear el rol ingresado
    input_role_mapped = role_map.get(input_role, input_role)

    # Roles válidos en OpenDota
    valid_roles = ["carry", "mid", "offlane", "support"]

    # Depuración: Mostrar el rol mapeado
    print(f"Rol ingresado: {input_role}, Rol mapeado: {input_role_mapped}")

    # Validar si el rol mapeado es válido
    if input_role_mapped not in valid_roles:
        await update.message.reply_text(f"Rol no válido. Por favor, elige entre: {', '.join(valid_roles)}")
        return

    url_hero_stats = "https://api.opendota.com/api/heroStats"
    
    try:
        response = requests.get(url_hero_stats)
        if response.status_code == 200:
            heroes = response.json()
            target_hero = next((h for h in heroes if h["localized_name"].lower() == input_hero), None)
            
            if not target_hero:
                await update.message.reply_text(f"No se encontró información para el héroe: {input_hero.capitalize()}")
                return
            
            hero_id = target_hero["id"]
            url_matchups = f"https://api.opendota.com/api/heroes/{hero_id}/matchups"
            response_matchups = requests.get(url_matchups)
            
            if response_matchups.status_code == 200:
                matchups = response_matchups.json()
                role_filtered_heroes = [
                    h for h in heroes if input_role_mapped in [r.lower() for r in h["roles"]]
                ]
                counters = sorted(
                    [(h["localized_name"], matchup["wins"] / matchup["games_played"] * 100) 
                     for matchup in matchups 
                     for h in role_filtered_heroes if h["id"] == matchup["hero_id"]],
                    key=lambda x: x[1], reverse=True
                )[:5]
                
                if counters:
                    message = f"Mejores héroes con rol '{input_role}' para contrarrestar a {target_hero['localized_name']}:\n"
                    message += "\n".join([f"- {c[0]} (Winrate: {c[1]:.2f}%)" for c in counters])
                else:
                    message = f"No se encontraron héroes con el rol '{input_role}' que sean efectivos contra {target_hero['localized_name']}."
                
                await update.message.reply_text(message)
            else:
                await update.message.reply_text("No se pudo obtener información de los matchups.")
        else:
            await update.message.reply_text("No se pudo obtener información de la API de OpenDota.")
    except Exception as e:
        await update.message.reply_text(f"Error al obtener datos: {e}")

# Configuración del bot
TOKEN = "7043154200:AAFY8JChkv-_d5ji1Qullr6Hkjj2X1rzFDw"  # Reemplaza con tu token de BotFather
application = Application.builder().token(TOKEN).build()

# Agregar comandos al bot
application.add_handler(CommandHandler("heroe_rol", heroe_rol)) # Comando para counters por rol

# Iniciar el bot
print("El bot está en funcionamiento...")
application.run_polling()







