import facebook
import wikipedia
from pathlib import Path
import urllib.request
import time
import datetime
import numpy as np

def upload_comment(graph, post_id, message="", img_path=None):
    if img_path:
        post = graph.put_photo(image=open(img_path, 'rb'),
                               album_path='%s/comments' % (post_id),
                               message=message)
    else:
        post = graph.put_object(parent_object=post_id,
                                connection_name="comments",
                                message=message)
    return post

def upload(message, access_token, img_path=None):
    graph = facebook.GraphAPI(access_token)
    if img_path:
        post = graph.put_photo(image=open(img_path, 'rb'),
                               message=message)
    else:
        post = graph.put_object(parent_object='me',
                                connection_name='feed',
                                message=message)
    return graph, post['post_id']

def getcomments(graph,post_id):#deprecated
    comments = graph.get_connections(post_id,connection_name='comments')
    comments = comments['data']
    if comments:
        ids = []
        texts = []
        for comment in comments:
            ids.append(comment['from']['id'])
            texts.append(comment['message'])
        return ids,texts
    else:
        return [],[]

def getAccessToken(filename='access_token.txt'):
    return Path(filename).read_text().strip()
 
def get_image(link,debug=False):
    if debug:
        print(link)
    form = 'svg'
    page = wikipedia.page(link,auto_suggest=False)
    im = page.images
    img = [imgs for imgs in im if 'png' in imgs or 'jpg' in imgs or 'jpeg' in imgs]
    url = img[np.random.randint(len(img))]
    form = url.split('.')[-1]
    if form=='svg':
        return '/home/pi/Documents/SegueBot/nominal.png'
    urllib.request.urlretrieve(url, '/home/pi/Documents/SegueBot/image.{}'.format(form))
    return '/home/pi/Documents/SegueBot/image.{}'.format(form)

def get_first():
    return wikipedia.random()

def get_next(page):
    page = wikipedia.page(page,auto_suggest=False)
    links = page.links
    while True:
        nex = np.random.randint(len(links))
        try:
            testpage = wikipedia.page(nex)
            return links[np.random.randint(len(links))]
        except:
            pass

def gen_text(chain):
    if len(chain)>1:
        text = "The previous page, {}, has taken us to this new page: {}.".format(chain[-2],chain[-1])
    else:
        text = "A new segue is starting! The first page is {}.".format(chain[0])
    return text

def gen_comment(chain):
    text = "The compete segue so far has been like this:\n"
    for link in chain:
        text+=link+'\n'
    return text

def main(chain=[]):
    chain = list(chain)
    if not chain:
        title = get_first()
    else:
        title = chain[0]
        while title in chain:
            title = get_next(chain[-1])
    chain.append(title)
    text = gen_text(chain)
    try:
        img_path = get_image(chain[-1])
    except:
        img_path = '/home/pi/Documents/SegueBot/nominal.png'
    #gr, p_id = upload(text,gettAccessToken(),img_path) 
    comment = gen_comment(chain)
    #c_id = upload_comment(gr, p_id, comment)['id']
    print(text)
    print(comment)
    np.save('chain',chain)
