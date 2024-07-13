import discord
from discord.ext import commands


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.remove_command("help")

    @commands.command()
    async def hi(self, ctx):
        await ctx.send("Hello, I'm here!")

    @commands.command(name="help", help="Show available commands", category="Admin")
    async def help_command(self, ctx):
        """
        Display all available commands.
        """
        embed = discord.Embed(
            title="Admin Commands", description="List of available admin commands:"
        )

        for command in self.bot.commands:
            if command.cog_name == "Admin":
                embed.add_field(
                    name=f"{self.bot.command_prefix}{command.name}",
                    value=command.help or "No description available",
                    inline=False,
                )

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Admin(bot))
