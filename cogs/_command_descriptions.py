"""
Central registry of command descriptions for ,help <command>.

Used as a FALLBACK in help.py - command.brief or command.description (set
directly on the @commands.command(...) decorator) wins first; this dict only
fills in commands that don't set one inline.

Keys are lowercase command names (qualified_name).
"""

COMMAND_DESCRIPTIONS = {
    # --- admin.py ---
    "savebans": "Save the current server ban list to a JSON file format storage.",
    "exportbans": "Import and systematically load an extracted JSON ban file profile back.",
    "nuke": "Clones the current text channel structure and drops the old channel instance.",
    "forcenick": "Locks a targeted member into an explicit nickname string override.",
    "stopforcenick": "Releases a targeted user from their locked forced nickname status.",
    "kick": "Ejects a targeted member user out of the current server.",
    "softban": "Bans a targeted user to wipe their history logs and immediately unbans them.",
    "ban": "Permanently banishes a targeted member user from the current guild server.",
    "unban": "Removes the active ban status from a specified user ID structure.",
    "mute": "Applies a time-out restriction boundary duration metric to a server member.",

    # --- afk.py ---
    "afk": "Configures an active away status layer paired with an optional message.",
    "afkoff": "Manually clears your away profile status and outputs all collected mention data.",

    # --- alerts.py ---
    "setloghook": "Configures your custom webhook pipeline to capture DM activity logging.",
    "logon": "Activates background webhook logging indicators for edited and deleted DMs.",
    "logoff": "Turns off the background direct message activity tracker webhook system.",
    "setmentionhook": "Saves your custom destination webhook pipeline address for mention alerts.",
    "mentionon": "Enables instant private notifications when your profile is directly mentioned.",
    "mentionoff": "Deactivates automated private webhook notification delivery for group mentions.",
    "setkeywordhook": "Saves your hook destination target tracking for custom word pings.",
    "addkeyword": "Appends an explicit text string phrase to your word alert surveillance matrix.",
    "removekeyword": "Deletes a designated keyword filter phrase from your monitor index.",
    "keywordlist": "Outputs a clean structured manifest displaying your current tracked words.",
    "keywordon": "Enables custom keyword word alerts via your configured webhook pipeline.",
    "keywordoff": "Turns off word keyword notifications.",
    "setrolehook": "Saves your hook destination address tracking string for role alert logging.",
    "addrole": "Appends a specific group category role index to your webhook tracking matrix.",
    "removerole": "Drops a specified role layout item from your alert tracking watch index.",
    "roleon": "Turns on alerts for watched group roles.",
    "roleoff": "Turns off alerts for watched group roles.",
    "setgreet": "Saves and activates a configured welcome text note layout for new incoming DMs.",
    "greetoff": "Disables the automatic message greetings panel completely.",
    "cleargreet": "Purges your greeting text preferences and historical user record tables.",

    # --- ai.py ---
    "ai": "Transmits a text payload message string forward to chat with the AI assistant.",
    "resetai": "Clears out the rolling text history memory index inside the current channel context.",
    "setprompt": "Saves a permanent baseline framework rule guide for your AI chats.",
    "resetprompt": "Restores the AI system guidelines back to their out-of-the-box configurations.",
    "showprompt": "Outputs the active structural system guidance note rule running on the AI.",

    # --- ars.py ---
    "addar": "Configures a new automatic word response string hook.",
    "removear": "Deletes a specified automated script trigger layer entirely.",
    "listar": "Displays a clean menu indexing all current active text response rules.",

    # --- automessage.py ---
    "startauto": "Schedules a message to repeat automatically in a channel at fixed intervals.",
    "listauto": "Displays an exhaustive timeline log profile tracking scheduled loop messages.",
    "stopauto": "Cancels a running background automation scheduler routine by its index ID.",

    # --- crypto.py ---
    "getbal": "Fetches current balances and parameters for any valid LTC destination addy.",
    "price": "Fetches current market valuations for support assets.",
    "getbtcbal": "Fetches current valuation values for any destination BTC address tracker.",
    "getethbal": "Fetches current balance parameters for any destination ETH address tracking loop.",
    "convert": "Processes exchange scale evaluations between supported asset groups.",

    # --- dump.py ---
    "alldump": "Dumps and saves every history asset file found inside a target channel loop.",
    "imgdump": "Extracts image assets from a channel's past chat history logs.",
    "audiodump": "Extracts MP3 media tracks out of history storage data blocks.",
    "videodump": "Extracts video formats from channel record parameters.",
    "textdump": "Compiles the last 1,000 text chat logs into a plaintext document layout.",
    "emojidump": "Downloads all custom graphics emojis configured inside a server folder.",
    "emojidownload": "Isolates and downloads a specific target image emoji asset array.",
    "avatardump": "Extracts and downloads profile photo icons from all server members.",
    "channeldump": "Compiles an inventory list mapping out all text channel names inside the guild.",

    # --- fun.py ---
    "spam": "Dispatches quick messaging lines forward down a text track at uniform rates.",
    "massreact": "Attaches random reaction graphics onto the immediate previous message stream.",
    "clear": "Bulk-delete your own messages in this channel (optionally links only).",
    "massmention": "Post a message that mentions a sample of server members.",
    # NOTE: "cum" is defined twice (here and under HENTAI.PY). In a dict the
    # LAST one wins, so ,help cum shows the HENTAI.PY text. Rename one if you
    # want both to show.
    "cum": "Displays a multi-frame custom graphical layout text execution line animation panel.",
    "fakenitro": "Generates a simulated gift link string payload matching platform patterns.",
    "infect": "Generates a multi-step custom loading progress tracking screen animation layout.",
    "spamgp": "Sends quick ghost mentions down a channel line that instantly delete.",
    "spamghostping": "Sends quick ghost mentions down a channel line that instantly delete.",
    "spamdm": "Sends direct messages to a targeted user at specific time parameters.",
    "spamrep": "Submits framework issue log metrics directly against an input message ID tag.",

    # --- funextras.py ---
    "meme": "Fetches a random joke meme graphic format from standard public repositories.",
    "cat": "Fetches a random picture item detailing domestic cats.",
    "dog": "Fetches a random picture tracking canine animals.",
    "fox": "Fetches a random image profiling wild foxes.",
    "joke": "Fetches a random two-stage comedy joke statement structure loop.",
    "rizz": "Fetches a random text phrase pickup guideline statement option.",
    "8ball": "Processes an evaluation response against an input string query.",
    "coinflip": "Flips a digital coin to return a random result.",
    "roll": "Rolls a die with custom sides.",

    # --- help.py ---
    "help": "Shows all modules, or a module's commands, or one command's full syntax.",

    # --- hentai.py (ILLUSTRATED / ANIME) ---
    "hrandom": "Fetch a random anime hentai image.",
    "hass": "Fetch a random anime hentai ass image.",
    "ass": "Fetch a random anime real-style ass image.",
    "boobs": "Fetch a random anime real-style breasts image.",
    "pussy": "Fetch a random anime real-style pussy image.",
    "4k": "Fetch a random high-quality 4K NSFW image.",
    "cumm": "Fetch a random anime cum/blowjob image.",
    "cum": "Fetch a random cum or creampie illustration picture loop entry.",
    "cummings": "Fetches random illustrations.",
    "lewd": "Fetches a random adult waifu illustration drawing asset.",
    "hblowjob": "Fetch a random anime blowjob image.",
    "ahegao": "Fetch a random anime ahegao face image.",
    "feet": "Fetch a random anime feet image.",
    "lesbian": "Fetch a random anime yuri/lesbian image.",
    "spank": "Fetch a random anime spanking image.",
    "hwallpaper": "Fetch a random clean anime/hentai wallpaper (99% SFW).",
    "panties": "Fetch a random anime panties/pantsu picture.",
    "hentai": "Fetch a standard random anime hentai image.",
    "hthigh": "Fetch a random anime thighs picture.",
    "hmidriff": "Fetch a random anime midriff picture.",
    "hboobs": "Fetch a random anime breasts picture.",
    "hkitsune": "Fetch a random anime kitsune/fox-girl picture.",
    "hneko": "Fetch a random anime neko/cat-girl picture.",
    "kemonomimi": "Fetch a random anime kemonomimi character picture.",
    "hanal": "Fetch a random anime anal hentai image.",
    "tentacle": "Fetch a random anime tentacle hentai image.",
    "yaoi": "Fetch a random anime yaoi image.",

    # --- hentai.py (REAL-LIFE PHOTOS & VIDEOS) ---
    "pvideo": "Fetches a random real-life adult streaming video link from premium indexes.",
    "hvideo": "Fetches a random short moving hentai animation loop file asset path.",
    "uncensored": "Fetch a random real-life uncensored adult image.",
    "thigh": "Fetch a random real-life thighs photo.",
    "anal": "Fetch a random real-life anal photo.",
    "gonewild": "Fetch a random real-life wild photo.",
    "pgif": "Fetch a random real-life adult porn GIF file.",
    "rass": "Fetch a random real-life ass photo.",
    "rboobs": "Fetch a random real-life breasts photo.",
    "rpussy": "Fetch a random real-life pussy photo.",
    "r4k": "Fetch a random high-definition real-life 4K adult photo.",

    # --- image.py ---
    "stealav": "Clones a specified member user's avatar icon photo onto your account.",
    "setavatar": "Changes your active account profile photo from a direct web URL link.",
    "setav": "Changes your active account profile photo from a direct web URL link.",
    "invisav": "Applies a hidden transparent profile graphic onto your active account avatar.",
    "setpass": "Saves your local selfbot verification security password parameters.",

    # --- info.py ---
    "avatar": "Extracts the clean, high-resolution source image file link of any member's avatar.",
    "av": "Extracts the clean, high-resolution source image file link of any member's avatar.",
    "ava": "Extracts the clean, high-resolution source image file link of any member's avatar.",
    "userinfo": "Compiles exhaustive tracking stats, register dates, and permissions for a user.",
    "whois": "Queries platform databases to pull raw flag configurations, background URLs, and user IDs.",
    "stats": "Outputs technical runtime telemetry, CPU status, Python versions, and memory usage.",
    "ping": "Outputs your current connection response speeds.",
    "tokeninfo": "Queries platform token details to pull up account verification parameters.",
    "iplook": "Queries geolocation databases to discover ISP details and city tracking variables.",
    "id": "Extracts internal design snow-flake ID metrics for any tag query target.",

    # --- wizz.py ---
    "randomban": "Bans a specified count of random server members.",
    "massban": "Ban a list of member IDs, with a delay between each ban.",
    "massunban": "Unban a list of member IDs.",
    "massdm": "Sends a direct message to all non-bot members in the server.",

    # --- utiltity.py ---
    "calc": "Evaluate a math expression.",
    "getpic": "Search for and post an image matching a query.",

    # --- status_rotator.py ---
    "start_rotation": "Start rotating your custom status through a list of messages.",
    "stop_rotation": "Stop the status rotation.",
}

