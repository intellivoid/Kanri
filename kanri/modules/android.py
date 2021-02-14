import json
from pyrogram import filters, Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from kanri import LOCAL
from kanri.helpers import custom_filters
from hurry.filesize import size as get_size
from urllib.parse import quote_plus
from aiohttp import ClientConnectionError
import asyncio

__mod_name__ = "Android"
__help__ = "android_help"


class ETagCacheManager:
    """
    This is a simple cache manager to make lookups
    faster so we don't need to download unnecessary data.
    """

    def __init__(self):
        """
        Object constructor
        """

        self.etag_cache = {}

    async def get(self, url):
        """
        Try to do some cache magic first so we don't download tons of data all the time
        """
        if url not in self.etag_cache:
            data = await LOCAL.HTTP_SESSION.get(url)
            # github and aiohttp are gay; dumb workaround for mimetype being text/plain
            if data.content_type != "application/json":
                response = json.loads(await data.text())
            else:
                response = await data.json()
            # if the site doesn't have an etag, just return the current data.
            if data.headers.get('etag'):
                self.etag_cache[url] = data.headers.get('etag'), response
        else:
            headers = {
                "If-None-Match": self.etag_cache[url][0],
            }
            data = await LOCAL.HTTP_SESSION.get(
                "https://raw.githubusercontent.com/Evolution-X-Devices/official_devices/master/devices.json",
                headers=headers,
            )
            if data.status == 304:
                response = self.etag_cache[url][1]
            else:
                response = json.loads(await data.text())
                self.etag_cache[url] = data.headers.get('etag'), response
        return response


# create a cache manager
cache = ETagCacheManager()


@Client.on_message(~filters.me & filters.command('los') & ~LOCAL.FLOOD_WAITED)
async def lineageos(_, message):
    cmd = message.command
    cmd.pop(0)

    if not cmd:
        await message.reply(LOCAL.PLATE("android_cmd_example", LOCAL.DEFAULT_LANG, cmd=cmd))
        return
    cmd = cmd[0]
    try:
        los = await cache.get(
            f'https://download.lineageos.org/api/v1/{quote_plus(cmd)}/nightly/*'
        )
        response = los['response']
        if not response:
            await message.reply(LOCAL.PLATE("android_err_notfound", LOCAL.DEFAULT_LANG))
            return
        response = response[0]
        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=LOCAL.PLATE("android_button_download", LOCAL.DEFAULT_LANG),
                        url=response['url'],
                    )
                ]
            ]
        )
        await message.reply(
            LOCAL.PLATE(
                "android_los_msgtxt",
                LOCAL.DEFAULT_LANG,
                filename=response['filename'],
                url=response['url'],
                size=get_size(int(response['size'])),
                version=response['version'],
            ),
            disable_web_page_preview=True,
            reply_markup=buttons,
        )
    except ClientConnectionError:
        await message.reply(LOCAL.PLATE("android_err_api", LOCAL.DEFAULT_LANG))


@Client.on_message(~filters.me & custom_filters.command('evo') & ~LOCAL.FLOOD_WAITED)
async def evolution_x(_, message):
    cmd = message.command
    cmd.pop(0)

    if not cmd:
        await message.reply(LOCAL.PLATE("android_cmd_example", LOCAL.DEFAULT_LANG, cmd="evo"))
        return
    cmd = cmd[0]
    try:
        # Try to do some cache magic first so we don't download tons of data all the time
        devices = await cache.get(
            "https://raw.githubusercontent.com/Evolution-X-Devices/official_devices/master/devices.json"
        )
        if not devices:
            await message.reply(LOCAL.PLATE("android_err_api", LOCAL.DEFAULT_LANG))
            return
        for d in devices:
            if d['codename'] == cmd:
                # find the device text so we can get the deprecated part
                deprecated = (
                    d['supported_versions'][0]['deprecated']
                    if "deprecated" in d['supported_versions'][0]
                    else False
                )

                evo = await cache.get(
                    f'https://raw.githubusercontent.com/Evolution-X-Devices/official_devices/master/builds/{quote_plus(cmd)}.json'
                )
                # someone messed up the devices.json file.
                if not evo:
                    await message.reply(LOCAL.PLATE("android_err_notfound", LOCAL.DEFAULT_LANG))
                    return

                buttons = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text=LOCAL.PLATE("android_button_download", LOCAL.DEFAULT_LANG),
                                url=evo['url'],
                            )
                        ]
                    ]
                )
                await message.reply(
                    LOCAL.PLATE(
                        "android_evo_msgtxt",
                        LOCAL.DEFAULT_LANG,
                        filename=evo['filename'],
                        url=evo['url'],
                        size=get_size(int(evo['size'])),
                        version=evo['version'],
                        maintainer=evo['maintainer'],
                        telegram_username=evo['telegram_username'],
                        maintained="No" if deprecated else "Yes",
                    ),
                    disable_web_page_preview=True,
                    reply_markup=buttons,
                )
                return  # Return early to skip the not found message

        await message.reply(LOCAL.PLATE("android_err_notfound", LOCAL.DEFAULT_LANG))
    except ClientConnectionError:
        await message.reply(LOCAL.PLATE("android_err_api", LOCAL.DEFAULT_LANG))


@Client.on_message(~filters.me & custom_filters.command('phh') & ~LOCAL.FLOOD_WAITED)
async def phhusson(_, message):
    try:
        data = await cache.get(
            "https://api.github.com/repos/phhusson/treble_experimentations/releases/latest"
        )
        reply_text = LOCAL.PLATE("android_phh_msgtxt", LOCAL.DEFAULT_LANG)
        for i in range(len(data)):
            try:
                name = data['assets'][i]['name']
                url = data['assets'][i]['browser_download_url']
                reply_text += f"[{name}]({url})\n"
            except IndexError:
                continue
        await message.reply(reply_text)
    except ClientConnectionError:
        await message.reply(LOCAL.PLATE("android_err_api", LOCAL.DEFAULT_LANG))


@Client.on_message(~filters.me & custom_filters.command('bootleggers') & ~LOCAL.FLOOD_WAITED)
async def bootleggers(_, message):
    cmd = message.command
    cmd.pop(0)
    if not cmd:
        await message.reply(LOCAL.PLATE("android_cmd_example", LOCAL.DEFAULT_LANG, cmd="bootleggers"))
        return
    cmd = cmd[0]
    # hotfix for some devices that have uppercase codenames
    if cmd.lower() in ["rmx1971", "x00t", "x01bd", "z01r", "rmx206x"]:
        cmd = cmd.upper()
    try:
        data = await cache.get("http://downloads.bootleggersrom.xyz/api/devices.json")
        for codename, info in data.items():
            if cmd == codename:
                xda = ""
                if info['xdathread']:
                    xda = LOCAL.PLATE("android_bootleg_xda", LOCAL.DEFAULT_LANG, url=info['xdathread'])
                buttons = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text=LOCAL.PLATE("android_button_download", LOCAL.DEFAULT_LANG),
                                url=info['download'],
                            )
                        ]
                    ]
                )
                await message.reply(
                    LOCAL.PLATE(
                        "android_bootleg_msgtxt",
                        LOCAL.DEFAULT_LANG,
                        name=info['fullname'],
                        maintainer=info['maintainer'],
                        date=info['buildate'],
                        size=get_size(int(info['buildsize'])),
                        folderurl=info['downloadfolder'],
                        XDA=xda,
                        filename=info['filename'],
                        fileurl=info['download'],
                    ),
                    disable_web_page_preview=True,
                    reply_markup=buttons,
                )
                return
        await message.reply(LOCAL.PLATE("android_err_notfound", LOCAL.DEFAULT_LANG))
    except ClientConnectionError:
        await message.reply(LOCAL.PLATE("android_err_api", LOCAL.DEFAULT_LANG))


@Client.on_message(~filters.me & custom_filters.command('magisk') & ~LOCAL.FLOOD_WAITED)
async def magisk(_, message):
    url = 'https://raw.githubusercontent.com/topjohnwu/magisk_files/'
    try:
        stable, beta, canary = await asyncio.gather(
            cache.get(url + "master/stable.json"),
            cache.get(url + "master/beta.json"),
            cache.get(url + "canary/canary.json"),
        )
        if not stable and not beta and not canary:
            await message.reply(LOCAL.PLATE("android_err_api", LOCAL.DEFAULT_LANG))
            return
        await message.reply(
            LOCAL.PLATE(
                "android_magisk_msgtxt",
                LOCAL.DEFAULT_LANG,
                # Generics
                uninstalltxt=LOCAL.PLATE("android_magisk_uninstaller", LOCAL.DEFAULT_LANG),
                changelogtxt=LOCAL.PLATE("android_magisk_changelog", LOCAL.DEFAULT_LANG),
                # Stable text
                stablezip="ZIP v" + stable['magisk']['version'],
                stablezipurl=stable['magisk']['link'],
                stableapk="APK v" + stable['app']['version'],
                stableapkurl=stable['app']['link'],
                stableuninstallurl=stable['uninstaller']['link'],
                stablechangelogurl=f"https://topjohnwu.github.io/Magisk/releases/{stable['magisk']['versionCode']}.html",
                # Beta text
                betazip="ZIP v" + beta['magisk']['version'],
                betazipurl=beta['magisk']['link'],
                betaapk="APK v" + beta['app']['version'],
                betaapkurl=beta['app']['link'],
                betauninstallurl=beta['uninstaller']['link'],
                betachangelogurl=f"https://topjohnwu.github.io/Magisk/releases/{beta['magisk']['versionCode']}.html",
                # Canary text
                canaryzip="ZIP v" + canary['magisk']['version'],
                canaryzipurl=url + "canary/canary/" + canary['magisk']['link'],
                canaryapk="APK v" + canary['app']['version'],
                canaryapkurl=url + "canary/" + canary['app']['link'],
                canaryuninstallurl=url + "canary/" + canary['uninstaller']['link'],
                canarychangelogurl=url + "canary/" + canary['magisk']['note'],
            ),
            disable_web_page_preview=True,
        )
    except ClientConnectionError:
        await message.reply(LOCAL.PLATE("android_err_api", LOCAL.DEFAULT_LANG))
