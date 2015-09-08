#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import jinja2
import logging
import os
from string import letters
import json
from datetime import datetime, timedelta
import datetime
import time
import urllib
from urlparse import urlparse
import re

from google.appengine.ext import ndb
from google.appengine.api import images
from google.appengine.api import memcache
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import mail
from google.appengine.datastore.datastore_query import Cursor

import model
import utils

import cloudstorage as gcs

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

def blog_date(value):
    return value.strftime("%d/%m/%y")
jinja_env.filters['blog_date'] = blog_date

def check_none(value):
    if value:
        return value
    else:
        return ""
jinja_env.filters['check_none'] = check_none

class MainHandler(webapp2.RequestHandler):

#TEMPLATE FUNCTIONS    
    def write(self, *a, **kw):
        self.response.headers['Host'] = 'localhost'
        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write(*a, **kw)
        
    def render_str(self, template, **params):
        params['user'] = self.user
        #params['buyer'] = self.buyer
        t = jinja_env.get_template(template)
        return t.render(params)
        
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    #JSON rendering
    def render_json(self, obj):
        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Host'] = 'localhost'
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.out.write(json.dumps(obj))
   
    #COOKIE FUNCTIONS
    # sets a cookie in the header with name, val , Set-Cookie and the Path---not blog    
    def set_secure_cookie(self, name, val):
        cookie_val = utils.make_secure_val(val)
        self.response.headers.add_header('Set-Cookie', '%s=%s; Path=/' % (name, cookie_val))# consider imcluding an expire time in cookie(now it closes with browser), see docs
    # reads the cookie from the request and then checks to see if its true/secure(fits our hmac)    
    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        if cookie_val:
            cookie_val = urllib.unquote(cookie_val)
        return cookie_val and utils.check_secure_val(cookie_val)
    
    def login(self, user):
        self.set_secure_cookie('nic_estappspotcom', str(user.key.id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'nic_estappspotcom=; Path=/')
    
    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('nic_estappspotcom')

        self.user = uid and model.User.by_id(int(uid))
        
class Register(MainHandler):
    def get(self):
        user_obj = self.user
        if user_obj:
            self.redirect("/")
        else:
            self.render("register.html")
    def post(self):
        name = self.request.get('name')
        email = self.request.get('email')
        password = self.request.get('password')
        verify_password = self.request.get('verify_password')
        key = self.request.get('key')
        
        error = False
        error_name = ""
        error_password = ""
        error_email = ""
        error_verify = ""
        
        if not utils.valid_username(name):
            error_name="Your username needs to be between 3 and 20 characters long and only contain numbers and letters"
            error = True
            
        if not utils.valid_password(password):
            error_password="Your password needs to be between 3 and 20 characters long"
            error = True
            
        if not utils.valid_email(email):
            error_email="Please type in a valid email address"
            error = True
            
        if password != verify_password:
            error_verify="Please ensure your passwords match"
            error = True
            
        if key != "Nicholas001":
            error_key="Please provide the correct key"
            error = True
        
        if not error:
            pw_hash = utils.make_pw_hash(name, password)
            user = model.User(parent=model.users_key(), name=name, email=email, pw_hash=pw_hash)
            user.put()
            self.login(user)
            self.redirect('/fileupload')
            
        else:
            js_code = "$('#register').modal('show');"
            data = {
                'error_name':error_name,
                'error_password':error_password,
                'error_email':error_email,
                'error_verify':error_verify,
                'error_key':error_key,
                'js_code':js_code
            }

            self.render('register.html', data=data)
            
            """
            In order to manually show the modal pop up you have to do this

            $('#myModal').modal('show');
            You previously need to initialize it with show: false so it won't show until you manually do it.

            $('#myModal').modal({ show: false})
            """
class LoginRegister(MainHandler):
    def get(self):
        data = None
        self.render("login.html", data=data)
        
class Login(MainHandler):
    def get(self):
        self.render("login.html")
    def post(self):
        email = self.request.get('email')
        password = self.request.get('password')

        s = model.User.login(email, password)
        if s:
            self.login(s)
            self.redirect('/fileupload')
        else:
            self.redirect('/login')
        
class Logout(MainHandler):
    def get(self):
        self.logout()
        self.redirect('/')
        
        
# ==============================
# Client Facing
# ==============================
        
class Home(MainHandler):
    def get(self):

        code = self.request.get("code")

        if code:
            self.redirect("/testapiresponse?code=%s" % code)
        else:
            year = datetime.datetime.now().year
            curs = Cursor(urlsafe=self.request.get('cursor'))
            projects, next_curs, more = model.Project.query().order(-model.Project.created).fetch_page(20, start_cursor=curs)
            if more and next_curs:
                next_curs = next_curs.urlsafe()
            else:
                next_curs = False

            self.render('index.html', year=year, projects=projects, next_curs=next_curs)
        
class Project(MainHandler):
    def get(self, project_id):

        project = model.Project.get_by_id(int(project_id))

        curs = Cursor(urlsafe=self.request.get('cursor'))
        responses, next_curs, more = model.Response.query( model.Response.project == project.key ).order(-model.Response.created).fetch_page(20, start_cursor=curs)
        if more and next_curs:
            next_curs = next_curs.urlsafe()
        else:
            next_curs = False

        self.render("project_page.html", project=project, responses=responses)

class SaveProject(MainHandler):
    def post(self):
        email = self.request.get("email")
        name = self.request.get("name")
        project_title = self.request.get("project_title")
        value = self.request.get("value")
        currency = self.request.get("currency")
        description = self.request.get("description")

        non_decimal = re.compile(r'[^\d]+')
        parsed_value = non_decimal.sub('', value)
        try:
            parsed_value = int(parsed_value)
            if parsed_value <= 0:
                value = False
        except:
            value = False

        email_user = model.EmailUser.query(model.EmailUser.email==email).get()

        if not email_user:
            email_user = model.EmailUser(email=email, name=name)
            email_user.put()

        if email_user and project_title and value and currency and description:
            project = model.Project(name=project_title, value=value, currency=currency, description=description, email_user=email_user.key)
            project.put()

            self.render_json({
                "message": "success",
                "project_url": "/project/%s" % project.key.id(),
                "project_id": project.key.id(),
                "title": project_title,
                "value": value,
                "currency": currency,
                "description": description
                })
        else:
            error_ids = []
            long_message = "Please complete the necessary fields"
            if not project_title:
                error_ids.append("project_title")
            if not email:
                error_ids.append("email")
            if not value:
                error_ids.append("value")
                long_message = "Please complete the necessary fields, we need to pay them something."
            if not currency:
                error_ids.append("currency")
            if not description:
                error_ids.append("description")
            self.render_json({
                "message": "fail",
                "long_message": long_message,
                "errors": error_ids
                })

class SaveResponse(MainHandler):
    def post(self, project_id):
        website = self.request.get("website")
        hook = self.request.get("hook")

        project = model.Project.get_by_id(int(project_id))

        netloc = urlparse(website)
        netloc = netloc.netloc
        if "www." in netloc:
            netloc.replace("www.", "")

        existing_response = False
        if project:
            existing_response_netloc = model.Response.query(model.Response.netloc==netloc, model.Response.project==project.key).get()
            existing_response_hook = model.Response.query(model.Response.hook==hook, model.Response.project==project.key).get()

            if existing_response_netloc or existing_response_hook:
                existing_response = True

        if not existing_response:
            if project and website and hook:
                response = model.Response(website=website, hook=hook, project=project.key, netloc=netloc)
                response.put()

                self.render_json({
                    "message": "success",
                    "long_message": "Your response has been posted, thanks!",
                    "project_id": project_id,
                    "response_id": response.key.id(),
                    "website": website,
                    "hook": hook
                    })
            else:
                error_ids = []
                if not website:
                    error_ids.append("website")
                if not hook:
                    error_ids.append("hook")
                self.render_json({
                    "message": "fail",
                    "long_message": "Please correct your response",
                    "errors": error_ids
                    })
        else:
            self.render_json({
                "message": "fail",
                "long_message": "There's already a response like that",
                })

# ==============================
# Admin
# ==============================

class Admin(MainHandler):
    def get(self):
        self.render('cms.html')

class AdminBlog(MainHandler):
    def get(self):
        error = self.request.get("error")
        posts = model.Blog.query().order(-model.Blog.created).fetch(20)

        media_curs = Cursor(urlsafe=self.request.get('media_cursor'))
        media, next_media_curs, more = model.Media.query().order(-model.Media.created).fetch_page(5, start_cursor=media_curs)
        if more and next_media_curs:
            next_media_curs = next_media_curs.urlsafe()
        else:
            next_media_curs = False

        self.render("admin_blogs.html", posts=posts, error=error, media=media, next_media_curs=next_media_curs)

    def post(self):

        title = self.request.get("title")
        post_body = self.request.get("post_body")
        short_text = self.request.get("short_text")
        featured = self.request.get("featured")
        post_id = self.request.get("post_id")
        cover_link = self.request.get("cover_link")
        url = self.request.get("url")
        blog_type = self.request.get("blog_type")

        if not post_id:
            if featured:
                featured = True
            else:
                featured = False

            post = model.Blog(title=title, post=post_body, featured=featured, short_text=short_text, url=url, blog_type=blog_type)
            post.put()
        else:
            post = model.Blog.get_by_id(int(post_id))

        f = self.request.get('image')

        cover = True
        if not f:
            if not cover_link:
                cover = False

        logging.error(" - - - - COVER - - - - ")
        logging.error(cover)

        if cover:
            # - - - 
            serving_url = ''#just assign it adn reassign later

            time_stamp = time.time()

            #delete old profile image
            # if user_obj.gcs_filename:
            #     images.delete_serving_url(blobstore.create_gs_key(user_obj.gcs_filename))
            #     gcs.delete(user_obj.gcs_filename[3:])

            fname = '/%s.appspot.com/post_%s_%s.jpg' % (utils.app_id, post.key.id(), time_stamp)

            gcs_file = gcs.open(fname, 'w', content_type="image/jpeg")
            gcs_file.write(self.request.get('image'))
            gcs_file.close()

            gcs_filename = "/gs%s" % fname
            serving_url = images.get_serving_url(blobstore.create_gs_key(gcs_filename))
            media_key = utils.save_gcs_to_media(gcs_filename, serving_url)

            post.gcs_filename = gcs_filename
            post.cover_img = serving_url
            post.media_obj = media_key
            post.put()

            # self.render_json({
            #     "message": "success",
            #     "long_message": "uploaded cover image to gcs",
            #     "serving_url": serving_url
            # })
            
            self.redirect("/admin/blog")
        else:
            self.redirect("/admin/blog?error=no_cover")

class UploadMedia(MainHandler):
    def get(self):
        curs = Cursor(urlsafe=self.request.get('cursor'))
        media, next_curs, more = model.Media.query().order(-model.Media.created).fetch_page(15, start_cursor=curs)
        #blogs = model.Blog.query().order(-model.Blog.created).fetch(20)
        if more and next_curs:
            next_curs = next_curs.urlsafe()
        else:
            next_curs = False

        self.render("upload_media.html", media=media, next_curs=next_curs)

    def post(self):
        serving_url = ''#just assign it adn reassign later

        time_stamp = time.time()

        #delete old profile image
        # if user_obj.gcs_filename:
        #     images.delete_serving_url(blobstore.create_gs_key(user_obj.gcs_filename))
        #     gcs.delete(user_obj.gcs_filename[3:])

        fname = '/%s.appspot.com/post_media_%s.jpg' % ( utisl.app_id, time_stamp)

        gcs_file = gcs.open(fname, 'w', content_type="image/jpeg")
        gcs_file.write(self.request.get('image'))
        gcs_file.close()

        gcs_filename = "/gs%s" % fname
        serving_url = images.get_serving_url(blobstore.create_gs_key(gcs_filename))
        media_key = utils.save_gcs_to_media(gcs_filename, serving_url)

        self.redirect("/admin/upload_media")
        # self.render_json({
        #     "message": "success",
        #     "long_message": "uploaded media to gcs",
        #     "serving_url": serving_url
        # })

class FetchMedia(MainHandler):
    def get(self):
        curs = Cursor(urlsafe=self.request.get('media_cursor'))
        media, next_curs, more = model.Media.query().order(-model.Media.created).fetch_page(5, start_cursor=curs)
        if more and next_curs:
            next_curs = next_curs.urlsafe()
        else:
            next_curs = False

        # media_obj = {"media": [], "next_curs": next_curs}
        # for m in media:
        #     m_obj = {}
        #     m_obj["serving_url"] = m.serving_url 
        #     media_obj["media"].append(m_obj)


        # self.render_json(media_obj)
        self.render("media_list.html", media=media, next_curs=next_curs)

class AdminApproveBlog(MainHandler):
    def post(self):
        blog_id = self.request.get("blog_id")
        blog_approved = self.request.get("approve_blog")
        blog = model.Blog.get_by_id(int(blog_id))

        if blog_approved:
            blog_approved = True
        else:
            blog_approved = False

        blog.approved = blog_approved
        blog.put()

        self.render_json({
            "message": "success"    
        })

class EditPost(MainHandler):
    def get(self, post_id):
        post = model.Blog.get_by_id(int(post_id))

        media_curs = Cursor(urlsafe=self.request.get('media_cursor'))
        media, next_media_curs, more = model.Media.query().order(-model.Media.created).fetch_page(5, start_cursor=media_curs)
        if more and next_media_curs:
            next_media_curs = next_media_curs.urlsafe()
        else:
            next_media_curs = False

        self.render("edit_post.html", post=post, media=media, next_media_curs=next_media_curs)

    def post(self, post_id):
        title = self.request.get("title")
        post_body = self.request.get("post_body")
        short_text = self.request.get("short_text")
        featured = self.request.get("featured")
        blog_type = self.request.get("blog_type")
        cover_link = self.request.get("cover_link")
        url = self.request.get("url")

        if featured:
            featured = True
        else:
            featured = False

        post = model.Blog.get_by_id(int(post_id))
        post.title = title
        post.post = post_body
        post.featured = featured
        post.short_text = short_text
        post.url = url
        post.blog_type = blog_type
        post.put()

        f = self.request.get('image')

        cover = True
        if not f:
            if not cover_link:
                cover = False

        if cover:
            # - - - 
            serving_url = ''#just assign it adn reassign later

            time_stamp = time.time()

            fname = '/%s.appspot.com/post_%s_%s.jpg' % (utils.app_id, post.key.id(), time_stamp)

            gcs_file = gcs.open(fname, 'w', content_type="image/jpeg")
            gcs_file.write(self.request.get('image'))
            gcs_file.close()

            gcs_filename = "/gs%s" % fname
            serving_url = images.get_serving_url(blobstore.create_gs_key(gcs_filename))
            media_key = utils.save_gcs_to_media(gcs_filename, serving_url)

            post.gcs_filename = gcs_filename
            post.cover_img = serving_url
            post.media_obj = media_key
            post.put()
            
        
        self.redirect("/admin/blog")


#  --------- QUOTES
class AdminQuote(MainHandler):
    def get(self):

        clients = model.Client.query().fetch()
        quotes = model.Quote.query().fetch()

        self.render("admin_quote.html", quotes=quotes, clients=clients)



#  --------- MAILERS
class SendMailer(MainHandler):
    def post(self):
        t = jinja_env.get_template("mailer_inline.html")
        body = t.render()

        text = "We were hoping to send you a wicked cool email, but it looks like something happened along the way. So, in short, to get great websites, mobile apps and games made for your next web project, visit hollowfish.com, if we can't build your project, we'll give you all the advice you need to get going. Emile"

        email_list = []

        subscribers = model.Subscriber.query(model.Subscriber.active == True).fetch()

        for s in subscribers:
            email_obj = {}
            email_obj["email"] = s.email
            if s.name:
                email_obj["name"] = s.name
            else:
                email_obj["name"] = "cool dude(tte)"
            email_obj["type"] = "to"
            email_list.append(email_obj)


        utils.send_mandrill_mail("Get a sweet website / app - HOLLOW FISH", body, text, email_list )

        self.render_json({"message": "success"})



# =====================================
#  Staging stuff
# =====================================

class GetToken(MainHandler):
    def get(self):
        token = utils.generate_random_token(6)
        token_count = model.TokenCount.query().get()
        if not token_count:
            token_count = model.TokenCount()
            token_count.put()

        token = token + str(token_count.count)
        token_count.count += 1
        token_count.put()

        self.render_json({
            "token": token
            })

class CheckUsedToken(MainHandler):
    def get(self):
        token = self.request.get("token")

        token = ""
        existing_token = model.UsedToken.query(model.UsedToken.token==token).get()

        if existing_token:
            result = True
            token = existing_token.token
        else:
            result = False

        # can later include the number of tokens purchased... and soem other payment details
        self.render_json({
            "result": result,
            "token": token
            })

class PayTest(MainHandler):
    def get(self):
        year = datetime.datetime.now().year
        # token = utils.generate_random_token(6)
        token = self.request.get("token")

        registering_email = self.request.get("email")

        # token_count = model.TokenCount.query().get()
        # if not token_count:
        #     token_count = model.TokenCount()
        #     token_count.put()

        # token = token + str(token_count.count)
        # token_count.count += 1
        # token_count.put()

        if token:
            self.render("pay-test.html", year=year, token=token, registering_email=registering_email)
        else:
            self.response.out.write("sorry no valid token was found")

class PayTestNotify(MainHandler):
    def get(self):
        logging.error("LOG POST RESPONSE - - - - - - - - - GET")
        logging.error(self.request.body)
    def post(self):
        logging.error("LOG POST RESPONSE - - - - - - - - - POST")
        logging.error(self.request.body)

        m_payment_id = self.request.get("m_payment_id")
        pf_payment_id = self.request.get("pf_payment_id")
        payment_status = self.request.get("payment_status")
        item_name = self.request.get("item_name")
        item_description = self.request.get("item_description")
        amount_gross = self.request.get("amount_gross")
        amount_fee = self.request.get("amount_fee")
        amount_net = self.request.get("amount_net")
        custom_int1 = self.request.get("custom_int1")
        custom_str1 = self.request.get("custom_str1")
        name_first = self.request.get("name_first")
        name_last = self.request.get("name_last")
        email_address = self.request.get("email_address")
        merchant_id = self.request.get("merchant_id")
        signature = self.request.get("signature")
        # Pass the registered client email as custom_str2
        registered_email_address = self.request.get("custom_str2")

        registered_email_key = None
        registered_email = model.RegisteredEmail.query(model.RegisteredEmail.email == registered_email_address).get()
        if not registered_email:
            if registered_email_address:
                registered_email = model.RegisterEmail(email=registered_email_address)
                registered_email.put()
                registered_email_key = registered_email.key
            else:
                registered_email_key = None

        payment_record = model.PayfastPayment(
            m_payment_id=m_payment_id,
            pf_payment_id=pf_payment_id,
            payment_status=payment_status,
            item_name=item_name,
            item_description=item_description,
            amount_gross=amount_gross,
            amount_fee=amount_fee,
            amount_net=amount_net,
            custom_int1=custom_int1,
            custom_str1=custom_str1,
            name_first=name_first,
            name_last=name_last,
            email_address=email_address,
            merchant_id=merchant_id,
            signature=signature,
            registered_email_address=registered_email_address,
            registered_email=registered_email_key
            )

        payment_record.put()

        used_token = model.UsedToken(token=custom_str1, payment=payment_record.key)
        used_token.put()

        self.render_json({
            "message": "success"
            })


class PayTestSuccess(MainHandler):
    def get(self):
        self.render("pay-success.html")

class PayTestCancel(MainHandler):
    def get(self):
        self.response.out.write("you've cancelled your payment... no worries")

class RegisterEmail(MainHandler):
    def get(self):
        pass
    def post(self):
        email = self.request.get("email")
        user = model.RegisteredEmail.query(model.RegisteredEmail.email == email).get()

        if not user:
            user = model.RegisterEmail(email=email)
            user.put()
            # maybe send confirmation/activation email here...

        self.render_json({
            "message": "success",
            "user_id": user.key.id()
            })




class TestAPI(MainHandler):
    def get(self):

        gmail_oauth = model.GmailAuth.query().get()

        if gmail_oauth:
            logging.error("---------------- already have oauth... redirecting......... ------------")
            self.redirect('/testapiresponse?code=%s' % gmail_oauth.auth_code)
        else:
            import google_credentials

            from oauth2client import client
            flow = client.flow_from_clientsecrets(
            google_credentials.CLIENTSECRETS_LOCATION,
            scope=google_credentials.SCOPES,
            redirect_uri=google_credentials.REDIRECT_URI)

            auth_uri = flow.step1_get_authorize_url()
            logging.error("---------------- auth URI ------------")
            logging.error(str(auth_uri))

            self.redirect(str(auth_uri))

            #response: ?code=4/VLoLevqDuzdbPVHC0HVzE6N0jRGh58hpo9m2JRgNU2M#

            # google_credentials.get_credentials('4/VLoLevqDuzdbPVHC0HVzE6N0jRGh58hpo9m2JRgNU2M#', 'hello')

class TestAPIResponse(MainHandler):
    def get(self):
        auth_code = self.request.get("code")

        logging.error("----------- auth_code ------------")
        logging.error(auth_code)

        import google_credentials

        from oauth2client import client
        flow = client.flow_from_clientsecrets(
        google_credentials.CLIENTSECRETS_LOCATION,
        scope=google_credentials.SCOPES,
        redirect_uri=google_credentials.REDIRECT_URI)

        gmail_oauth = model.GmailAuth.query().get()
        if not gmail_oauth:
            credentials = flow.step2_exchange(auth_code)
            gmail_oauth = model.GmailAuth(auth_code=auth_code, credentials=credentials)
            gmail_oauth.put()
        else:
            credentials = gmail_oauth.credentials


        import httplib2
        http_auth = credentials.authorize(httplib2.Http())

        from apiclient.discovery import build

        gmail_service = build('gmail', 'v1', http=http_auth)

        try:
            response = gmail_service.users().messages().list(userId='emile.app@gmail.com', q='in:inbox newer_than:2d category:primary', maxResults=3).execute()
            messages = response['messages']
            logging.error("----------- MESSAGES -----------")
            logging.error(messages)
            a_message = messages[0]
            logging.error("-------- a message --------")
            logging.error(a_message["id"])# 14fad054971a3760
            # json_message = gmail_service.users().messages().get(userId='emile.app@gmail.com', id='14fad054971a3760', format='full', metadataHeaders=None).execute()
            # json_message = gmail_service.users().messages().get(userId='emile.app@gmail.com', id=a_message["id"], format='full', metadataHeaders=None).execute()
            message_string = "..."

            for message in messages:
                json_message = gmail_service.users().messages().get(userId='emile.app@gmail.com', id=message["id"], format='minimal', metadataHeaders=None).execute()
                try:
                    json_message = json.dumps(json_message)
                    json_message = json.loads(json_message)
                    logging.error(json_message)
                    # logging.error(json_message["snippet"])
                    message_string += "%s/n" % json_message["snippet"]
                except Exception as ex:
                    logging.error("something's up with the string formatting/json")
                    template = "An exception of type {0} occured. Arguments:\n{1!r}"
                    error_message = template.format(type(ex).__name__, ex.args)
                    logging.error(error_message)
            # logging.error(json_message)
            
            self.response.out.write(message_string)

        except:
            logging.error("---- something went wrong with the gmail message query")

app = webapp2.WSGIApplication([
    ('/', Home),
    ('/project/(\w+)', Project),
    ('/save_project', SaveProject),
    ('/save_response/(\w+)', SaveResponse),

    ('/testapi', TestAPI),
    ('/testapiresponse', TestAPIResponse),

    ('/admin', Admin),
    ('/admin/blog', AdminBlog),
    ('/admin/approve_blog', AdminApproveBlog),
    ('/admin/post/edit/(\w+)', EditPost),
    ('/admin/upload_media', UploadMedia),
    ('/admin/fetch_media', FetchMedia),
    ('/admin/quote', AdminQuote),

], debug=False)
