from django.contrib.auth.validators import ASCIIUsernameValidator
from django.core import validators
from django.utils.translation import gettext_lazy as _


class MyASCIIUsernameValidator(ASCIIUsernameValidator):
    regex = r'^[\w-]+$'


class OnlyDigitUsernameValidator(validators.RegexValidator):
    regex = r'(?!^\d+$)^.+$'
    message = "ნიკი არ უნდა შეიცავდეს მხოლოდ ციფრებს"


class WebDomainValidator(validators.RegexValidator):

    def __init__(self, domain, name):
        regex = r'^((?:https?:\/\/)?(?:[^.]+\.)?)({domain}\.com\/)(.+)$'.format(
            domain=WebDomainValidator.process_regex(domain)
        )
        message = "გთხოვთ, შეიყვანოთ მხოლოდ {}-ის პროფაილის ლინკი".format(name)
        super().__init__(regex=regex, message=message)

    code = "invalid_url"

    @classmethod
    def process_regex(cls, domain):
        if isinstance(domain, str):
            return domain
        return "({})".format('|'.join(domain))


ERRORS = {
    'unique': _("A user with that username already exists."),
    'unique_email': "ეს Email უკვე დარეგისტრირებულია. ( <a href='/account/password_reset/'>პაროლის გახსენება</a> )",
    'empty_fields': "ცარიელი ველები უნდა შეავსოთ.",
    'blacklist': "ასეთი ნიკი მიუღებელია. სხვა სცადეთ.",
}

blacklist = ['.htaccess', '.htpasswd', '.well-known', 'ad', 'add', 'admin', 'administration', 'administrator', 'ads',
             'ads.txt', 'advertise', 'advertising', 'apps', 'assets', 'authentication', 'authorize', 'board',
             'chart', 'chat', 'checkout', 'clear', 'client', 'close', 'cloud', 'comment', 'comments', 'community',
             'compare', 'compose', 'config', 'connect', 'contact', 'contest', 'cookies', 'copy', 'copyright',
             'count', 'cpanel', 'create', 'css', 'customers', 'customize', 'dashboard', 'deals', 'debug', 'delete',
             'dev', 'developer', 'developers', 'disconnect', 'discuss', 'documentation', 'domain', 'download',
             'downloads', 'edit', 'editor', 'email', 'favicon.ico', 'features', 'feed', 'feedback', 'feeds', 'file',
             'files', 'filter', 'fonts', 'forgot', 'forgot-password', 'forgotpassword', 'form', 'forms', 'forum',
             'get', 'group', 'groups', 'header', 'help', 'hide', 'home', 'host', 'hosting', 'business', 'buy',
             'hostmaster', 'htpasswd', 'http', 'httpd', 'https', 'humans.txt', 'icons', 'images', 'img', 'import',
             'info', 'js', 'json', 'like', 'limit', 'live', 'load', 'local', 'localdomain', 'localhost', 'lock',
             'login', 'logout', 'lost-password', 'mail', 'map', 'message', 'messages', 'metrics', 'moderator',
             'no-reply', 'nobody', 'noc', 'none', 'noreply', 'notification', 'notifications', 'offers', 'online',
             'openid', 'order', 'orders', 'overview', 'owner', 'page', 'pages', 'passwd', 'password', 'pay', 'payment',
             'payments', 'photo', 'photos', 'plugins', 'policies', 'policy', 'post', 'privacy', 'privacy-policy',
             'private', 'product', 'production', 'profile', 'profiles', 'public', 'register', 'registration',
             'remove', 'replies', 'reply', 'report', 'request', 'request-password', 'reset', 'reset-password',
             'response', 'return', 'returns', 'robots.txt', 'root', 'rootuser', 'save', 'script', 'search', 'secure',
             'security', 'session', 'sessions', 'settings', 'setup', 'shop', 'signin', 'signup', 'site', 'sitemap',
             'sites', 'stat', 'static', 'statistics', 'stats', 'status', 'store', 'style', 'styles', 'stylesheet',
             'stylesheets', 'sudo', 'super', 'superuser', 'support', 'sysadmin', 'system', 'tablet', 'team', 'terms',
             'terms-of-use', 'true', 'undefined', 'update', 'upgrade', 'user', 'webmaster', 'website', 'www',
             'yourname', 'yourusername', 'god', "g o d", 'calendar', 'categories', 'category', 'change', 'zlib', 'anal',
             'bastard', 'bitch', 'biatch', 'blowjob', 'blow job', 'clitoris', 'cock', 'dick', 'dildo', 'fuck',
             'f u c k', 'Goddamn', 'God damn', 'nigger', 'nigga', 'omg', 'penis', 'pussy', 'sex', 'shit', 's hit',
             'sh1t', 'spunk', 'tit', 'vagina', 'wtf', 'yleo', 'ylexar', 'muteli', 'dedamovtyan', 'shenidedasheveci',
             'shenidedamovtyan', 'yle', 'sheveci', 'ანიმილია', "აპოლონი", 'აპოლონ', 'დედა მოვტყან', 'anus',
             "დედა შევეცი"]
