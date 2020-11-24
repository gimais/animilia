from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _

class MyUnicodeUsernameValidator(UnicodeUsernameValidator):
    regex = r'^[\w-]+$'
    message = 'ნიკი შეიძლება შეიცავდეს მხოლოდ ასოებს, ციფრებსა და /-/_ სიმბოლოებს.'

ERRORS = {
    'unique': _("A user with that username already exists."),
    'unique_email' : "ეს Email უკვე დარეგისტრირებულია. ( <a href='/account/password_reset/'>პაროლის გახსენება</a> )",
    'empty_fields': "ცარიელი ველები უნდა შეავსოთ.",
    'blacklist': "ასეთი ნიკი მიუღებელია. სხვა სცადეთ.",
}

blacklist = ['.htaccess', '.htpasswd', '.well-known','ad', 'add','admin', 'administration',
             'administrator','ads', 'ads.txt', 'advertise', 'advertising', 'analytics',
             'apps','assets','authentication', 'authorize', 'backup',
             'blog', 'blogs', 'board','business', 'buy', 'calendar', 'categories',
             'category', 'change', 'chart', 'chat', 'checkout',
             'clear', 'client', 'close', 'cloud','comment', 'comments', 'community',
             'compare', 'compose', 'config', 'connect', 'contact', 'contest', 'cookies', 'copy', 'copyright',
             'count','cpanel', 'create', 'css','customers', 'customize', 'dashboard',
             'deals', 'debug', 'delete', 'dev','developer', 'developers','disconnect',
             'discuss', 'documentation','domain', 'download','downloads', 'edit', 'editor',
             'email', 'favicon.ico', 'features', 'feed', 'feedback',
             'feeds', 'file','files', 'filter', 'follow', 'follower', 'followers', 'following', 'fonts', 'forgot',
             'forgot-password','forgotpassword', 'form', 'forms', 'forum', 'forums', 'get','group', 'groups',
             'guest',  'head', 'header', 'help', 'hide', 'home', 'host', 'hosting', 'hostmaster',
             'htpasswd', 'http', 'httpd', 'https','humans.txt', 'icons', 'images', 'img', 'import',
             'info','js','json', 'like','limit', 'live', 'load','local','localdomain', 'localhost',
             'lock', 'login', 'logout', 'lost-password','mail','map', 'message', 'messages', 'metrics',
             'moderator', 'no-reply', 'nobody', 'noc', 'none', 'noreply', 'notification', 'notifications',
             'offers', 'online', 'openid', 'order', 'orders', 'overview', 'owner', 'page', 'pages','passwd', 'password',
             'pay', 'payment', 'payments', 'photo', 'photos', 'plans', 'plugins','policies', 'policy', 'pop', 'pop3',
             'popular', 'portal', 'portfolio', 'post', 'postfix', 'postmaster','poweruser', 'privacy', 'privacy-policy',
             'private','product', 'production','profile', 'profiles', 'public', 'register',
             'registration', 'remove','replies', 'reply', 'report', 'request', 'request-password',
             'reset', 'reset-password', 'response', 'return','returns', 'review', 'reviews', 'robots.txt', 'root', 'rootuser',
             'rss','rules', 'sales', 'save', 'script', 'search', 'secure', 'security', 'select', 'services', 'session',
             'sessions', 'settings', 'setup', 'shop', 'signin', 'signup', 'site', 'sitemap', 'sites',
             'stat', 'static', 'statistics', 'stats', 'status', 'store', 'style', 'styles',
             'stylesheet', 'stylesheets', 'sudo', 'super', 'superuser', 'support',
             'sysadmin', 'system', 'tablet', 'team','terms', 'terms-of-use','true', 'undefined',
             'update', 'upgrade', 'user', 'webmaster', 'website','www','yourname', 'yourusername','god','zlib','anal', 'anus',
             'bastard', 'bitch','biatch', 'blowjob', 'blow job', 'clitoris', 'cock', 'dick', 'dildo', 'fuck',
             'f u c k', 'Goddamn','God damn','nigger', 'nigga', 'omg', 'penis','pussy', 'sex','shit', 's hit', 'sh1t',
             'spunk', 'tit', 'vagina', 'wtf','yleo','ylexar','muteli','dedamovtyan','shenidedasheveci',
             'shenidedamovtyan','yle','sheveci','ანიმილია']