
import re
import hashlib
import hmac
import random
import string
from string import letters
import logging
import json

from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import images
from google.appengine.api import mail
from google.appengine.api import app_identity

import cloudstorage as gcs

#for mandrill api
from google.appengine.api import urlfetch

import model

app_id = app_identity.get_application_id()

secret = 'Est!eMi001'
sender_email = "emile.esterhuizen@gmail.com"

# Mandrill
mandrill_key = "9y6hFh8u9Ii6IZj5Ib2Mbg"# "qODMJ7be5Cy68y7M7z6q4w"

# Twitter
twitter_consumer_key = "aUYWh62q9x9k1fL1i65fsgwJm"
twitter_consumer_secret = "BKYCrbAs61xYTXYuxc3OabAiLf7noMExJFQqYEC2Sy91Gl4jfi"


#PW HASHING
def make_pw_hash(name, pw, salt = None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)
    
def make_salt(length=5):
    return ''.join(random.choice(letters) for x in xrange(length))
    
# returns a cookie with a value value|hashedvalue
def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())
# returns the origional value and validates if given hashed cookie matches our hash of the value    
def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val
        
def valid_pw(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)


#REGEX for register validtion
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return email and EMAIL_RE.match(email)
    
def request_blob_url(self, callback_url, max_bytes):
    upload_url = blobstore.create_upload_url(callback_url, max_bytes)
    return upload_url
    
def send_gmail(email, subject, body):
    try:
        logging.error("sending subscription mail")
        message = mail.EmailMessage(sender="Emile <%s>" % sender_email,
                                subject=subject)
        message.to = email
        message.html = body
        message.send()
    except:
        logging.error("couldnt send gmail... probably invalid email")




def generate_random_token(N):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))


#saving blobkey to seller obj along with serving url
def save_blob_to_image_obj(blob_key, price, title, description):
    img_url = images.get_serving_url(blob_key)
    portfolio_image = model.Images(img_url=img_url, img_key=blob_key, price=price, title=title, description=description)
    portfolio_image.put()
    return img_url

def save_gcs_to_media(gcs_filename, serving_url):
    media = model.Media(gcs_filename=gcs_filename, serving_url=serving_url)
    media.put()
    return media.key

def delete_media(gcs_filename):
    images.delete_serving_url(blobstore.create_gs_key(gcs_filename))
    gcs.delete(gcs_filename[3:])
    return True

def send_mandrill_mail(subject, html, text, email_list):
    
    url = "https://mandrillapp.com/api/1.0/messages/send.json"

    form_json = {
            "key": mandrill_key,
            "message": {
                "html": html,
                "text": text,
                "subject": subject,
                "from_email": sender_email,
                "from_name": "Emile",
                "to": email_list,
                "headers": {
                    "Reply-To": sender_email
                },
                "important": False,
                "track_opens": True,
                "track_clicks": True,
                "auto_text": None,
                "auto_html": None,
                "inline_css": None,
                "url_strip_qs": None,
                "preserve_recipients": False,
                "view_content_link": None,
                "bcc_address": None,
                "tracking_domain": None,
                "signing_domain": "http://hollowfish.com",
            },
            "async": False,
            "ip_pool": "Main Pool",
            "send_at": None
        }
    

    result = urlfetch.fetch(url=url, payload=json.dumps(form_json), method=urlfetch.POST)

    logging.error("MANDRILL RESULT")

    logging.error(dir(result))
    logging.error(result.status_code)
    logging.error(json.loads(result.content))
    
    
    
    
    
    
    
    
    
    