#import facebook
import wikipedia
#from pathlib import Path
import BotUtils as BU
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
    try:
        links = page.links
    except KeyError:
        return "ABORT"
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
        lines,size = BU.Font.get_wrapped_text(link,draw,900,36)
        draw.text(((il>=50)*900,(il%50)*36),textwrap.fill(link,len(link)//lines+lines-1),font=BU.Font.get_font(size))
    img.save("final_img.png")


def main(chain=[]):
    chain = list(chain)
    if not chain:
        title = get_first()
    else:
        if len(chain)==100:
            gen_final_img(chain)
            gr,p_id = BU.Facebook.upload("We've finished another Segue, here is the complete list",getAccessToken(),"final_img.png")
            os.remove('chain.npy')
            return True
        title = chain[0]
        while title in chain and not (title=="ABORT"):
            title = get_next(chain[-1])
    if title=="ABORT":
        gen_final_img(chain)
        gr,p_id = BU.Facebook.upload("We've PREMATURELY finished another Segue, here is the complete list",BU.getAccessToken(),"final_img.png")
        os.remove('chain.npy')
        return True

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
