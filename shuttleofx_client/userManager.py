from flask import session
import config
import logging


def getUser():
    if 'google_token' in session:
        resp = config.google.get('userinfo')
        if resp.status is not 200:
            logging.error("Bad request Google authentication API : " + str(resp.data))
        else:
            googleUser = resp.data
            user = {'name': googleUser.get('name'), 'picture': googleUser.get('picture'), 'id': googleUser.get('sub')}
            return user
    elif 'github_token' in session:
        resp = config.github.get('?access_token=' + str(session['github_token'][0]))
        if resp.status is not 200:
            logging.error("Bad request Github authentication API : " + str(resp.data))
        else:
            githubUser = resp.data
            if githubUser.get('name') is None:
                name = githubUser.get('login')
            else:
                name = githubUser.get('name')

            user = {'name': name, 'picture': githubUser.get('avatar_url'), 'id': githubUser.get('id')}
            return user
    else:
        return None

def getOAuthProvider():
    if 'google_token' in session:
        return 'google'
    elif 'github_token' in session:
        return 'github'
    else:
        return None
