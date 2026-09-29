"""Wiki commands: player-facing role/faction win-condition reference."""
import discord
from discord import app_commands
from discord.ext import commands

from wiki import ROLE_WIKI, FACTION_WIKI


def _overview_embed():
    embed = discord.Embed(
        title=":books: Murder Mystery Wiki",
        description=(
            "Pick a role or faction below to see its ability and win "
            "condition. Use the dropdown, or `!wiki <role>` / "
            "`/wiki role:<role>` to jump straight to one."
        ),
        color=0x00b8ff,
    )
    faction_lines = "\n".join(
        f"{data['emoji']} **{data['name']}** \u2014 {data['win']}"
        for data in FACTION_WIKI.values()
    )
    embed.add_field(name="Factions", value=faction_lines, inline=False)
    role_lines = "\n".join(
        f"{data['emoji']} {data['fancyName']}" for data in ROLE_WIKI.values()
    )
    embed.add_field(name="Roles", value=role_lines, inline=False)
    return embed


def _role_embed(role_key):
    data = ROLE_WIKI[role_key]
    embed = discord.Embed(
        title=f"{data['emoji']} {data['fancyName']}",
        color=0x00b8ff,
    )
    embed.add_field(name="Ability", value=data["ability"], inline=False)
    embed.add_field(name="Win condition", value=data["win"], inline=False)
    embed.add_field(
        name="Availability",
        value=data.get("availability", "Always in every game."),
        inline=False,
    )
    return embed


def _faction_embed(faction_key):
    data = FACTION_WIKI[faction_key]
    embed = discord.Embed(
        title=f"{data['emoji']} {data['name']}",
        color=0x00b8ff,
    )
    embed.add_field(name="Win condition", value=data["win"], inline=False)
    return embed


class WikiView(discord.ui.View):
    """Dropdown for browsing factions and roles without re-running the command."""

    def __init__(self):
        super().__init__(timeout=120)
        options = [
            discord.SelectOption(label="Overview", value="overview:", emoji="\U0001F4D6")
        ]
        for key, data in FACTION_WIKI.items():
            options.append(
                discord.SelectOption(label=data["name"][:100], value=f"faction:{key}")
            )
        for key, data in ROLE_WIKI.items():
            options.append(
                discord.SelectOption(label=data["fancyName"][:100], value=f"role:{key}")
            )
        select = discord.ui.Select(
            placeholder="Choose a role or faction",
            options=options[:25],
        )
        select.callback = self._on_select
        self.add_item(select)

    async def _on_select(self, interaction: discord.Interaction):
        value = interaction.data["values"][0]
        kind, _, key = value.partition(":")
        if kind == "role":
            embed = _role_embed(key)
        elif kind == "faction":
            embed = _faction_embed(key)
        else:
            embed = _overview_embed()
        await interaction.response.edit_message(embed=embed, view=self)


def _resolve_lookup(name):
    """Match a free-typed role/faction name to a wiki entry, embed pair."""
    if not name:
        return _overview_embed()
    key = name.strip().lower()
    if key in ROLE_WIKI:
        return _role_embed(key)
    if key in FACTION_WIKI:
        return _faction_embed(key)
    return None


_ROLE_CHOICES = [
    app_commands.Choice(name=data["fancyName"], value=key)
    for key, data in ROLE_WIKI.items()
] + [
    app_commands.Choice(name=data["name"], value=key)
    for key, data in FACTION_WIKI.items()
]


class WikiCommands(commands.Cog):
    """`!wiki` / `/wiki` role and faction reference."""

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def wiki(self, ctx, *, role: str = None):
        """Show role/faction abilities and win conditions."""
        if role is None:
            await ctx.send(embed=_overview_embed(), view=WikiView())
            return
        embed = _resolve_lookup(role)
        if embed is None:
            await ctx.send(embed=discord.Embed(
                title=":x: Unknown role or faction",
                description="Use `!wiki` with no argument to browse the full list.",
                color=0xff0000,
            ))
            return
        await ctx.send(embed=embed, view=WikiView())

    @app_commands.command(name="wiki", description="Show role/faction abilities and win conditions")
    @app_commands.choices(role=_ROLE_CHOICES[:25])
    async def slash_wiki(self, interaction: discord.Interaction, role: app_commands.Choice[str] = None):
        if role is None:
            await interaction.response.send_message(embed=_overview_embed(), view=WikiView())
            return
        embed = _resolve_lookup(role.value)
        await interaction.response.send_message(embed=embed, view=WikiView())


async def setup(client):
    """Setup function for cog."""
    await client.add_cog(WikiCommands(client))
