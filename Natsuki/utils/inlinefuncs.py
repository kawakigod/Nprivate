import aiohttp
import json
import sys
import asyncio
from pyrogram.types import (
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardButton,
    InlineQueryResultPhoto
)
from googletrans import Translator
from search_engine_parser import GoogleSearch
from pykeyboard import InlineKeyboard
from sys import version as pyver
from motor import version as mongover
from pyrogram import __version__ as pyrover
from time import time, ctime
from Natsuki.utils.fetch import fetch
from Natsuki.utils.formatter import convert_seconds_to_minutes as time_convert
from Natsuki.utils.pastebin import paste
from Natsuki import (
    pbot as app, BOT_USERNAME, EVENT_LOGS as LOG_GROUP_ID
)
from Natsuki.core.types.InlineQueryResult import InlineQueryResultAudio, InlineQueryResultCachedAudio
from Python_ARQ import ARQ
ARQ_API = "http://thearq.tech"
arq = ARQ(ARQ_API)

async def inline_help_func(__help__):
    buttons = InlineKeyboard(row_width=2)
    buttons.add(
        InlineKeyboardButton(
            'Get More Help?',
            url=f"t.me/{BOT_USERNAME}?start=help"
        ),
        InlineKeyboardButton(
            "Go Inline!",
            switch_inline_query_current_chat=""
        )
    )
    answerss = [
        InlineQueryResultArticle(
            title="Inline Commands",
            description="Help Related To Inline Usage.",
            input_message_content=InputTextMessageContent(__help__),
            thumb_url="https://telegra.ph/file/a39e5688b6764c6c29809.jpg",
            reply_markup=buttons
        )
    ]
    return answerss

async def translate_func(answers, lang, tex):
    i = Translator().translate(tex, dest=lang)
    msg = f"""
__**Translated to {lang}**__
**INPUT:**
{tex}
**OUTPUT:**
{i.text}"""
    answers.append(
        InlineQueryResultArticle(
            title=f'Translated to {lang}',
            description=i.text,
            input_message_content=InputTextMessageContent(msg)
        )
    )
    return answers


async def urban_func(answers, text):
    results = await arq.urbandict(text)
    limit = 0
    for i in results:
        if limit > 48:
            break
        limit += 1
        msg = f"""
**Query:** {text}
**Definition:** __{results[i].definition}__
**Example:** __{results[i].example}__"""

        answers.append(
            InlineQueryResultArticle(
                title=results[i].word,
                description=results[i].definition,
                input_message_content=InputTextMessageContent(msg)
            ))
    return answers


async def google_search_func(answers, text):
    gresults = await GoogleSearch().async_search(text)
    limit = 0
    for i in gresults:
        if limit > 48:
            break
        limit += 1

        try:
            msg = f"""
[{i['titles']}]({i['links']})
{i['descriptions']}"""

            answers.append(
                InlineQueryResultArticle(
                    title=i['titles'],
                    description=i['descriptions'],
                    input_message_content=InputTextMessageContent(
                        msg,
                        disable_web_page_preview=True
                    )
                ))
        except KeyError:
            pass
    return answers


async def wall_func(answers, text):
    results = await arq.wall(text)
    limit = 0
    for i in results:
        if limit > 48:
            break
        limit += 1
        try:
            answers.append(
                InlineQueryResultPhoto(
                    photo_url=results[i].url_image,
                    thumb_url=results[i].url_thumb,
                    caption=f"[Source]({results[i].url_image})"
                ))
        except KeyError:
            pass
    return answers


async def saavn_func(answers, text):
    buttons_list = []
    results = await arq.saavn(text)
    for i in results:
        buttons = InlineKeyboard(row_width=1)
        buttons.add(
            InlineKeyboardButton(
                'Download | Play',
                url=results[i].media_url
            )
        )
        buttons_list.append(buttons)
        duration = await time_convert(results[i].duration)
        caption = f"""
**Title:** {results[i].song}
**Album:** {results[i].album}
**Duration:** {duration}
**Release:** {results[i].year}
**Singers:** {results[i].singers}"""
        description = f"{results[i].album} | {duration} " \
            + f"| {results[i].singers} ({results[i].year})"
        try:
            answers.append(
                InlineQueryResultArticle(
                    title=results[i].song,
                    input_message_content=InputTextMessageContent(
                        caption,
                        disable_web_page_preview=True
                    ),
                    description=description,
                    thumb_url=results[i].image,
                    reply_markup=buttons_list[i]
                ))
        except (KeyError, ValueError):
            pass
    return answers


async def deezer_func(answers, text):
    buttons_list = []
    results = await arq.deezer(text, 5)
    for i in results:
        buttons = InlineKeyboard(row_width=1)
        buttons.add(
            InlineKeyboardButton(
                'Download | Play',
                url=results[i].url
            )
        )
        buttons_list.append(buttons)
        duration = await time_convert(results[i].duration)
        caption = f"""
**Title:** {results[i].title}
**Artist:** {results[i].artist}
**Duration:** {duration}
**Source:** [Deezer]({results[i].source})"""
        description = f"{results[i].artist} | {duration}"
        try:
            answers.append(
                InlineQueryResultArticle(
                    title=results[i].title,
                    thumb_url=results[i].thumbnail,
                    description=description,
                    input_message_content=InputTextMessageContent(
                        caption,
                        disable_web_page_preview=True
                    ),
                    reply_markup=buttons_list[i]
                ))
        except (KeyError, ValueError):
            pass
    return answers


async def webss(url):
    start_time = time()
    if "." not in url:
        return
    screenshot = await fetch(f"https://patheticprogrammers.cf/ss?site={url}")
    end_time = time()
    a = []
    pic = InlineQueryResultPhoto(
        photo_url=screenshot['url'],
        caption=(f"`{url}`\n__Took {round(end_time - start_time)} Seconds.__")
    )
    a.append(pic)
    return a


# Used my api key here, don't fuck with it
async def shortify(url):
    if "." not in url:
        return
    header = {
        "Authorization": "Bearer ad39983fa42d0b19e4534f33671629a4940298dc",
        'Content-Type': 'application/json'
    }
    payload = {
        "long_url": f"{url}"
    }
    payload = json.dumps(payload)
    async with aiohttp.ClientSession() as session:
        async with session.post("https://api-ssl.bitly.com/v4/shorten", headers=header, data=payload) as resp:
            data = await resp.json()
    msg = f"**Original Url:** {url}\n**Shortened Url:** {data['link']}"
    a = []
    b = InlineQueryResultArticle(
        title="Link Shortened!",
        description=data['link'],
        input_message_content=InputTextMessageContent(
            msg, disable_web_page_preview=True)
    )
    a.append(b)
    return a


async def torrent_func(answers, text):
    results = await arq.torrent(text)
    limit = 0
    for i in results:
        if limit > 48:
            break
        title = results[i].name
        size = results[i].size
        seeds = results[i].seeds
        leechs = results[i].leechs
        upload_date = results[i].uploaded + " Ago"
        magnet = results[i].magnet
        caption = f"""
**Title:** __{title}__
**Size:** __{size}__
**Seeds:** __{seeds}__
**Leechs:** __{leechs}__
**Uploaded:** __{upload_date}__
**Magnet:** __{magnet}__"""

        description = f"{size} | {upload_date} | Seeds: {seeds}"
        try:
            answers.append(
                InlineQueryResultArticle(
                    title=title,
                    description=description,
                    input_message_content=InputTextMessageContent(
                        caption,
                        disable_web_page_preview=True
                    )
                )
            )
            limit += 1
        except (KeyError, ValueError):
            pass
    return answers


async def youtube_func(answers, text):
    results = await arq.youtube(text)
    limit = 0
    for i in results:
        if limit > 48:
            break
        limit += 1
        buttons = InlineKeyboard(row_width=1)
        video_url = f"https://youtube.com{results[i].url_suffix}"
        buttons.add(
            InlineKeyboardButton(
                'Watch',
                url=video_url
            )
        )
        caption = f"""
**Title:** {results[i].title}
**Views:** {results[i].views}
**Channel:** {results[i].channel}
**Duration:** {results[i].duration}
**Uploaded:** {results[i].publish_time}
**Description:** {results[i].long_desc}"""
        description = f"{results[i].views} | {results[i].channel} | " \
            + f"{results[i].duration} | {results[i].publish_time}"
        try:
            answers.append(
                InlineQueryResultArticle(
                    title=results[i].title,
                    thumb_url=results[i].thumbnails[0],
                    description=description,
                    input_message_content=InputTextMessageContent(
                        caption,
                        disable_web_page_preview=True
                    ),
                    reply_markup=buttons
                ))
        except (KeyError, ValueError):
            pass
    return answers


async def lyrics_func(answers, text):
    song = await arq.lyrics(text)
    lyrics = song.lyrics
    song = lyrics.splitlines()
    song_name = song[0]
    artist = song[1]
    if len(lyrics) > 4095:
        lyrics = await paste(lyrics)
        lyrics = f"**LYRICS_TOO_LONG:** [URL]({lyrics})"

    msg = f"__{lyrics}__"

    answers.append(
        InlineQueryResultArticle(
            title=song_name,
            description=artist,
            input_message_content=InputTextMessageContent(msg)
        ))
    return answers


async def github_user_func(answers, text):
    URL = f"https://api.github.com/users/{text}"
    result = await fetch(URL)
    buttons = InlineKeyboard(row_width=1)
    buttons.add(InlineKeyboardButton(
        text="Open On Github",
        url=f"https://github.com/{text}"
    ))
    caption = f"""
**Info Of {result['name']}**
**Username:** `{text}`
**Bio:** `{result['bio']}`
**Profile Link:** [Here]({result['html_url']})
**Company:** `{result['company']}`
**Created On:** `{result['created_at']}`
**Repositories:** `{result['public_repos']}`
**Blog:** `{result['blog']}`
**Location:** `{result['location']}`
**Followers:** `{result['followers']}`
**Following:** `{result['following']}`"""
    answers.append(
        InlineQueryResultPhoto(
            photo_url=result['avatar_url'],
            caption=caption,
            reply_markup=buttons
        ))
    return answers


async def github_repo_func(answers, text):
    URL = f"https://api.github.com/repos/{text}"
    URL2 = f"https://api.github.com/repos/{text}/contributors"
    results = await asyncio.gather(fetch(URL), fetch(URL2))
    r = results[0]
    r1 = results[1]
    commits = 0
    for developer in r1:
        commits += developer['contributions']
    buttons = InlineKeyboard(row_width=1)
    buttons.add(
        InlineKeyboardButton(
            'Open On Github',
            url=f"https://github.com/{text}"
        )
    )
    caption = f"""
**Info Of {r['full_name']}**
**Stars:** `{r['stargazers_count']}`
**Watchers:** `{r['watchers_count']}`
**Forks:** `{r['forks_count']}`
**Commits:** `{commits}`
**Is Fork:** `{r['fork']}`
**Language:** `{r['language']}`
**Contributors:** `{len(r1)}`
**License:** `{r['license']['name']}`
**Repo Owner:** [{r['owner']['login']}]({r['owner']['html_url']})
**Created On:** `{r['created_at']}`
**Homepage:** {r['homepage']}
**Description:** __{r['description']}__"""
    answers.append(
        InlineQueryResultArticle(
            title="Found Repo",
            description=text,
            reply_markup=buttons,
            input_message_content=InputTextMessageContent(
                caption,
                disable_web_page_preview=True
            )
        ))
    return answers


async def cached_audio_test_func(answers):
    answers.append(
        InlineQueryResultCachedAudio(
            file_id="CQACAgUAAx0EWIlO9AABA5N3YH0yxW2M9qTAMATvsj2-hkXv7NUAAn4CAAL2U-hXv1yOjFTFTiweBA"
        )
    )
    return answers
