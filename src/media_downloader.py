"""This scripts downloads media from collected URLs.

The default 
- Raw URLs file locates at '../data/texts/urls_raw.json'.
- Domains config file locates at 'configs/domains.json'.
- Output media directory locates at '../data/media'.
- Output texts directory locates at '../data/texts'.

Example usage:
    python media_downloader.py \
        -i "path/to/the/urls_raw/file" \
        -s "path/to/the/domains/config/file" \
        -o "path/to/the/media/output/directory"\
        -x "path/to/the/texts/output/directory"
"""

from __future__ import annotations
import argparse
import os
from subprocess import CompletedProcess

from utils import color, io, shell, string # pylint: disable=import-error


URL_OUTPUT_FILENAME = 'urls.json'


def config_downloads(urls: dict, domains: dict) -> tuple[dict, dict]:
    """Configs media downloads.

    Maps URLs to the expanded ones, omits skipped URLs, removes redundant tokens
    from URLs, and gets downloaders depending on URLs.

    Parameters
    ----------
    urls: dict
        Mappings from URL to its local download directory.
        Format:
        {
            str('URL'): str('Local download directory.')
        }
    domains: dict
        Contains domains of URLs to expand/map, skip, clean (redundancy), and
        select downloaders. Domains of locally available media should also be 
        skipped during download. These local media are downloaded before the
        target Twitter account went private. (If the account is still public,
        leave the 'local' attribute empty in the domains config file.)
        Format:
        {
            'map': {
                str('A shortened URL'): str('The fully expanded URL.')
            },
            'local': [
                str('A domain of media already available locally. e.g. Twitter private accounts.')
            ],
            'skip': [
                str('A domain that does not potentially contain media. e.g. Live streaming.')
            ],
            'redundant': {
                str('A domain where its URLs may contain redundant parameters.'): [
                    str('A rundant parameter. e.g. /photo/1 in the end of a Twitter status.')
                ]
            },
            'downloaders': {
                'default': str('The default downloader.'),
                str('A domain that requires a specific downloader'): str('A specific downloader.')
            }
        }

    Returns
    -------
    dict
        Processed download configs. Maps each processed URL to its downloader
        and local download path.
        Format:
        {
            str('A processed URL'): {
                'downloader': str('Specific downloader required to download the media.'),
                'path': str('Local dowload directory of the media.')
            }
        }
    dict
        Maps each URL to its local download directory. Domains of locally 
        available media are preserved, while skipped domains are removed.
    """
    skip_domains = set(domains['skip'])
    local_domains = set(domains['local'])
    urls_resolved = {}
    downloads = {}

    for url, path in sorted(urls.items()):
        url_download = url
        url_download = _map_domain(url_download, domains['map'])
        if _get_domain(url_download, skip_domains):
            continue

        if _get_domain(url_download, local_domains):
            urls_resolved[url] = path
        else:
            url_download = _clean_domain(url_download, domains['redundant'])
            downloader = _get_downloader(url_download, domains['downloaders'])
            
            if url_download not in downloads:
                downloads[url_download] = {
                    'downloader': downloader,
                    'path': path
                }
            urls_resolved[url] = downloads[url_download]['path']
    return downloads, urls_resolved


def download_media(downloader: str, url: str, dst: str) -> CompletedProcess:
    """Downloads a piece of media.

    Parameters
    ----------
    downloader: str
        Represents a media downloader, either 'you-get' or 'youtube-dl'.
    url: str
        URL to download.
    dst: str
        Local download directory.
    
    Returns
    -------
        The execution result including the following attribute:
        - returncode: an integer representing the exit status.
            0 indicates a success while 1 indicates an error.

    Raise
    -----
        ValueError if unsupported downloader.
    """
    if downloader == 'you-get':
        return shell.run([
            'you-get', 
            '--skip-existing-file-size-check', # No overwrite
            url,
            '-o', # Output directory
            dst
        ], capture_output=False)
    elif downloader == 'youtube-dl':
        return shell.run([
            'youtube-dl',
            '-i', # Continues on download errors
            '-w', # No overwrite
            '--write-thumbnail', # Downloads the thumbnail. Same filename.
            url,
            '-o', # Output filename template
            io.join_paths(dst, '%(title)s-%(id)s.%(ext)s')
        ], capture_output=False)
    else:
        raise ValueError(f"Unsupported downloader.")


def _get_domain(url: str, domains: tuple[dict, list, set]) -> str:
    for domain in domains:
        if url.startswith(domain):
            return domain
    return None


def _map_domain(url: str, domains: dict) -> str:
    domain = _get_domain(url, domains)
    if domain:
        return string.replace_first(url, domain, domains[domain])
    return url


def _clean_domain(url: str, domains: dict) -> str:
    domain = _get_domain(url, domains)
    if domain:
        for target in domains[domain]:
            url = string.remove_last(url, target)
    return url


def _get_downloader(url: str, domains: dict) -> str:
    domain = _get_domain(url, domains)
    if domain:
        return domains[domain]
    return domains['default']


def _get_options() -> dict:
    parser = argparse.ArgumentParser(
        description='Downloads images and videos from URLs.')
    parser.add_argument(
        '-i', '--input', default='../data/texts/urls_raw.json', type=str, 
        help='Path to the raw URLs file.')
    parser.add_argument(
        '-s', '--settings', default='configs/domains.json', type=str, 
        help='Path to the domain config file.')
    parser.add_argument(
        '-o', '--output', default='../data/media', type=str, 
        help='Path to the media output directory.')
    parser.add_argument(
        '-x', '--export', default='../data/texts', type=str, 
        help='Path to the texts output directory.')
    return parser.parse_args()


if __name__ == '__main__':
    options = _get_options()
    io.make_directory(options.output)
    urls_raw = io.load_json(options.input)
    domains = io.load_json(options.settings)

    # Stage 1: Configs downloads
    print(color.get_info('Configuring downloads...'))
    downloads, urls = config_downloads(urls_raw, domains)
    urls_path = io.join_paths(options.export, URL_OUTPUT_FILENAME)
    if os.path.isfile(urls_path):
        archive_path = io.archive_file(urls_path)
        print(f"Archived '{urls_path}' to '{archive_path}'.")
    io.dump_json(urls, urls_path)
    print(f"Saved {len(urls)} valid URLs to '{urls_path}''.")
    print()

    # Stage 2: Downloads media
    print(color.get_info(f'{len(downloads)} media to download.'))
    error_count = 0
    for i, url in enumerate(downloads):
        downloader = downloads[url]['downloader']
        dst = io.join_paths(options.output, downloads[url]['path'])
        print(color.get_highlight(
            f"({i + 1}/{len(downloads)}) "
            f"Downloding media from '{url}' to '{dst}'..."))

        result = download_media(downloader, url, dst)
        if result.returncode:
            error_count += 1
    print()
    
    messages = []
    if error_count > 0:
        messages.append(color.get_error(f'Failure: {error_count}'))
    if len(downloads) - error_count > 0:
        messages.append(color.get_ok(f'Success: {len(downloads) - error_count}'))
    print(', '.join(messages) + '.')
