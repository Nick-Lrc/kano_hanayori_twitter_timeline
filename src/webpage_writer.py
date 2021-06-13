"""This scripts writes the final webpage of the Twitter user.

The default
- Tweets file locates at '../data/texts/tweets.json'.
- User info file locates at '../data/texts/user.json'.
- HTML setting file locates at 'configs/html.json'.
- Output directory of the webpage locates at '..'.

Example Usage:
    python webpage_writer.py \
        -i "path/to/the/tweets/file" \
        -u "path/to/the/user/info/file" \
        -s "path/to/the/html/setting/file" \
        -o "path/to/the/webpage/output/directory"
"""

from __future__ import annotations
import argparse
from datetime import datetime
import os
import re
import urllib.parse

from utils import color, io, string # pylint: disable=import-error
from utils.html import HTMLWriter # pylint: disable=import-error


# Output filename
WEBPAGE_OUTPUT_FILENAME = 'index.html'


def write_footer(writer: HTMLWriter, footer: dict) -> None:
    """Writes the footer.

    Parameters
    ----------
    writer: HTMLWriter
        An instance of HTMLWriter.
    footer: dict
        Contents in the footer. Includes a URL and the inner text.
        Format:
        {
            'url': str('URL links to the inner text.'),
            'inner_text': str('Text inside the footer.')
        }
    """
    (writer.open_footer()
           .open_paragraph(classes=['text-center'])
           .open_hyperlink(href=footer['url'])
           .write_inner_text(footer['inner_text'])
           .close_hyperlink()
           .close_paragraph()
           .close_footer())


def write_head(
        writer: HTMLWriter, title: str, icon_path: str, settings: dict) -> None:
    """Writes the head.

    Parameters
    ----------
    writer: HTMLWriter
        An instance of HTMLWriter.
    title: str
        Webpage title.
    icon_path: str
        Path to the website icon.
    settings: dict
        HTML settings. Includes the charset and paths to the stylesheets and 
        javascripts.
        Format:
        {
            "charset": str('Charset to use.'),
            "stylesheets": [
                str('Paths to the CSS stylesheets.')
            ],
            "javascripts": [
                str('Paths to the Javascripts.')
            ]
        }
    """
    (writer.open_head()
           .open_meta(charset=settings['charset'])
           .open_meta(
               name='viewport', content='width=device-width, initial-scale=1'))
    
    for href in settings['stylesheets']:
        writer.open_stylesheet(href=href)
    for src in settings['javascripts']:
        writer.open_javascript(src=src).close_javascript()

    (writer.open_title()
           .write_inner_text(title)
           .close_title()
           .open_icon(href=icon_path)
           .close_head())


def write_tweet(
        writer: HTMLWriter, user: dict, tweet: dict, use_remote_video: bool) -> None:
    """Write a single Tweet and maps hashtags, mentions, and websites to URLs.
    
    Parameters
    ----------
    writer: HTMLWriter
        An instance of HTMLWriter.
    user: dict
        User info. See twitter_downloader.get_user() and the script comment of 
        path_resolver for the format.
    tweet: dict
        Tweets. See twitter_downloader.get_tweets() and the script comment of
        path_resolver for the format.
    use_remote_video: bool
        Whether or not to use remote URLs instead of local paths. Affects video
        files only.
    """
    username = user['username']
    avatar_path = user['profile_image_url']['path']
    display_name = user['friendly_name']
    if 'protected' in user and user['protected']:
        display_name += '🔒'
    tweet_id = tweet['id']
    created_at = string.convert_timestamp(
        tweet['created_at'], '%Y-%m-%dT%H:%M:%S', '%b %d, %Y %H:%M')

    (writer.open_div(classes=['media', 'p-3'])
           .open_hyperlink(href=avatar_path)
           .open_image(
               src=avatar_path, 
               alt=f"Avatar of {username}", 
               classes=['avatar', 'border', 'mr-3', 'rounded-circle'])
           .close_hyperlink()
           .open_div(classes=['media-body'])
           .open_span(classes=['font-weight-bold'])
           .write_inner_text(display_name)
           .close_span()
           .open_span(classes=['text-secondary'])
           .write_inner_text(f' / {created_at}')
           .close_span()
           .open_hyperlink(
               href=get_status_url(username, tweet_id), classes=['float-right'])
           .write_inner_text(f'#{tweet_id}')
           .close_hyperlink())

    write_paragraph(writer, tweet['text'])
    if 'media' in tweet:
        image_classes = ['border', 'img-fluid', 'rounded']
        media = tweet['media']
        write_media(writer, media[0], image_classes, use_remote_video, tweet_id)
        if len(media) > 1:
            image_classes.append('mt-3')
            for path in media[1:]:
                write_media(writer, path, image_classes, use_remote_video, tweet_id)
    writer.close_div().close_div()


def write_media(
        writer: HTMLWriter, path: dict, classes: list, use_remote_video: bool, 
        tweet_id: int) -> None:
    """Writes HTML tags to display a media file, either an image or a video.

    Parameters
    ----------
    writer: HTMLWriter
        An instance of HTMLWriter.
    path: dict
        Local path and remote URL of this media.
        Format:
        {
            'type': str('Media type, either video or image.'),
            'path': str('Local path to the media.'),
            'url': str('Remote URL of the media'),
            'thumbnail': str('Local path to the video. For video files only.')
        }
    classes: list
        Image tag classes.
    use_remote_video: bool
        Whether or not to use remote URLs instead of local paths. Affects video
        files only.
    tweet_id: bool
        Unique identifier of this Tweet. Included here to support accessibility
        in the image tag (alt).
    """
    image_path = path['path']
    url = image_path
    media_type = path['type']
    if media_type == 'video':
        image_path = path['thumbnail']
        writer.open_div(classes=['thumbnail'])
        if use_remote_video:
            url = path['url']
    else:
        writer.open_div()
    
    (writer.open_hyperlink(href=url)
           .open_image(
               src=image_path, 
               alt=f'{media_type.capitalize()} of Tweet #{tweet_id}', 
               classes=classes))
    if media_type == 'video':
        writer.open_span().write_inner_text('▶').close_span()
    writer.close_hyperlink().close_div()


def write_user(writer: HTMLWriter, user: dict) -> None:
    """Writes HTML tags to display the user profile.

    Parameters
    ----------
    writer: HTMLWriter
        An instance of HTMLWriter.
    user: dict
        User info. See twitter_downloader.get_user() and the script comment of 
        path_resolver for the format.
    """
    username = user['username']
    writer.open_div(classes=['shadow'])
    if 'profile_banner_url' in user:
        profile_banner_path = user['profile_banner_url']['path']
        (writer.open_hyperlink(href=profile_banner_path)
               .open_image(
                   src=profile_banner_path, 
                   alt=f"Profile banner image of {username}", 
                   classes=['border-bottom', 'img-fluid'])
               .close_hyperlink())

    avatar_path = user['profile_image_url']['path']
    display_name = user['friendly_name']
    if 'protected' in user and user['protected']:
        display_name += '🔒'
    (writer.open_div(classes=['media', 'p-3'])
           .open_hyperlink(href=avatar_path)
           .open_image(
               src=avatar_path, 
               alt=f"Avatar of {username}", 
               classes=['avatar-profile', 'border', 'mr-3', 'rounded-circle'])
           .close_hyperlink()
           .open_div(classes=['media-body'])
           .open_heading(2, classes=['font-weight-bold'])
           .write_inner_text(display_name)
           .close_heading(2)
           .open_hyperlink(href=get_profile_url(username))
           .write_inner_text(f'@{username}')
           .close_hyperlink())

    write_paragraph(writer, user['description'])
    writer.open_div(classes=['text-secondary'])
    if 'location' in user:
        writer.open_div().write_inner_text(f"📍 {user['location']}").close_div()

    if 'profile_website_urls' in user:
        for url in user['profile_website_urls']:
            (writer.open_div()
                   .open_hyperlink(href=url['expanded_url'])
                   .write_inner_text(f"🔗 {url['display_url']}")
                   .close_hyperlink()
                   .close_div())

    timestamp_in_format = '%Y-%m-%dT%H:%M:%S'
    if 'birthday' in user:
        birthday = string.convert_timestamp(
            user['birthday'], timestamp_in_format, '%B %d')
        writer.open_div().write_inner_text(f'🎈 Born {birthday}').close_div()

    if 'created_at' in user:
        created_at = string.convert_timestamp(
            user['created_at'], timestamp_in_format, '%B %Y')
        writer.open_div().write_inner_text(f'📅 Joined {created_at}').close_div()

    if 'following_count' in user and 'followers_count' in user:
        (writer.open_div(classes=['mt-3'])
               .open_hyperlink(href=get_following_url(username), classes=['mr-3'])
               .open_span(classes=['font-weight-bold'])
               .write_inner_text(str(user['following_count']))
               .close_span()
               .write_inner_text(' Following')
               .close_hyperlink()
               .open_hyperlink(href=get_followers_url(username))
               .open_span(classes=['font-weight-bold'])
               .write_inner_text(str(user['followers_count']))
               .close_span()
               .write_inner_text(' Followers')
               .close_hyperlink()
               .close_div())
    writer.close_div().close_div().close_div().close_div()


def write_paragraph(writer: HTMLWriter, paragraph: dict) -> None:
    """Writes either a user description or the text portion of a Tweet.

    The content may contain hashtags, mentions, and website links. Translates
    them to actual URLs.

    Parameters
    ----------
    writer: HTMLWriter
        An instance of HTMLWriter.
    paragraph: dict
        Paragraph content. Includes position hints to hashtags, mentions, and
        website links present in the paragraph content.
    """
    writer.open_paragraph()
    links = []
    if 'hashtags' in paragraph:
        links.extend(paragraph['hashtags'])
    if 'mentions' in paragraph:
        links.extend(paragraph['mentions'])
    if 'urls' in paragraph:
        links.extend(paragraph['urls'])
    links = sorted(links, key=lambda link: link['start'])

    content = paragraph['content']
    cursor = 0
    for link in links:
        start = link['start']
        # Avoid duplicated links.
        if start < cursor:
            continue
        end = link['end']

        # TODO: Uses the HTMLWriter to write '<br>' tags.
        text_before = content[cursor:start].replace('\n', '<br>')
        writer.write_inner_text(_check_links(text_before))
        link_text = content[start:end]
        url = None
        if 'tag' in link:
            url = get_hashtag_url(f"#{link['tag']}")
        elif 'username' in link:
            url = get_profile_url(link['username'])
        else:
            url = link['expanded_url']
            link_text = link['display_url']
        writer.open_hyperlink(href=url).write_inner_text(link_text).close_hyperlink()
        cursor = end
    if cursor < len(content):
        text_remain = content[cursor:].replace('\n', '<br>')
        writer.write_inner_text(_check_links(text_remain))
    writer.close_paragraph()


def get_hashtag_url(hashtag: str) -> str:
    """Translates the hashtag to an actual URL.

    Parameters
    ----------
    hashtag: str
        Twitter hashtag with the '#' prefix. e.g. #example
    
    Returns
    -------
    str
        URL linked to the hashtag.
    """
    escaped_hashtag = urllib.parse.quote_plus(hashtag)
    return f'https://twitter.com/search?q={escaped_hashtag}&src=hashtag_click'


def get_followers_url(username: str) -> str:
    """Translates the username to the follower URL.
    
    Parameters
    ----------
    username: str
        Twitter username without the '@' prefix. e.g. example_twitter_user
    
    Returns
    -------
    str
        URL linked to the follower list.
    """
    return f'{get_profile_url(username)}/followers'


def get_following_url(username: str) -> str:
    """Translates the username to the following URL.
    
    Parameters
    ----------
    username: str
        Twitter username without the '@' prefix. e.g. example_twitter_user
    
    Returns
    -------
    str
        URL linked to the following list.
    """
    return f'{get_profile_url(username)}/following'


def get_profile_url(username: str) -> str:
    """Translates the username to the profile URL.
    
    Parameters
    ----------
    username: str
        Twitter username without the '@' prefix. e.g. example_twitter_user
    
    Returns
    -------
    str
        URL linked to the profile URL.
    """
    return f'https://twitter.com/{username}'


def get_status_url(username: str, tweet_id: tuple[int, str]) -> str:
    """Translates the Tweet id to the Tweet status URL.
    
    Parameters
    ----------
    username: str
        Twitter username without the '@' prefix. e.g. example_twitter_user
    tweet_id: tuple[int, str]
        Unique identification of a Tweet.
    
    Returns
    -------
    str
        URL linked to the Tweet status URL.
    """
    return f'{get_profile_url(username)}/status/{tweet_id}'


def _check_links(text: str) -> str:
    """Check if there are hashtags or mentions in the text.
    
    The Twitter API omits invalid mentions (and maybe hashtags as well). This
    method identifies them and makes them look disabled.

    Parameters
    -------
    text: str
        Tweets content that may contain hashtags or mentions neglected by the API.
    
    Returns
    -------
    str
        Link-resolved text.
    """
    tokens = set()
    hashtags = re.findall(r'#\w+', text)
    for hashtag in hashtags:
        tokens.add(hashtag)
    mentions = re.findall(r'@\w+', text)
    for mention in mentions:
        tokens.add(mention)
    for token in tokens:
        # TODO: Tells the HTMLWriter to write this span instead.
        text = text.replace(token, f'<span class="text-secondary">{token}</span>')
    return text

def _get_options() -> None:
    parser = argparse.ArgumentParser(
        description='Parses the user info and Tweets to write a webpage.')
    parser.add_argument(
        '-i', '--input', default='../data/texts/tweets.json', type=str, 
        help='Path to the Tweets file.')
    parser.add_argument(
        '-u', '--user', default='../data/texts/user.json', type=str, 
        help='Path to the user info file.')
    parser.add_argument(
        '-s', '--settings', default='configs/html.json', type=str, 
        help='Path to HTML setting file')
    parser.add_argument(
        '-o', '--output', default='..', type=str, 
        help='Path to output directory.')
    parser.add_argument(
        '--use-remote-video', action='store_true', default=False, 
        help='Links each thumbnail to its remote URL instead of its local path.')
    return parser.parse_args()


if __name__ == '__main__':
    options = _get_options()
    tweets = io.load_json(options.input)
    user = io.load_json(options.user)
    settings = io.load_json(options.settings)
    webpage_path = io.join_paths(options.output, WEBPAGE_OUTPUT_FILENAME)
    webpage = io.open_text(webpage_path)
    writer = HTMLWriter(webpage)

    print(f"Writing webpage of {user['username']}...")
    writer.write_doctype().open_html()
    write_head(
        writer, user['friendly_name'], user['profile_image_url']['path'], 
        settings)
    writer.open_body().open_div(classes=['container'])
    write_user(writer, user=user)
    writer.open_div(classes=['mt-4'])

    for _, tweet in sorted(tweets.items()):
        write_tweet(writer, user, tweet, options.use_remote_video)
        writer.open_horizontal_rule()

    writer.close_div().close_div()
    write_footer(writer, settings['footer'])
    writer.close_body().close_html()
    print(f"Saved webpage of {user['username']} to '{webpage_path}'.")
    print()
    print(color.get_ok('Done.'))
