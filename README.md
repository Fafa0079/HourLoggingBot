# Hour Logging Bot 
A discord bot that manages logging hours. <br />
Integrates with Google Sheets to log hours directly to a spreadsheet from commands sent over discord. <br />
Utilizes Google OAuth 2.0 to make changes to a spreadsheet. <br />
Currently a WIP, not all features are implemented yet.
## Current Features:
- Use of Discord's new slash command system
- /setup: Easy setup of the /log command for your discord. Administrators are led through a series of GUIs.
    1. Allow integration of discord bot w/ google sheets
    1. Select hour approval channel (or allow the bot to create one for you)
    1. Select log channel (where all instances of hour logging will be logged)
    1. Select whether the /verify command is required before logging hours (If true, will log real name alongside discord name)
    1. Add all subteams/groups
- /log: Logs hours to the system. Three parameters: subteam/group, number of hours, description of work done. Message is sent to the selected hour approval channel. (selected in /setup)
  - In the hour approval channel, you may select to confirm or deny the hours.
    - Confirming the hours will automatically update the spreadsheet.
    - Editing the hours will allow an admin to change the number of hours to a number more appropiate.
    - Denying the hours will give you the option to provide a reason for the denial and the user who sent the request will be messaged with the reason.
  - After selecting an option, the embed will show the hours accepted/denied and for what person.
## Planned Features:
- Use of Discord's new slash command system
- /setup config: Allows you to configure settings of previously created logging systems created through /setup
  - Add subteams/groups
  - Select hour approval channel
  - Toggle use of /verify
  - Clear setup (Allows you to redo the setup process, clearing the previous one in the process.)
- /verify: Add real name to hour logging. Togglable in /setup.
  - Will log your real name in the spreadsheet instead of the discord name if true in /setup
  - In the hour approval channel, you may select to confirm or deny the hours.
    - Confirming the hours will automatically update the spreadsheet.
    - Editing the hours will allow an admin to change the number of hours to a number more appropiate.
    - Denying the hours will give you the option to provide a reason for the denial and the user who sent the request will be messaged with the reason.
  - After selecting an option, the embed will show the hours accepted/denied and for what person.
- /hours: Lists the number of hours on each subteam/group. One parameter: discord user.
  - May not be implemented if plans change
