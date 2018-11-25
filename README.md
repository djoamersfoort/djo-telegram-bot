# DJO Bot

## Description

  This is a Telegram bot based on: https://github.com/cbrgm/telegram-robot-rss

### Usage

**Controls**  
`/start` - Activates the bot. If you have subscribed to RSS feeds, you will receive news from now on  
`/stop` - Deactivates the bot. You won't receive any messages from the bot until you activate the bot again using the start comand

**RSS Management**  
`/add <url> <entryname>` - Adds a new subscription to your list.  
`/remove <entryname>` - Removes an exisiting subscription from your list.  
`/get <entryname> [optional: <count 1-10>]` - Manually parses your subscription, sending you the last <count> elements.  
`/list` - Shows all your subscriptions as a list.
`/addgroup` <url> <@groupname> - Adds a feed url and sends updates to a supergroup

**Other**  
`/about` - Shows some information about RobotRSS Bot  
`/help` - Shows the help menue
