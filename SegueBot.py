import facebook
import wikipedia
from pathlib import Path
import urllib.request
import time
import datetime
import numpy as np
import subprocess
import webbrowser as wb
#from pynput.keyboard import Key,Controller
from PIL import Image, ImageFont, ImageDraw
import textwrap
import os

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
    if not im:
        return False
    img = [imgs for imgs in im if 'png' in imgs or 'jpg' in imgs or 'jpeg' in imgs]
    if not img:
        return False
    url = img[np.random.randint(len(img))]
    form = url.split('.')[-1]
    #if form=='svg':
    #    return './nominal.png'
    urllib.request.urlretrieve(url, './image.{}'.format(form))
    return '/home/fer/Documents/Bots/Facebook/SegueBot/image.{}'.format(form)

#def get_screenshot(page):
#    subprocess.run(["/bin/bash","-i","-c","disp"])
#    wb.open(wikipedia.page(page,auto_suggest=False).url)
#    time.sleep(10)
#    subprocess.run(["scrot","./image.png"])
#    keyboard = Controller()
#    keyboard.press(Key.ctrl)
#    keyboard.press('w')
#    keyboard.release(Key.ctrl)
#    keyboard.press('w')
#    image = Image.open("./image.png")
#    image = image.crop((170,370,1920,1080))
#    image.save("./image.png")
#    return "./image.png"

def get_first():
    return wikipedia.random()

def get_next(page):
    page = wikipedia.page(page,auto_suggest=False)
    links = page.links
    while True:
        nex = np.random.randint(len(links))
        try:
            testpage = wikipedia.page(links[nex],auto_suggest=False).url
            return links[nex]
        except:
            pass

def gen_text(chain):
    if len(chain)>1:
        text = "The previous page, {}, has taken us to this new page: {} ({}).".format(chain[-2],chain[-1],wikipedia.page(chain[-1],auto_suggest=False).url)
    else:
        text = "A new segue is starting! The first page is {} ({}).".format(chain[0],wikipedia.page(chain[-1],auto_suggest=False).url)
    return text

def gen_comment(chain):
    text = "The compete segue so far has been like this:\n"
    for link in chain:
        text+=link+'\n'
    return text

def gen_final_img(chain):
    img = Image.new("RGB",(1800,1800))
    draw = ImageDraw.Draw(img)
    for il, link in enumerate(chain):
        size, lines = get_size_and_lines(link,draw)
        draw.text(((il>=50)*900,(il%50)*36),textwrap.fill(link,len(link)//lines+lines-1),font=get_font(size))
    img.save("final_img.png")

def get_font(size):
    try:#Linux
        font = ImageFont.truetype("Lato-Medium.ttf",size)
    except:#Windows
        font = ImageFont.truetype("arial.ttf",size)
        #mac users BTFO
    return font

def get_size_and_lines(text,draw):
    font1 = get_fontsize(text,draw)
    font2 = get_fontsize(textwrap.fill(text,len(text)//2+1),draw)
    font3 = get_fontsize(textwrap.fill(text,len(text)//3+2),draw)
    if font1>font3 and font1>font2:
        font = font1
        lines = 1
    elif font2>font3:
        font = font2
        lines = 2
    else:
        font = font3
        lines = 3
    return min(font,90), lines

def get_fontsize(text,draw,maxlenx = 900, maxleny = 36):
    pw = []
    ph = []
    for i in range(10):
        font = get_font((i+1)*10)
        ps = draw.textsize(text,font)
        pw.append(ps[0])
        ph.append(ps[1])
        #print (pw, ph)
    return int(min(10*maxlenx//np.mean(np.diff(pw)),10*maxleny//np.mean(np.diff(ph))))

def main(chain=[]):
    chain = list(chain)
    if not chain:
        title = get_first()
    else:
        if len(chain)==100:
            gen_final_img(chain)
            gr,p_id = upload("We've finished another Segue, here is the complete list",getAccessToken(),"final_img.png")
            os.remove('chain.npy')
            return True
        title = chain[0]
        while title in chain:
            title = get_next(chain[-1])
    chain.append(title)
    text = gen_text(chain)
    #try:
    img_path = get_image(chain[-1])
    #except:
    #img_path = '/home/pi/Documents/SegueBot/nominal.png'
    if not img_path:
        #img_path = get_screenshot(title)
        img_path = '1x1.png'
        text+='\nNo image found for this article :('
    gr, p_id = upload(text,getAccessToken(),img_path) 
    comment = gen_comment(chain)
    c_id = upload_comment(gr, p_id, comment)['id']
    #print(text)
    #print(comment)
    np.save('chain',chain)
