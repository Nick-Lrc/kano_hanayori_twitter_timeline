import pickle
from datetime import datetime

def import_data(src):
    with open(src, 'rb') as f:
        return pickle.load(f)

def write_tweet(tid, tweet):
    dst.write(f'推特 id : {tid}\n')
    dst.write(f"发布时间: {datetime.strptime(tweet['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ')}\n")
    dst.write(f"回复数量: {tweet['reply_count']}\n")
    dst.write(f"转推数量: {tweet['retweet_count']}\n")
    dst.write(f"获赞数量: {tweet['like_count']}\n")
    dst.write(f"引用数量: {tweet['quote_count']}\n")
    if tweet['urls']:
        dst.write(f'媒体地址:\n')
        for i, url in enumerate(tweet['urls']):
            dst.write(f"       {i}: {url['expanded_url']}\n")
    dst.write(f"发布内容:\n")
    dst.write('\n')
    dst.write(f"{tweet['text']}\n")

def write_user(user_info, dst):
    uid = list(user_info.keys())[0]
    info = user_info[uid]
    dst.write(f'id      : {uid}\n')
    dst.write(f"名字    : {info['name']}\n")
    dst.write(f"用户名  : {info['username']}\n")
    dst.write(f"头像地址: {info['profile_image_url']}\n")
    dst.write(f"加入时间: {datetime.strptime(info['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ')}\n")
    dst.write(f"推特数量: {info['tweet_count']}\n")
    dst.write(f"粉丝数量: {info['followers_count']}\n")
    dst.write(f"关注数量: {info['following_count']}\n")
    dst.write('自我介绍:\n')
    dst.write('\n')
    dst.write(f"{info['description']}\n")

def write_bar(dst):
    dst.write('---\n')

if __name__ == '__main__':
    user_info = import_data('user_info.pickle')
    log = import_data('log.pickle')

    dst = open('kano_hanayori_twitter.txt', 'w', encoding='utf-8')
    write_bar(dst)
    write_user(user_info, dst)
    
    for tid, tweet in sorted(log.items(), reverse=True):
        write_bar(dst)
        write_tweet(tid, tweet)
    write_bar(dst)
    dst.close()
