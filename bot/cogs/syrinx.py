import discord
from discord import ButtonStyle
from discord.ext import commands, tasks
from config import Config
import logging

logging.basicConfig(
    filename="bot.log",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
)


class SyrinxButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        custom_id="click_button",
        label="Click here",
        style=ButtonStyle.primary,
        emoji="🏳️",
    )
    async def on_click(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        reg_view = discord.ui.View()
        reg_view.add_item(
            discord.ui.Button(
                style=ButtonStyle.link,
                label="Register Now",
                emoji="🔗",
                url="https://syrinx.ccstiet.com/",
            )
        )
        collection = Config.mongo_client["2024_ctf"]["users"]
        user = collection.find_one({"discordID": str(interaction.user.name)})

        if user:
            teamID_binary = user.get("teamID")

            if teamID_binary:
                team_collection = Config.mongo_client["2024_ctf"]["teams"]
                team = team_collection.find_one({"teamID": teamID_binary})

                if team:
                    team_name = team["teamName"]
                    role = discord.utils.get(interaction.guild.roles, name=team_name)

                    if role:
                        try:
                            await interaction.user.add_roles(role)
                            await interaction.response.send_message(
                                f"You have been assigned to team {team_name}. Please use the provided channels for communication.",
                                ephemeral=True,  # Only visible to the user
                            )
                        except discord.Forbidden:
                            await interaction.response.send_message(
                                "I don't have permission to assign roles! Please contact Core.",
                                ephemeral=True,
                            )
                    else:
                        await interaction.response.send_message(
                            f"Role '{team_name}' not found in the server! Please wait atleast for 5 minutes for the role to be created or contact Core.",
                            ephemeral=True,
                        )
                else:
                    await interaction.response.send_message(
                        "Team information not found! Please make sure to register yourself for SYRINX from the SYRINX portal and wait for 5 minutes for the team to be created or contact Core.",
                        ephemeral=True,
                        view=reg_view,
                    )
            else:
                await interaction.response.send_message(
                    "TeamID not found or invalid format in user document! Please contact Core.",
                    ephemeral=True,
                )
        else:
            await interaction.response.send_message(
                "User information not found! Please make sure to register yourself on SYRINX Portal and use the same Discord username that you provided in the form.",
                ephemeral=True,
                view=reg_view,
            )


class Syrinx(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mongo_client = Config.mongo_client
        self.create_event_loop.start()
        self.handle_event_message.start()
        self.bot.add_view(SyrinxButton())
        self.guild_id = 768959556012736544
        self.channel_id = 1261631290671890474

    def cog_unload(self):
        self.create_event_loop.cancel()

    @tasks.loop(count=1)
    async def handle_event_message(self):
        await self.send_event_message()

    async def send_event_message(self):
        print("Sending event message")
        guild = self.bot.get_guild(self.guild_id)
        if not guild:
            logging.warning("Guild not found. Aborting on_ready task.")
            return

        channel: discord.TextChannel = guild.get_channel(self.channel_id)
        if not channel:
            logging.warning("Channel not found in guild. Aborting on_ready task.")
            return

        if channel.last_message_id == 1261637362098634822:
            return
        embed = discord.Embed(
            title="Welcome to Syrinx!",
            description="You are required to join your team on Discord to participate in the event. You would be provided with a role to access your team's channels (voice and text). Click the button below to join your team.",
            colour=0xF8CF1A,
        )

        embed.add_field(
            name="You are required to use the same Discord username that you provided in the form to register for the event.",
            value="Also make sure to only use the provided channels for communication.",
            inline=False,
        )

        embed.set_thumbnail(url="https://syrinx.ccstiet.com/logo.png")

        embed.set_footer(text="Contact Core if you have any issues.")

        await channel.send(embed=embed, view=SyrinxButton())

    @tasks.loop(minutes=5)
    async def create_event_loop(self):
        await self.create_event_entities()

    async def create_event_entities(self):
        channel_id = 1261630295371681832
        guild: discord.Guild = self.bot.get_guild(self.guild_id)
        if not guild:
            logging.warning("Guild not found. Aborting create_event_entities task.")
            return

        collection = self.mongo_client["2024_ctf"]["teams"]
        teams = collection.find()

        logging.info("Creating event channels and roles")

        total_created_teams = 0

        for team in teams:
            category_exists = any(
                team["teamName"] in category.name for category in guild.categories
            )

            if category_exists:
                continue

            try:
                role = await guild.create_role(
                    name=team["teamName"], reason="Syrinx Role"
                )
                category = await guild.create_category(
                    f"╭──・{team['teamName']}", reason="Syrinx Category"
                )

                await category.set_permissions(guild.default_role, view_channel=False)

                role = guild.get_role(role.id)

                await category.set_permissions(
                    role,
                    view_channel=True,
                    read_messages=True,
                    send_messages=True,
                    read_message_history=True,
                    connect=True,
                    speak=True,
                )

                await category.create_text_channel(f"📝・{team['teamName']}")
                await category.create_voice_channel(f"🔊・{team['teamName']} VC")

                total_created_teams += 1

                logging.info(f"Created category and role for {team['teamName']}")

            except Exception as e:
                logging.error(f"Error creating entities for {team['teamName']}: {e}")

        if total_created_teams > 0:
            await guild.get_channel(channel_id).send(
                embed=discord.Embed(
                    title="Event Channels Created",
                    description="Event channels and roles created successfully!",
                    color=discord.Color.green(),
                )
                .add_field(
                    name="Teams Created Now",
                    value=str(total_created_teams),
                    inline=False,
                )
                .add_field(
                    name="Total Teams",
                    value=str(collection.count_documents({})),
                    inline=False,
                )
            )
        else:
            await guild.get_channel(channel_id).send(
                embed=discord.Embed(
                    title="Event Channels Created",
                    description="No new event channels created",
                    color=discord.Color.green(),
                ).add_field(
                    name="Total Teams",
                    value=str(collection.count_documents({})),
                    inline=False,
                )
            )
            total_created_teams = 0

    @commands.command()
    @commands.has_any_role(768960824009162802, 1254871511056257144)
    async def delete_event_entities(self, ctx):
        guild: discord.Guild = ctx.guild
        reason_role = "Syrinx Role"
        reason_category = "Syrinx Category"

        logging.info("Deleting event channels and roles")

        embed = discord.Embed(
            title="Deleting Event Channels and Roles",
            description="Deleting event channels and roles",
            color=discord.Color.red(),
        )

        message = await ctx.send(embed=embed)

        async for action in guild.audit_logs(action=discord.AuditLogAction.role_create):
            if action.reason == reason_role:
                role = guild.get_role(action.target.id)
                if role:
                    await role.delete()
                    logging.info(f"Deleted role: {role.name}")

        async for action in guild.audit_logs(
            action=discord.AuditLogAction.channel_create
        ):
            if (
                action.reason == reason_category
                and action.target.type == discord.ChannelType.category
            ):
                category = guild.get_channel(action.target.id)
                if category:
                    for channel in category.channels:
                        await channel.delete()
                    await category.delete()
                    logging.info(f"Deleted channels and category: {category.name}")

        await message.edit(
            embed=discord.Embed(
                title="Event Channels Deleted",
                description="Event channels and roles deleted successfully!",
                color=discord.Color.green(),
            )
        )


async def setup(bot):
    await bot.add_cog(Syrinx(bot))
