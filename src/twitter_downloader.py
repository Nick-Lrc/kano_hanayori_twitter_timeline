"""This script downloads the account info and Tweets of a Twitter user.

The default 
- Twitter credential file locates at 'configs/credentials.json'.
- Twitter setting file locates at 'configs/twitter.json'.
- Output directory locates at '../data/texts'.

Example usage:
    python twitter.py \
        -c "path/to/twitter/credential/file" \
        -s "path/to/twitter/setting/file" \
        -o "path/to/output/directory"
"""

from __future__ import annotations
import argparse
import os
from typing import Union

import tweepy
from tweepy.client import Client
from tweepy.tweet import Tweet

from utils import color, io, string # pylint: disable=import-error


# Output filenames.
USER_OUTPUT_FILENAME = 'user.json'
TWEETS_OUTPUT_FILENAME = 'tweets.json'
URLS_OUTPUT_FILENAME = 'urls.json'


def archive_tweets(path: str) -> tuple[dict, str]:
    """Loads and archives the existing Tweets file. Extracts the since id as well.
    
    Parameters
    ----------
    path: str
        Path to the Tweets file.

    Returns
    -------
    dict:
        Existing Tweets.
    str:
        Since id. Tells the Twitter client to returns results with a Tweet ID 
        greater than (that is, more recent than) the specified 'since' Tweet ID.
    """
    tweets = {}
    since_id = None
    if os.path.isfile(path):
        tweets = io.load_json(path)
        if tweets:
            since_id = str(sorted(tweets)[-1])
            archive_path = io.archive_file(path)
            print(f"Archived '{path}' to '{archive_path}'.")
    return tweets, since_id


def archive_urls(path: str) -> None:
    """Archives the existing URLs file.

    Parameters
    ----------
    path: str
        Path to the URLs file.
    """
    if os.path.isfile(path):
        archive_path = io.archive_file(path)
        print(f"Archived '{path}' to '{archive_path}'.")


def archive_user(path: str) -> None:
    """Archives the existing user info file.
    
    Parameters
    ----------
    path: str
        Path to the user info file.
    """
    if os.path.isfile(path):
        archive_path = io.archive_file(path)
        print(f"Archived '{path}' to '{archive_path}'.")


def get_client(credentials: dict) -> Client:
    """Authenticates Twitter credentials.

    Credentials format:
    {
        'access_token': str('Twitter API Access Token.'),
        'access_token_secret': str('Twitter API Access Token Secret.'),
        'bearer_token': str('Twitter API Bearer Token.'),
        'consumer_key': str('Twitter API Consumer Key'),
        'consumer_secret': str('Twitter API Consumer Secret')
    }

    Parameters
    ----------
    credentials: dict
        Twitter credentials.
    
    Returns
    -------
    Client:
        Authenticated Twitter client.
    """
    return tweepy.Client(
        access_token=credentials['access_token'],
        access_token_secret=credentials['access_token_secret'],
        bearer_token=credentials['bearer_token'],
        consumer_key=credentials['consumer_key'],
        consumer_secret=credentials['consumer_secret'])


def get_tweets(
        client: Client, uid: int, tweet_parameters: dict, 
        pagination_token: str = None, since_id: str = None) -> tuple[dict, str]:
    """Fetches Tweets.

    Note that the client returns up to the most recent 3200 Tweets.

    Parameters
    ----------
    client: Client
        Authenticated Twitter client.
    uid: int
        User id.
    tweet_parameters: dict
        Additional parameters involved in the search.
        Format:
        {
            'max_results': int('Specifies the number of Tweets to try and retrieve, up to a maximum of 100 per distinct request.'),
            'tweet_fields': [
                str('Selects which specific Tweet fields will deliver in each returned Tweet object.')
            ]
        }
    pagination_token: str, default: None
        Token used to move forwards or backwards through 'pages' of results.
    
    Returns
    -------
    dict:
        Tweets. Unset properties are excluded.
        Format:
        {
            str('Unique identifier of this Tweet.'): {
                'created_at': str('Creation time of the Tweet.'),
                'id': int('Unique identifier of this Tweet.'),
                'like_count': int('Number of Likes of this Tweet.'),
                'quote_count': int('Number of times this Tweet has been Retweeted with a comment.'),
                'reply_count': int('Number of Replies of this Tweet.'),
                'retweet_count': int('Number of times this Tweet has been Retweeted.'),
                'source': str('The name of the app the user Tweeted from.'),
                'text': {
                    'content': str('The content of the Tweet.'),
                    'hashtags': [
                        {
                            'end': int('The end position (zero-based) of the recognized Hashtag within the Tweet.'),
                            'start': int('The start position (zero-based) of the recognized Hashtag within the Tweet.'),
                            'tag': str('The text of the Hashtag.')
                        }
                    ],
                    'mentions': [
                        {
                            'end': int('The end position (zero-based) of the recognized user mention within the Tweet.'),
                            'start': int('The start position (zero-based) of the recognized user mention within the Tweet.'),
                            'username': str('The part of text recognized as a user mention.')
                        }
                    ],
                    'urls': [
                        {
                            'display_url': str('The URL as displayed in the Twitter client.'),
                            'end': int('The end position (zero-based) of the recognized URL within the Tweet.'),
                            'expanded_url': str('The fully resolved URL.'),
                            'start': int('The start position (zero-based) of the recognized URL within the Tweet.'),
                            'url': str('The URL in the format tweeted by the user.')
                        }
                    ]
                }
            }
        }
    
    Raises
    ------
    TypeError
        If cannot get Tweets response from the client.
    """
    tweets = {}
    response = client.get_users_tweets(
        uid, user_auth=True, max_results=tweet_parameters['max_results'], 
        pagination_token=pagination_token,
        since_id=since_id,
        tweet_fields=tweet_parameters['tweet_fields'])
    if not response:
        raise TypeError('Failed to fetch Tweets.')
    if not response.data:
        print(color.get_warning(f'WARNING: No (new) Tweets fetched.'))
        return tweets, None

    for tweet_response in response.data:
        tweet = _parse_tweet(tweet_response)
        tweets[str(tweet['id'])] = tweet

    if 'next_token' in response.meta:
        pagination_token = response.meta['next_token']
    else:
        pagination_token = None
    return tweets, pagination_token


def get_urls(user: dict, tweets: dict) -> dict:
    """Gets unique URLs in user info and Tweets.
    
    Parameters
    ----------
    user: dict
        User info
    tweets: dict
        Tweets
    
    Returns
    -------
    dict:
        Mappings from unique URLs to their local download destinations.
        Format:
        {
            str('URL.'): str('Local download destination.')
        }
    """
    urls = {}
    if 'profile_banner_url' in user:
        urls[user['profile_banner_url']] = 'banner'
    if 'profile_image_url' in user:
        urls[user['profile_image_url']] = 'avatar'

    for tid, tweet in sorted(tweets.items()):
        if 'text' in tweet and 'urls' in tweet['text']:
            for idx, url_info in enumerate(tweet['text']['urls']):
                expanded_url = url_info['expanded_url']
                if expanded_url not in urls:
                    urls[expanded_url] = f'{tid}_{idx}'
    return urls


def get_user(client: Client, username: str, user_parameters: dict) -> dict:
    """Fetches user info.

    Parameters
    ----------
    client: Client
        Authenticated Twitter client.
    username: str
        Username of the target user. Used as a search key.
    user_parameters: dict
        Additional parameters involved in the search.
        Format:
        {
            'user_fields': [
                str('Select which specific user fields will deliver with each returned users objects.')
            ]
        }

    Returns
    -------
    dict:
        User info. Unset properties are excluded.
        Format:
        {
            'created_at': str('Creation time of this account.'),
            'description': {
                'content': str('The text of this user's profile description (also known as bio), if the user provided one.'),
                'hashtags': [
                    {
                        'end': int('The end position (zero-based) of the recognized Hashtag within the Tweet.'),
                        'start': int('The start position (zero-based) of the recognized Hashtag within the Tweet.'),
                        'tag': str('The text of the Hashtag.')
                    }
                ],
                'mentions': [
                    {
                        'end': int('The end position (zero-based) of the recognized user mention within the Tweet.),
                        'start': int('The start position (zero-based) of the recognized user mention within the Tweet.'),
                        'username': str('The part of text recognized as a user mention.')
                    }
                ],
                'urls': [
                    {
                        'display_url': str('The URL as displayed in the user's description.'),
                        'end': int('The end position (zero-based) of the recognized URL in the user's description.'),
                        'expanded_url': str('The fully resolved URL.'),
                        'start': int('The start position (zero-based) of the recognized URL in the user's description.'),
                        'url': str('The URL in the format entered by the user.')
                    }
                ]
            },
            'followers_count': int('Number of users who follow this user.'),
            'following_count': int('Number of users this user is following.'),
            'id': int('Unique identifier of this user.'),
            'listed_count': int('Number of lists that include this user.),
            'location': str('The location specified in the user's profile.'),
            'profile_banner_url': str('The URL to the banner image for this user.'),
            'profile_image_url': str('The URL to the avatar for this user.'),
            'profile_website_urls': {
                {
                    "display_url": str('The URL as displayed in the user's profile.'),
                    "end": int('The end position (zero-based) of the recognized user's profile website.'),
                    "expanded_url": str('The fully resolved URL.'),
                    "start": int('The start position (zero-based) of the recognized user's profile website.'),
                    "url": str('The URL in the format entered by the user.')
                }
            },
            'protected': bool('Indicates if this user's Tweets are private.'),
            'friendly_name': str('The friendly name of this user.'),
            'tweet_count': int('Number of Tweets (including Retweets) posted by this user.')
            'username': str('The Twitter handle (screen name) of this user.'),
        }

    Raises
    ------
    TypeError
        If cannot get user response from the client.
    """
    response = client.get_user(
        username=username, user_fields=user_parameters['user_fields'])
    if not response or not response.data:
        raise TypeError(f'Failed to fetch user info.')
    
    profile = response.data
    user = {
        'id': profile.id,
        'friendly_name': profile.name,
        'username': profile.username,
    }

    if profile.created_at:
        user['created_at'] = profile.created_at.isoformat()
    if profile.description:
        user['description'] = {'content': profile.description}
    if profile.location:
        user['location'] = profile.location
    if profile.profile_image_url:
        user['profile_image_url'] = string.replace_last(
            profile.profile_image_url, '_normal')
    if profile.protected is not None:
        user['protected'] = profile.protected
    
    public_metrics = profile.public_metrics
    if public_metrics:
        user['followers_count'] = public_metrics['followers_count']
        user['following_count'] = public_metrics['following_count']
        user['tweet_count'] = public_metrics['tweet_count']
        user['listed_count'] = public_metrics['listed_count']

    entities = profile.entities
    if entities:
        if 'url' in entities and 'urls' in entities['url']:
            user['profile_website_urls'] = entities['url']['urls']
        if 'description' in entities:
            description_url = entities['description']
            if 'hashtags' in description_url:
                user['description']['hashtags'] = description_url['hashtags']
            if 'mentions' in entities['description']:
                user['description']['mentions'] = description_url['mentions']
            if 'urls' in entities['description']:
                user['description']['urls'] = description_url['urls']
    return user


def _get_options() -> dict:
    parser = argparse.ArgumentParser(
        description='Downloads user info and tweets from Twitter.')
    parser.add_argument(
        '-c', '--credentials', default='configs/credentials.json', type=str, 
        help='Path to Twitter credential file.')
    parser.add_argument(
        '-s', '--settings', default='configs/twitter.json', type=str, 
        help='Path to Twitter setting file')
    parser.add_argument(
        '-o', '--output', default='../data/texts', type=str, 
        help='Path to output directory.')
    parser.add_argument(
        '-t', '--test', action='store_true', default=False, 
        help='Runs in test mode (early stop).')
    return parser.parse_args()


def _parse_tweet(response: Tweet) -> dict:
    tweet = {
        'id': response.id,
        'text': {
            'content': response.text,
        },
    }
    if response.created_at:
        tweet['created_at'] = response.created_at.isoformat()
    if response.source:
        tweet['source'] = response.source
    
    public_metrics = response.public_metrics
    if public_metrics:
        tweet['retweet_count'] = public_metrics['retweet_count']
        tweet['reply_count'] = public_metrics['reply_count']
        tweet['like_count'] = public_metrics['like_count']
        tweet['quote_count'] = public_metrics['quote_count']

    entities = response.entities
    if entities:
        if 'hashtags' in entities:
            tweet['text']['hashtags'] = entities['hashtags']
        if 'mentions' in entities:
            tweet['text']['mentions'] = entities['mentions']
        if 'urls' in entities:
            tweet['text']['urls'] = entities['urls']
    return tweet


if __name__ == '__main__':
    options = _get_options()
    io.make_directory(options.output)
    credentials = io.load_json(options.credentials)['twitter']
    settings = io.load_json(options.settings)
    tweet_parameters = settings['tweet_parameters']
    username = settings['username']

    print(color.get_info('Authenticating...'))
    client = get_client(credentials)
    print()

    # Stage 1: Gets user info
    print(color.get_info(f"Fetching user info of {username}..."))
    user = get_user(client, username, settings['user_parameters'])

    # TODO: Finds an automatic method to get the URL of the banner image.
    if 'profile_banner_url' in settings:
        user['profile_banner_url'] = settings['profile_banner_url']

    user_path = io.join_paths(options.output, USER_OUTPUT_FILENAME)
    archive_user(user_path)
    io.dump_json(user, user_path)
    print(f"Saved user info of {username} to '{user_path}'.")
    print()

    # Stage 2: Gets Tweets
    print(color.get_info(f"Fetching Tweet(s) of {username}..."))
    tweets_path = io.join_paths(options.output, TWEETS_OUTPUT_FILENAME)
    tweets, since_id = archive_tweets(tweets_path)

    # TODO: Gets Tweets older then the most recent 3200 ones.
    new_tweets, pagination_token = get_tweets(
        client, user['id'], settings['tweet_parameters'], since_id=since_id)
    tweets.update(new_tweets)
    print(f'Fetched {len(tweets)} tweets.')

    while pagination_token:
        new_tweets, pagination_token = get_tweets(
            client, user['id'], settings['tweet_parameters'], 
            pagination_token=pagination_token, since_id=since_id)
        tweets.update(new_tweets)
        print(f'Fetched {len(tweets)} tweets.')

        if options.test:
            break

    io.dump_json(tweets, tweets_path)
    print(f"Saved {len(tweets)} tweets of {username} to '{tweets_path}'.")
    print()

    # Stage 3: Collects URLs
    print(color.get_info(f'Collecting unique URLs...'))
    urls = get_urls(user, tweets)
    urls_path = io.join_paths(options.output, URLS_OUTPUT_FILENAME)
    archive_urls(urls_path)
    io.dump_json(urls, urls_path)
    print(f"Saved {len(urls)} unique URLs to '{urls_path}'.")
    print()

    print(color.get_ok('Done.'))
