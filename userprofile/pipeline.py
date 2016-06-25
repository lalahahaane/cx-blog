from django.shortcuts import redirect
from django.conf import settings
from social.pipeline.partial import partial
from django.core.files.base import ContentFile
from requests import request, ConnectionError

@partial
def require_email(strategy, details, user=None, is_new=False, *args, **kwargs):
    if kwargs.get('ajax') or user and user.email:
        return
    elif is_new and not details.get('email'):
        email = strategy.request_data().get('email')
        if email:
            details['email'] = email
        else:
            return redirect('require_email')





def save_profile(backend, user, response, is_new,  *args, **kwargs):
    '''
    Get the user avatar (and any other details you're interested in)
    and save them to the userprofile
    '''
    if backend.name == 'google-plus':
        if response.get('picture') and response['picture'].get('url'):
            url = response['picture'].get('url')
            prof = user.userprofile
            if prof.picture:
                # if existing avatar stick with it rather than google syncing
                pass
            else:
                try:
                    response = request('GET', url)
                    response.raise_for_status()
                except ConnectionError:
                    pass
                else:
                    # No avatar so sync it with the google one.
                    # Passing '' for name will invoke my upload_to function
                    # saving by username (you prob want to change this!)
                    prof.username = response.get('username')
                    prof.email = response.get('email')
                    prof.password = response.get('sub')
                    prof.picture.save('{0}_{1}.jpg'.format(settings.MEDIA_ROOT, prof.username),
                                 ContentFile(response.content),
                                 save=False
                                 )
                    prof.save()
    elif backend.name == 'facebook':   # and is_new:
        prof = user.userprofile
        if prof.picture:
            pass
        else:
            url = 'http://graph.facebook.com/{0}/picture'.format(response['id'])

            try:
                response = request('GET', url, params={'type': 'large'})
                response.raise_for_status()
            except ConnectionError:
                pass
            else:
                prof.picture.save(u'',
                                 ContentFile(response.content),
                                 save=False
                                 )
                prof.save()
