import requests
import re
import subprocess
import os
import folder_paths
import shutil

cwd = os.getcwd ()
# TEXT = '((masterpiece:1.4, best quality)),((masterpiece, best quality)),cute little girl,loli,feel happy,graduate,Cherry blossom on both sides of the road'
LINEFEED = '\n\n'

def init():
    tweak_path = cwd + os.sep.join('\\web\\extensions\\tweak_keywords_CN2EN'.split("\\"))
    tweak_path_bk = cwd + os.sep.join('\\custom_nodes\\comfy_translation_node\\tweak_keywords_CN2EN'.split("\\"))

    if not os.path.isdir(tweak_path):
        print("----------start-------------未发现tweak_keywords_CN2EN文件夹，正在处理。。。")
        os.rename(tweak_path_bk, cwd + os.sep.join('\\web\\extensions\\tweak_keywords_CN2EN'.split("\\")))
        print("-----------end------------tweak_keywords_CN2EN文件夹处理完成--------------")

def symbol_fun(str):
    # 处理中文符号
    symbol = {ord(f):ord(t) for f,t in zip(
        u'｛｝：，。！？【】（）％＃＠＆１２３４５６７８９０',
        u'{}:，.!?[]()%#@&1234567890')}
    str = str.translate(symbol)
    return str
     
def gg_trans(trans_str,args):
    trans_str = trans_str.replace(';', '#')
    if args['language'] == 'EN':
        from_lang = 'ZH-CN'
        to_lang = 'EN'
    else:
        from_lang = 'EN'
        to_lang = 'ZH-CN'
    # 导入Translator类
    from translate import Translator
    try:
        # 创建一个Translator对象，指定源语言和目标语言
        translator = Translator(from_lang=from_lang, to_lang=to_lang)
        # 调用translate方法来翻译文本
        translation = (translator.translate(trans_str)).replace('#', ';')
        if args['log'] == 'OPEN':
            print('\n调用谷歌请注意查看控制台信息！！！因为谷歌api不稳定，经常调用失败，如果控制台出现500 CHARS时请更换有道api。。。',translator,)
        return translation
    except Exception as e:
        # 打印异常信息
        print("Error:", e)
        return trans_str
    finally:
        # 释放资源
        translator = None

def yd_trans(trans_str,args):
    # 定义有道翻译的网页版地址
    YOUDAO_URL = 'http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule&smartresult=ugc&sessionFrom=null'

    if args['language'] == 'EN':
        from_lang = 'ZH-CN'
        to_lang = 'EN'
    else:
        from_lang = 'EN'
        to_lang = 'ZH-CN'
        
    # 构造请求参数
    data = {
        'i': trans_str,
        'from': from_lang,
        'to': to_lang,
        'doctype': 'json',
        'version': '2.1',
        'keyfrom': 'fanyi.web',
        'action': 'FY_BY_REALTIME',
        'typoResult': 'false'
    }

    try:
        # 发送请求并获取响应
        response = requests.post(YOUDAO_URL, data=data)
        if response.status_code == 200:
            result = response.json()
            # 打印翻译结果
            result_text = ''
            tgt_list = result['translateResult'][0]
            # 循环获取tgt
            # loop gain TGT
            for i in tgt_list:
                result_text = result_text+i['tgt']
            return result_text
        else:
            if args['log'] == 'OPEN':
                print(LINEFEED+"调用翻译失败，未进行翻译，原数据返回（call translation failure, not for translation, the original data back）>>>>>>：",trans_str,LINEFEED)
            return trans_str
    except Exception as e:
        # 打印异常信息
        print("Error:", e)
        return trans_str
    finally:
        # 释放资源
        response = None

def trans(args):
    text = args['text']
    if not args or not text:
        return ''
    if args['language'] == 'AUTO':
        return text
    text = 'start' + symbol_fun(text) + 'end'

    if args['language'] == 'EN':
        # 匹配非中文字符的范围
        no_chinese_re = re.compile(r'[\u4e00-\u9fff]+')
        # 使用replace或sub方法，将匹配到的非中文字符替换为,
        no_chinese_re = no_chinese_re.sub('/', text)

        # 匹配中文字符的范围
        chinese_re = re.compile(r'[^\u4e00-\u9fff]+')
        # 使用replace或sub方法，将匹配到的中文字符替换为,
        chinese_re = chinese_re.sub(',', text)

        chinese_re_arr = chinese_re.split(",")
        no_chinese_re_arr = no_chinese_re.split("/")
        del chinese_re_arr[0]
        del chinese_re_arr[-1]
        text_data = no_chinese_re_arr
        trans_str = ';'.join(chinese_re_arr)
        # 调用翻译
        if args['transAPI'] == 'GOOGLE':
            result_text = gg_trans(trans_str,args)
        elif args['transAPI'] == 'YOUDAO':
            result_text = yd_trans(trans_str,args)
        
        # 用逗号作为分隔符，拆分字符串到数组里
        result_text_arr = result_text.split(";")

        text_new = ''
        for i,item in enumerate(text_data):
                if (i<len(result_text_arr)):
                    text_new = text_new + item + result_text_arr[i].strip()
                else:
                    text_new = text_new + item
        text_new = re.sub(r"^(start)|(end)$", "", text_new.replace('，',','))
        if args['log'] == 'OPEN':
            print(LINEFEED,'调用'+args['transAPI']+'转换后的内容如下（The converted contents are as follows）↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓',LINEFEED,text_new,LINEFEED,'↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑',LINEFEED)
        return text_new
    elif args['language'] == 'CN':
        text = re.sub(r"^(start)|(end)$", "", text.replace('，',','))
        # 调用翻译
        if args['transAPI'] == 'GOOGLE':
            result_text = gg_trans(text,args)
        elif args['transAPI'] == 'YOUDAO':
            result_text = yd_trans(text,args)
        if args['log'] == 'OPEN':
            print(LINEFEED,'调用'+args['transAPI']+'转换后的内容如下（The converted contents are as follows）↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓',LINEFEED,result_text,LINEFEED,'↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑',LINEFEED)
        return result_text
    
    

# trans({"text": TEXT, "language": 'EN', "log": "OPEN", "transAPI":"YOUDAO"})

inputTypes = {
        "required": {
            "text": ("STRING",
                {
                    "multiline": True
                }),
            # "clip": ("CLIP", ),
            "language": (['AUTO','CN','EN'], ),
            "transAPI": (['YOUDAO','GOOGLE'], ),
            "log": (['CLOSE','OPEN'], ),
        }
    }
try:
    embeddingsFile = folder_paths.get_filename_list("embeddings")
    embeddingsList = ['none']
    embeddingsList = embeddingsList + embeddingsFile
    emb = {
        "embeddings": (embeddingsList, ),
        "embeddingsStrength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.01}),
    }
    inputTypes['required'].update(emb)
except:
    emb = {}

class CN2ENTRANS:
    @classmethod
    def INPUT_TYPES(s):
        return inputTypes
    RETURN_TYPES = ("STRING",)
    FUNCTION = "text_trans"
    OUTPUT_NODE = True
    CATEGORY = "xww/trans"

    if len(emb) > 0:
        def text_trans(self, text,language,log,transAPI,embeddings,embeddingsStrength):
            print('embeddingsStrength============',embeddingsStrength)
            text = trans({"text": text, "language": language, "log": log, "transAPI": transAPI})
            if  embeddings == 'none':
                if log == 'OPEN':
                    print('no embeddings----------',text)
                return (text,)
            textEmb = '{} embeddings: {} : {},'
            textEmb = textEmb.format(text, embeddings, format(embeddingsStrength,'.3f'))
            if log == 'OPEN':
                print('add embeddings----------',textEmb)
            return (textEmb,)
    else:
        def text_trans(self, text,language,log,transAPI):
            text = trans({"text": text, "language": language, "log": log, "transAPI": transAPI})
            if log == 'OPEN':
                print('no embeddings----------',text)
            return (text,)

class TWEAKKEYWORDS:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "text": ("STRING", {"forceInput": True}),
        }}

    RETURN_TYPES = ("STRING",)
    FUNCTION = "tweak_keywords"
    OUTPUT_NODE = True

    CATEGORY = "xww/trans"

    def tweak_keywords(self, text):   
        return {"ui": { "text": text }, "result": (text,)}

NODE_CLASS_MAPPINGS = {
    "CLIP Text Encode CN2EN": CN2ENTRANS,
    "Tweak Keywords CN2EN": TWEAKKEYWORDS,
}
init()