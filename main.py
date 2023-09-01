import nextcord
from nextcord.ext import commands, application_checks
from json import dump,load
import unidecode


data = ""
role_messages = {}


def get_token():
    with open("token.bin", mode = "rb") as f:
        token = f.readline()
        f.close()
    return token.decode('utf-8')


def save_to_data(payload, keyname:str):
    with open("./data/data.json","w+")as file :
        dump(data, file)
        file.close()
    return


bot = commands.Bot()


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    global data
    try:
        with open("./data/data.json","r") as f:
            data = load(f)
            f.close()
    except FileNotFoundError:
        pass
    return


@bot.slash_command(description="test pour savoir si le bot est on.")
async def test(interaction: nextcord.Interaction):
    await interaction.send("Online")

@bot.slash_command(description="S'assigner un role de classe")
async def assignerclasse(interaction: nextcord.Interaction, group:str = nextcord.SlashOption(required=True)):
    if group.upper() > 'D':
        await interaction.send("E: Les groupes sont forcément A, B, C ou D")
    else:
        try:
            roles_id = {"A":1146771605746368672,"B":1146771791595982928,"C":1146771338153963581,"D":1146771504730742866}
            role_id = roles_id[group.upper()]
            await interaction.user.add_roles(interaction.user.guild.get_role(role_id))
            await interaction.send("I: Opération réalisée avec succès")
        except Exception as e:
            print(e)


@bot.slash_command(description="Activer/Désactiver les catégories facultatives")
async def role(interaction: nextcord.Interaction, categorie: str = nextcord.SlashOption(required=True)):
    categorie = unidecode.unidecode(categorie)
    if categorie.lower() not in ["jeux","soirees","aide"]:
        await interaction.send("E: La catégorie doit être Jeux, Soirees, Aide.")
        return
    roles_id = {"jeux":1146878452117545032,"aide":1146878574272458902,"soirees":1146878503422267443}
    user = interaction.user
    role = interaction.user.guild.get_role(roles_id[categorie.lower()])
    if role in user.roles:
        await user.remove_roles(role)
        await interaction.send(f"I: Rôle {role.name} Retiré")
    else:
        await user.add_roles(role)
        await interaction.send(f"I: Rôle {role.name} Ajouté")


bot.run(get_token())