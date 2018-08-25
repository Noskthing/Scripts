import keyring
import sys
from hashlib import pbkdf2_hmac
import os
import sqlite3
from urlparse import urlparse
from Crypto.Cipher import AES

# Constant for Symmetic key derivation.
CHROME_COOKIES_ENCRYPTION_ITERATIONS = 1003

# Salt for Symmetric key derivation.
CHROME_COOKIES_ENCRYPTION_SALT       = b'saltysalt'

# Key size required for 128 bit AES. So dklen = 128/8
CHROME_COOKIES_ENCRYPTION_DKLEN      = 16

def get_password_from_keychain(isChrome=True):
    """Try to read password from keychain

    Args:
        isChrome will help judge what name is
        if it' true name is Chrome else Chromium

    Return:
        password storage in keychain
    """
    browser = 'Chrome' if isChrome else 'Chromium'
    return keyring.get_password(browser + ' Safe Storage', browser)

def get_cookies_filepath(isChrome=True):
    """Get path to store cookies
    """
    return '~/Library/Application Support/Google/Chrome/Default/Cookies'\
     if isChrome else '~/Library/Application Support/Chromium/Default/Cookies'

def get_cookies_erncrypt_key(isChrome=True):
    """Generates a newly allocated SymmetricKey object based on the password found
    in the Keychain.  The generated key is for AES encryption.

    Return:
       SymmetricKey for AES 
    """
    return pbkdf2_hmac(hash_name='sha1',
                       password=get_password_from_keychain(isChrome).encode('utf8'),
                       salt=CHROME_COOKIES_ENCRYPTION_SALT,
                       iterations=CHROME_COOKIES_ENCRYPTION_ITERATIONS,
                       dklen=CHROME_COOKIES_ENCRYPTION_DKLEN)

def generate_host_keys(hostname):
    """Yield Chrome/Chromium keys for `hostname`, from least to most specific.

    Given a hostname like foo.example.com, this yields the key sequence:

    example.com
    .example.com
    foo.example.com
    .foo.example.com

    """
    parsed_url = urlparse(hostname)
    if parsed_url.scheme:
        domain = parsed_url.netloc
    else:
        raise ValueError('You must include a scheme with your hostname')
    labels = domain.split('.')
    for i in range(2, len(labels) + 1):
        domain = '.'.join(labels[-i:])
        yield domain
        yield '.' + domain

def chrome_decrypt(encrypt_string, isChrome=True):
    """Decrypt Chrome/Chromium's encrypted cookies

    Args:
        encrypt_string: Encrypted cookie from Chrome/Chromium's cookie file

    Returns:
        Decrypted value of encrypted_value
    """

    encrypt_string = encrypt_string[3:]

    cipher = AES.new(get_cookies_erncrypt_key(isChrome), AES.MODE_CBC, IV=b' ' * 16)
    decrypted_string = cipher.decrypt(encrypt_string)

    return decrypted_string.rstrip().decode('utf8')
    
def fetch_chrome_cookies(hostname, isChrome=True):
    """Retrieve cookies from Chrome/Chromium on macOS.

    Args:
        hostname: Domain from which to retrieve cookies, starting with http(s)

    Returns:
        Dictionary of cookie values for UR
    """
    if not (sys.platform == 'darwin'):
        raise ValueError('This script only works on macOS')

    cookie_file_path = str(os.path.expanduser(get_cookies_filepath()))

    with sqlite3.connect(cookie_file_path) as conn:
        secure_column_name = 'is_secure'
        for column_names in conn.execute('PRAGMA table_info(cookies)'):
            if column_names[1] == 'secure':
                secure_column_name = 'secure'
                break
            elif column_names[1] == 'is_secure':
                break
        
        sql_str = ('select host_key, path, ' + secure_column_name +
                   ', expires_utc, name, value, encrypted_value '
                   'from cookies where host_key like ?')
        cookies = dict()

        for host_key in generate_host_keys(hostname):
            for hk, path, is_secure, expires_utc, cookie_key, val, enc_val \
                in conn.execute(sql_str, (host_key,)):
                if val or (enc_val[:3] not in (b'v10', b'v11')):
                    pass
                else:
                    val = chrome_decrypt(enc_val, isChrome)
                cookies[cookie_key] = val

    return cookies
            

if __name__ == '__main__':

    url = 'http://www.baidu.com'

    cookies = fetch_chrome_cookies(url)   
    for key in cookies:
        print key + ' = ' + cookies[key]