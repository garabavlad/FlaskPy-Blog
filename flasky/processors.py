from flasky import app
import random

#PROCESSORS
@app.context_processor
def utility_processor():
    def article_body(string):
        i1 = string.find('<p>')
        i2 = string.find('</p>')
        output = ''

        if(i1 != -1 and i2 != -1):
            output += string[int(i1)+3:int(i2)]

        if len(output) > 300:
            output = output[0:300] + '...'

        return output
    return dict(article_body=article_body)

@app.context_processor
def utility_processor():
    def article_list_color_gen():
        return '#' + str(random.randint(100000,999999)) + '14'
    return dict(article_list_color_gen=article_list_color_gen)