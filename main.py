import nextcord
from nextcord.ext import commands, application_checks
from json import dump,load
import unidecode
from os import listdir, mkdir, getcwd, path



class Dataset:
    def __init__(self, name):
        self.data = {}
        self.name = name
        return
    

    def add_data(self,id,content):
        self.data[id] = content
        return self.data
    

    def remove_data(self,id):
        self.data.pop(id)
        return self.data
    

    def load_data(self,file):
        with open(f'data/{file}.json', 'r') as f:
            self.data = load(f)
            f.close()
        return
    

    def save_data(self,file):
        with open(f'data/{file}.json', 'w') as f:
            dump(self.data, f)
            f.close()
        return

class data:
    def __init__(self):
        self.datasets = {}
        return
    

    def add_dataset(self,dataset:Dataset):
        self.datasets[dataset.name] = dataset
        print(f"Datasets {self.datasets}")
        return self.datasets
    

    def delete_dataset(self,dataset:Dataset):
        self.datasets.pop(dataset.name)
        return self.datasets


datas = data()


def get_token():
    with open("token.bin", mode = "rb") as f:
        token = f.readline()
        f.close()
    return token.decode('utf-8')


bot = commands.Bot()


@bot.event
async def on_raw_reaction_add(payload):
    user = payload.member
    if not user == bot.user:
        message_id = payload.message_id
        guild_id = payload.guild_id
        guild_roles_messages = datas.datasets[str(guild_id)]
        if str(message_id) in guild_roles_messages.data:
            guild = await bot.fetch_guild(guild_id)
            role_to_assign = guild.get_role(int(guild_roles_messages.data[str(message_id)][payload.emoji.name]))
            try:
                await user.add_roles(role_to_assign)
            except Exception as e:
                print(e)
                pass


@bot.event
async def on_raw_reaction_remove(payload):
    message_id = payload.message_id
    guild_id = payload.guild_id
    guild_roles_messages = datas.datasets[str(guild_id)]
    if str(message_id) in guild_roles_messages.data:
        guild = await bot.fetch_guild(guild_id)
        user = await guild.fetch_member(payload.user_id)
        role_to_unassign = guild.get_role(int(guild_roles_messages.data[str(message_id)][payload.emoji.name]))
        try:
            await user.remove_roles(role_to_unassign)
        except Exception as e:
            print(e)
            pass

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    global datas
    try:
        for file in listdir(path.join(getcwd(),"data")):
            if file.endswith(".json"):
                filename = file.replace(".json","")
                print(f"got file {filename}.json")
                _tmp = Dataset(filename)
                _tmp.load_data(filename)
                datas.add_dataset(_tmp)
    except FileNotFoundError:
        mkdir("data")
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


@application_checks.has_permissions(administrator = True)
@bot.slash_command(description="Créer un message afin d'assigner des roles")
async def rolemsg(interaction :nextcord.Interaction, message:str = nextcord.SlashOption(required=True), emotes:str = nextcord.SlashOption(required=True), roles:str = nextcord.SlashOption(required=True)):
    try:
        global datas
        print(datas.datasets)
        await interaction.send("Création...")
        print(emotes, roles)
        emotes = emotes.split(",")
        roles = roles.replace("<","")
        roles = roles.replace(">","")
        roles = roles.replace("&","")
        roles = roles.replace("@","")
        roles = roles.replace(" ","")
        roles = roles.split(",")
        channel = bot.get_channel(interaction.channel_id)
        msg = await channel.send(message)
        assignTable = {}
        for emote,role in zip(emotes,roles):
            print(emote)
            await msg.add_reaction(emote)
            assignTable[emote] = str(role)
        print(assignTable)
        print(msg.guild.id)
        print(msg.id)
        print()
        if str(msg.guild.id) not in datas.datasets.keys():
            print("coucou")
            _tmp = Dataset(str(msg.guild.id))
            _tmp.add_data(str(msg.id),assignTable)
            _tmp.save_data(msg.guild.id)
            datas.add_dataset(_tmp)
        else:
            _tmp = datas.datasets[str(msg.guild.id)]
            _tmp.add_data(str(msg.id),assignTable)
            _tmp.save_data(msg.guild.id)
    except Exception as error:
        print(error)
        await interaction.send(f"Erreur: {error}")
        return


@application_checks.has_permissions(administrator = True)
@bot.slash_command(description="Arrête le bot")
async def stop(interaction = nextcord.Interaction):
    await interaction.send("Arrêt en cours...")
    quit()


bot.run(get_token())