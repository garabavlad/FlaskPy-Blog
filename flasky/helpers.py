from Crypto.Cipher import AES
from Crypto import Random
import codecs

enc_key = b'PnueFan8Xs]xeq6P'
iv = Random.new().read(AES.block_size)
cipher = AES.new(enc_key, AES.MODE_CFB, iv)

def create_activation_link(id):

    binary = iv + cipher.encrypt(id.encode("utf-8"))
    return binary.hex()

def decrypt_activation_link(link):

    decode_hex = codecs.getdecoder("hex_codec")
    string = decode_hex(link)[0]

    binary = cipher.decrypt(string)[len(iv):]

    try:
        to_return = str(binary, 'utf-8')
    except:
        to_return = -1

    return to_return

def activation_mail_body(username, base_url, activation_link ):
    return '''
    Hello %s!
    <br>
    Here is the link to activate your account on Flasky-App:
    <a href="%sactivate?link=%s"> Click to activate</a>
    <br>
    We can't wait to see you among us!
    <br>
    Have fun!
    ''' % (username, base_url,activation_link)
