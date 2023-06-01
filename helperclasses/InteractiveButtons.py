import discord

# creating a buttonView that helps with pagnation through various embeds
class ButtonView(discord.ui.View):
    def __init__(self, embed: list):
        # after 60 seconds, the buttons will stop working
        super().__init__(timeout=60)
        self.embeds = embed
        self.count = 0

    @discord.ui.button(label="<--", style=discord.ButtonStyle.blurple, custom_id="prev", disabled=True)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):

        # subtracts 1 from the count (the page number)
        self.count -= 1

        # if the count is 0, it will disable the previous button from being clicked and enable the
        # next button
        if self.count == 0:
            button1 = [x for x in self.children if x.custom_id == "next"][0]
            button1.disabled = False
            button.disabled = True
            await interaction.response.edit_message(embed=self.embeds[self.count], view=self)

        # if the count is over 0, it will enable button1 (the next button)
        elif self.count > 0:
            button1 = [x for x in self.children if x.custom_id == "next"][0]
            button1.disabled = False
            await interaction.response.edit_message(embed=self.embeds[self.count], view=self)

    @discord.ui.button(label="-->", style=discord.ButtonStyle.blurple, custom_id="next", disabled=False)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):

        # adds 1 to the count (the page number)
        self.count += 1

        # if the count is less than the max amount of pages, it will enable the previous button
        if self.count < len(self.embeds)-1:
            button1 = [x for x in self.children if x.custom_id == "prev"][0]
            button1.disabled = False
            await interaction.response.edit_message(embed=self.embeds[self.count], view=self)
        
        # if the count is equal to the max amount of pages, it will disable the next button and enable
        # the previous button
        elif self.count == len(self.embeds)-1:
            button1 = [x for x in self.children if x.custom_id == "prev"][0]
            button1.disabled = False
            button.disabled = True
            await interaction.response.edit_message(embed=self.embeds[self.count], view=self)
