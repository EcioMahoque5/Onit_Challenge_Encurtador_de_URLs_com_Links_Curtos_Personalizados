from flask import Blueprint, request, make_response, redirect
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import random
import string
from datetime import datetime
from .validator import LoginForm, UserRegistrationForm, ShortenLinkForm, validate_domain
from . import bcrypt, logger
import validators


auth_bp = Blueprint('auth', __name__)
app_bp = Blueprint('api', __name__)

# In-memory storage
users = {}  # {username: {"password": str, "urls": list}}
next_id = 1000
short_links = {}  # {short_link: {"original_url": str, "clicks": int, "owner": str}}


"""Generate a random short link."""
def generate_short_link():    
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))



"""
    Authentication APIs
"""
# Register a new user
@auth_bp.route("/register_user", methods=["POST"])
def register_user():
    try:
        global next_id  
        data = request.get_json()
        form = UserRegistrationForm(data=data, data_store=users)
        
        logger.info(f"register_user request received: {data}")
        
        if form.validate():
            time = datetime.now()
            username = data.get('username')
            password = bcrypt.generate_password_hash(password=data.get('password')).decode('utf-8')

            users[username] = {"password": password, "urls": [], "date_created": time.strftime("%Y-%m-%d %H:%M:%S")}
            
            response_data = {
                "id": next_id,
                "username": username,
                "date_created": time.strftime("%Y-%m-%d %H:%M:%S")
            }

            next_id += 1
            
            logger.info("register_user response: User registered successfully!")
            
            return make_response({
                "success": True,
                "message": "User registered successfully!",
                "data": response_data
            }, 201)
            
        else:
            logger.error({
                "message": "Validations errors",
                "errors": form.errors,
            })
            return make_response({
                "success": False,
                "message": "Validations errors",
                "errors": form.errors
            }, 400)
        
        
    except Exception as e:
        logger.error(e, exc_info=True)
        logger.info(f"error {e} occured on register_user api")
        return make_response({
            "message": "An unexpected error occurred. Please try again later!"
        }, 500)
    
    
# User login
@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        
        logger.info(f"login request {data.get('username')}")
        
        form = LoginForm(data=data)
        
        if form.validate():
            user = users.get(data.get('username'))
            
            if not user or not bcrypt.check_password_hash(user['password'], data.get('password')):
                logger.error(f"login response: Invalid password for user '{data.get('username')}'")
                return make_response({
                    "success": False,
                    "message": "Invalid username or password!"
                }, 401)
                
            access_token = create_access_token(identity=data.get('username'))
            
            logger.info(f"login response: User {data.get('username')} logged in successfully!")
            return make_response({
                "success": True,
                "message": "Login successful!",
                "access_token": access_token
                }, 200)

        
        logger.info("user_login response: {}".format(
            {
                "message": "Validation errors",
                "errors": form.errors
            }
        ))
        
        return make_response({
            "success": False,
            "message": "Validation errors",
            "errors": form.errors
        }, 400)
        
    except Exception as e:
        logger.error(e, exc_info=True)
        logger.info(f"error {e} occured on login api")
        return make_response({
            "message": "An unexpected error occurred. Please try again later!"
        }, 500)
    


"""
    Challenge APIs
"""
# Shorten a URL7
@app_bp.route("/shorten", methods=["POST"])
@jwt_required()
def shorten_url():
    try:
        data = request.get_json()
        
        logger.info(f"shorten_url request {data}")
        
        form = ShortenLinkForm(data=data)
        
        if form.validate():
            original_url = data.get("originalUrl")
            custom_short_link = data.get("customShortLink")
            username = get_jwt_identity()
            
             # Check for custom short link conflicts
            if custom_short_link:
                if custom_short_link in short_links:
                    logger.info(f"shorten_url response: Custom short link is already taken!")
                    return make_response({
                        "success": False, 
                        "message": "Custom short link is already taken!"
                    }, 409)
                
                short_link = custom_short_link
                
            else:
                # Generate a unique short link
                short_link = generate_short_link()
                while short_link in short_links:
                    short_link = generate_short_link()
                    
            if not validators.url(original_url):
                logger.info("shorten_url response: {}".format(
                    {
                        "message": "Validation errors",
                         "errors": { "originalUrl": ["Invalid URL!"] }
                    }
                ))
                return make_response({
                    "success": False,
                    "message": "Validation errors",
                    "errors": {
                        "originalUrl": ["Invalid URL!"]
                    }
                })
                    
            if data.get('domain'):
                domain = data.get('domain')
                
                domain_valid = validate_domain(domain)
                
                if not domain_valid:
                    logger.info("shorten_url response: {}".format(
                        {
                            "message": "Validation errors",
                            "errors": { "domain": ["Invalid domain!"] }
                        }
                    ))
                    return make_response({
                        "success": False,
                        "message": "Validation errors",
                        "errors": {
                            "domain": ["Invalid domain!"]
                        }
                    })
            else:
                domain = ''

            # Save the URL and owner in memory
            short_links[short_link] = {"original_url": original_url, "domain": domain, "clicks": 0, "owner": username}
            users[username]["urls"].append(short_link)

            logger.info("shorten_url response: {}".format({
                "success": True, 
                "short_Link": short_link, 
                "original_url": original_url,
                "domain": domain
            }))
            
            return make_response({
                "success": True, 
                "short_Link": short_link, 
                "original_url": original_url,
                "domain": domain
            }, 201)

        else:
            logger.info("shorten_url response: {}".format(
                {
                    "message": "Validation errors",
                    "errors": form.errors
                }
            ))
            
            return make_response({
                "success": False,
                "message": "Validation errors",
                "errors": form.errors
            }, 400)
            
    except Exception as e:
        logger.error(e, exc_info=True)
        logger.info(f"Error {e} occurred on shorten_url api")
        return make_response({
            "message": "An unexpected error occurred. Please try again later!"
        }, 500) 


"""Redirect to the original URL."""
@app_bp.route("/shorten/<shortLink>", methods=["GET"])
def redirect_url(shortLink):
    try:
        logger.info("redirect_url request received")
        entry = short_links.get(shortLink)
        
        if not entry:
            logger.info(f"redirect_url response: Short link '{shortLink}' not found!")
            return make_response({
                "success": False, 
                "message": "Short link not found!"
            }, 404)

        entry["clicks"] += 1
        return redirect(entry["original_url"], code=302)
    
    except Exception as e:
        logger.error(e, exc_info=True)
        logger.info(f"error {e} occured on redirect_url api")
        return make_response({
            "message": "An unexpected error occurred. Please try again later!"
        }, 500)
    

"""Get statistics for a short link."""
@app_bp.route("/stats/<shortLink>", methods=["GET"])
@jwt_required()
def get_stats(shortLink):
    try:
        logger.info(f"get_stats request received")
        username = get_jwt_identity()
        entry = short_links.get(shortLink)

        if not entry:
            logger.info(f"get_stats response: Short link '{shortLink}' not found!")
            return make_response({
                "success": False, 
                "message": "Short link not found!"
            }, 404)

        if entry["owner"] != username:
            logger.info(f"redirect_url response: User '{username}' is not authorized to view the statistics!")
            return make_response({
                "success": False, 
                "message": "You are not authorized to view these statistics!"
            }, 403)
            

        return make_response({
            "success": True, 
            "original_url": entry["original_url"],
            "short_link": shortLink, 
            "domain": entry["domain"],
            "clicks": entry["clicks"]
        }, 200)
    
    except Exception as e:
        logger.error(e, exc_info=True)
        logger.info(f"error {e} occured on get_stats api")
        return make_response({
            "message": "An unexpected error occurred. Please try again later!"
        }, 500)
    

"""Get all short links created by the authenticated user."""
@app_bp.route("/user/links", methods=["GET"])
@jwt_required()
def user_links():
    try:
        logger.info("user_links request received")
        username = get_jwt_identity()
        user_urls = users[username]["urls"]
        
        if not user_urls:
            logger.info(f"user_links response: User '{username}' didn't create a short link yet!")
            return make_response({
                "success": False,
                "message": "You didn't create a short link yet!"
            }, 404)

        data = [{
            "originalUrl": short_links[link]["original_url"], 
            "shortLink": link, 
            "domain": short_links[link]["domain"],
            "clicks": short_links[link]["clicks"],
            "owner": short_links[link]["owner"]
            } for link in user_urls]

        return make_response({
            "success": True, 
            "urls": data
        }, 200)
        
    except Exception as e:
        logger.error(e, exc_info=True)
        logger.info(f"error {e} occured on user_links api")
        return make_response({
            "message": "An unexpected error occurred. Please try again later!"
        }, 500)
    


