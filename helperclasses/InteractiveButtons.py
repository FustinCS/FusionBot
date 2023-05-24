import discord

class ButtonView(discord.ui.View):
    def __init__(self, embed: list):
        super().__init__(timeout=60)
        self.embeds = embed
        self.count = 0

    @discord.ui.button(label="<--", style=discord.ButtonStyle.blurple, custom_id="prev", disabled=True)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.count -= 1
        if self.count == 0:
            button1 = [x for x in self.children if x.custom_id == "next"][0]
            button1.disabled = False
            button.disabled = True
            await interaction.response.edit_message(embed=self.embeds[self.count], view=self)
        elif self.count > 0:
            button1 = [x for x in self.children if x.custom_id == "next"][0]
            button1.disabled = False
            await interaction.response.edit_message(embed=self.embeds[self.count], view=self)

    @discord.ui.button(label="-->", style=discord.ButtonStyle.blurple, custom_id="next", disabled=False)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.count += 1
        if self.count < len(self.embeds)-1:
            button1 = [x for x in self.children if x.custom_id == "prev"][0]
            button1.disabled = False
            await interaction.response.edit_message(embed=self.embeds[self.count], view=self)
        elif self.count == len(self.embeds)-1:
            button1 = [x for x in self.children if x.custom_id == "prev"][0]
            button1.disabled = False
            button.disabled = True
            await interaction.response.edit_message(embed=self.embeds[self.count], view=self)
