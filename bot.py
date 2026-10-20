import discord
from discord.ext import commands
import yt_dlp
import asyncio

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Options de configuration pour yt-dlp (recherche la meilleure qualité audio sans télécharger le fichier)
YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'default_search': 'ytsearch', # Permet de chercher par mot-clé si ce n'est pas un lien direct
}

# Options FFmpeg pour éviter les coupures et assurer un flux super fluide et sans pub
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

@bot.event
async def on_ready():
    print(f"Le bot {bot.user} est prêt à chercher de la musique sans pub !")

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await channel.connect()
        else:
            await ctx.voice_client.move_to(channel)
    else:
        await ctx.send("Tu dois être dans un salon vocal !")

@bot.command()
async def play(ctx, *, search: str):
    """Cherche un titre sur YouTube et le joue instantanément"""
    if not ctx.voice_client:
        await ctx.invoke(join)
        
    async with ctx.typing():
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            try:
                # Cherche le terme écrit par l'utilisateur
                info = ydl.extract_info(f"ytsearch:{search}", download=False)
                if 'entries' in info and len(info['entries']) > 0:
                    info = info['entries'][0]
                else:
                    await ctx.send("Désolé, je n'ai rien trouvé pour cette recherche.")
                    return
                
                # Récupère l'URL brute du flux audio (zéro pub)
                url = info['url']
                title = info['title']
                
                # Arrête la musique en cours si le bot jouait déjà quelque chose
                if ctx.voice_client.is_playing():
                    ctx.voice_client.stop()
                
                # Lance la lecture du flux direct avec FFmpeg
                source = discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS)
                ctx.voice_client.play(source)
                
                await ctx.send(f"🎵 En train de lire : **{title}** (Qualité Max, Sans pub ⚡)")
                
            except Exception as e:
                await ctx.send("Une erreur est survenue lors de la recherche.")
                print(e)

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Musique arrêtée.")

bot.run("MTU2MjA2MzcxMTAzMDc0MzE0MA.GHeJ68.VyFSG0TkFpbNe8Ju1W8PYQ131nrGNnOmvHcdNU
")
