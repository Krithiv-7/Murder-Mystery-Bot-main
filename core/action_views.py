"""Buttons and selects for private night actions."""

from types import SimpleNamespace

import discord


class TargetSelectView(discord.ui.View):
    """Pick a player or role by menu instead of typing an index."""

    def __init__(self, role_obj, options):
        super().__init__(timeout=300)
        self.role_obj = role_obj
        select = discord.ui.Select(
            placeholder="Choose a target",
            options=options[:25],
            min_values=1,
            max_values=1,
        )
        select.callback = self.chosen
        self.add_item(select)

    async def chosen(self, interaction: discord.Interaction):
        if interaction.user.id != self.role_obj.player.member.id:
            await interaction.response.send_message(
                "Only you can use this action.", ephemeral=True
            )
            return
        choice = interaction.data["values"][0]
        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(view=self)
        fake = SimpleNamespace(content=choice, author=interaction.user)
        await self.role_obj.processRoleChannelCommand(fake)


def player_select(role_obj):
    players = getattr(role_obj, "currentPlayerList", None) or []
    options = [
        discord.SelectOption(
            label=player.member.display_name[:100],
            value=str(index),
            description=f"Option {index}",
        )
        for index, player in enumerate(players[:25])
    ]
    if not options:
        return None
    return TargetSelectView(role_obj, options)


def role_select(role_obj):
    roles = getattr(role_obj, "currentRolesList", None) or []
    options = [
        discord.SelectOption(label=item.fancyName[:100], value=str(index))
        for index, item in enumerate(roles[:24])
    ]
    options.append(
        discord.SelectOption(label="Everyone", value=str(len(roles)), description="Broadcast to every role")
    )
    return TargetSelectView(role_obj, options)


class HealView(discord.ui.View):
    """Doctor choice after the murderer attacks."""

    def __init__(self, doctor_role):
        super().__init__(timeout=300)
        self.doctor_role = doctor_role

    async def _answer(self, interaction, answer):
        if interaction.user.id != self.doctor_role.player.member.id:
            await interaction.response.send_message(
                "Only the doctor can make this choice.", ephemeral=True
            )
            return
        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(view=self)
        fake = SimpleNamespace(content=answer, author=interaction.user)
        await self.doctor_role.processRoleChannelCommand(fake)

    @discord.ui.button(label="Heal them", style=discord.ButtonStyle.success)
    async def heal(self, interaction, button):
        await self._answer(interaction, "yes")

    @discord.ui.button(label="Let them die", style=discord.ButtonStyle.danger)
    async def decline(self, interaction, button):
        await self._answer(interaction, "no")


GUILD_PERMISSIONS = 137439332416


def guild_invite_url(application_id: int) -> str:
    """Server install link. applications.commands is included in the scope."""
    return (
        "https://discord.com/oauth2/authorize"
        f"?client_id={application_id}&permissions={GUILD_PERMISSIONS}"
        "&integration_type=0&scope=applications.commands+bot"
    )


def user_install_url(application_id: int) -> str:
    """User-install link. This is what lets the bot DM someone."""
    return (
        "https://discord.com/oauth2/authorize"
        f"?client_id={application_id}&integration_type=1&scope=applications.commands"
    )


def application_id(guild) -> int | None:
    me = getattr(guild, "me", None)
    app_id = getattr(me, "id", None)
    return int(app_id) if app_id else None


def dm_link_view(application_id: int) -> discord.ui.View:
    view = discord.ui.View(timeout=None)
    view.add_item(
        discord.ui.Button(
            label="Allow DMs from this bot",
            style=discord.ButtonStyle.link,
            url=user_install_url(application_id),
        )
    )
    return view
