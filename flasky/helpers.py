from Crypto.Cipher import AES
from Crypto import Random
import codecs
from flasky import app

enc_key_activation = b'PnueFan8Xs]xeq6P'
enc_key_pwreset = b'Rof)012Sv]b#0q'
iv = Random.new().read(AES.block_size)


def create_activation_link(id):
    cipher = AES.new(enc_key_activation, AES.MODE_CFB, iv)
    binary = iv + cipher.encrypt(id.encode("utf-8"))
    return binary.hex()


def decrypt_activation_link(link):
    cipher = AES.new(enc_key_activation, AES.MODE_CFB, iv)
    decode_hex = codecs.getdecoder("hex_codec")
    string = decode_hex(link)[0]

    binary = cipher.decrypt(string)[len(iv):]

    try:
        to_return = str(binary, 'utf-8')
    except:
        to_return = -1
    return to_return


def create_pwreset_link(id):
    cipher = AES.new(enc_key_activation, AES.MODE_CFB, iv)
    binary = iv + cipher.encrypt(id.encode("utf-8"))
    return binary.hex()


def decrypt_pwreset_link(link):
    cipher = AES.new(enc_key_activation, AES.MODE_CFB, iv)
    decode_hex = codecs.getdecoder("hex_codec")
    string = decode_hex(link)[0]

    binary = cipher.decrypt(string)[len(iv):]

    try:
        to_return = str(binary, 'utf-8')
    except:
        to_return = -1
    return to_return


def activation_mail_body(username, base_url, activation_link):
    return '''
    Hello %s!
    <br>
    Here is the link to activate your account on Flasky-App:
    <a href="%sactivate?link=%s"> Click to activate</a>
    <br>
    We can't wait to see you among us!
    <br>
    Have fun!
    ''' % (username, base_url, activation_link)


def pwreset_mail_body(username, base_url, reset_link):
    return '''
    Hello %s!
    <br>
    You requested a password change for your account on Flasky-App:
    <a href="%srecover/%s"> Click to activate</a>
    <br>
    We can't wait to see you among us!
    <br>
    Have fun!
    ''' % (username, base_url, reset_link)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
