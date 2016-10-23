#/usr/bin/python
import requests,re,json,time,os,os.path
import traceback  
#模拟知乎登陆，主要是获取验证码登陆
_zhihu_url='https://www.zhihu.com'
_login_url=_zhihu_url+'/login/email'
_captcha_url=_zhihu_url+'/captcha.gif?r='
_captcha_url_end="&type=login";
header_data={'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding':'gzip, deflate, sdch, br',
    'Accept-Language':'zh-CN,zh;q=0.8',
    'Connection':'keep-alive',
    'Cache-Control':'max-age=0'
    ,'Host':'www.zhihu.com'
    ,'Upgrade-Insecure-Requests':'1'
    ,'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'

    }


class ZhiHu():

    _session=None
    #email=None,
    #password=None,
    #xsrf=None
    favor_data=100
    #question_url='https://www.zhihu.com/question/32120582'
    #path_for=None
    def __init__(self):
        self.do_first()
    def get_captcha(self):
        return _captcha_url+str(int(time.time()*1000))+_captcha_url_end
    def save_captcha(self,url):
        global _session
        r=_session.get(url,headers=header_data,verify=True)
        with open("code.gif",'wb') as f:
            f.write(r.content)

    def input_data(self):
        global email
        global password
        global question_url
        self.email=input('请输入邮箱:')
        self.password=input('请输入密码:')
        self.save_captcha(self.get_captcha())
        self.captcha=input('请输入已下载的验证码:')

      
    def login(self):
        global _session
        global header_data
        global xsrf
        r=_session.get('https://www.zhihu.com',headers=header_data,verify=True)
        self.xsrf=re.findall('name="_xsrf" value="([\S\s]*?)"',r.text)[0]
        #print(r.status_code)
        #print(self.xsrf)
        self.input_data()
        
        
        login_data = {' _xsrf':self.xsrf,'email':self.email,'password':self.password,'rememberme':'true'
        ,'captcha':self.captcha}
        r=_session.post(_login_url,data=login_data,headers=header_data,verify=True)
        j=r.json()
        c=int(j['r'])
        if c==0:
            print('sign in successful')
            
            self.save_cookies()
            os.remove("code.gif")
            
        
        else:
            print('登陆出现问题。。。。')
        
    import  pickle,json
    def save_cookies(self):
        global _session,path_for
        with open('./'+"cookiefile",'w')as f:
            json.dump(_session.cookies.get_dict(),f)
            #_session.cookies.save()

    def read_cookies(self):
        global _session,path_for
        #_session.cookies.load()
        #_session.headers.update(header_data)
        with open('./'+'cookiefile')as f:
            cookie=json.load(f)
            _session.cookies.update(cookie)
 
    def get_text(self,url,answers=15):
        global _session
        global favor_data
        r=_session.get(url,headers=header_data,verify=True)
        pat=re.compile('"count">[\s]*?(.*?)</span>')
       
        _list=re.findall(pat,r.text)
        #print(_list);
        #favor_list=[int(k) for k in _list]
        favor_list=[]
        for i in _list:
            if 'K' in i:
                #print('k in'+i)
                i.replace('K','000')
                favor_list.append(int(1))
            else:
                #print(i)
                favor_list.append(int(i))
                
        favor_list.sort(reverse=True)
        if len(favor_list)>=answers:
            favor_data=favor_list[answers-1]
        else:
            favor_data=0
        self.save_text(r)

    def get_img(self,url):
        global  _session
        r=_session.get(url,headers=header_data,verify=True).text
        item_pattern=re.compile('<div tabindex="-1" class="zm-item-answer  zm-item-expanded"([\S\s]*?)class="meta-item zu-autohide js-noHelp">')
        img_pattern=re.compile('<img[\s\S]*? src="([\s\S]*?)"')
        pattern_title=re.compile('<span class="zm-editable-content">([\s\S]*?)</span>')
        #author_pattern=re.compile('<a class="author-link"[\s\S]*?href="([\S\s]*?)"')
        author_pattern=re.compile('<a class="author-link"[\s\S]*?>([\S\s]*?)</a>')
        items=re.findall(item_pattern,r)
        title=re.findall(pattern_title,r)
        authors=[]
        img_list=[]
        i=0
        try :
            #print('items   len---->'+str(len(items)))
            for item in items:

                i+=1
                authors.append(re.findall(author_pattern,item))
 
                img_list.append(re.findall(img_pattern,item))
                
               
        except :
            print('查找出了一点问题')
            traceback.print_exc()
        try:
            #print(authors)
            j=0
            for author in authors:
                img_urls=img_list[j]
                print(len(img_urls))
                if len(img_urls) == 0:
                    continue
                title_text=title[0];
                author_text=''
                if len(author)>0:
                    author_text=author[0]
                    path=self.createPathIfNotExist(title_text+'\\'+author[0])
                j+=1
                k=0
                for url in img_urls:
                    if 'https' not in url:
                        #print('坏图：'+url)
                        continue
                    print(url)
                    temp=url.split('.')
                    suffix='jpg'
                    if len(temp)>0:
                        
                        suffix=temp[len(temp)-1]
                        print('suffix=  '+suffix)
                    
                    k+=1
                    with open(path+author_text+str(k)+'.'+suffix,'bw')as f:
                        print('下载第'+str(j)+'个人'+'第'+str(k)+'照片')
                        f.write(_session.get(url,verify=True).content)

                
                
        except:
            print('下载图片出了一点问题')
            traceback.print_exc()
                
    def createPathIfNotExist(self,path):
        root_path=os.path.abspath('.')
        p=root_path+'\\'+path+'\\'
        if not os.path.exists(p):
            os.makedirs(p)
            
        return p
    
    def save_text(self,r):
        global path_for
        pattern_title=re.compile('<span class="zm-editable-content">([\s\S]*?)</span>')
        pattern_desc=re.compile('<div class="zm-editable-content">([\s\S]*?)</div>')
        pattern_answer=re.compile('<span class="count">[\s]*?([\S]*?)</span>[\s\S]*?<div class="zm-editable-content clearfix">([\s\S]*?)</div>')
        
        title=re.findall(pattern_title,r.text)
        #print('title:'+title[0]);
        desc=re.findall(pattern_desc,r.text)
        #print(title,desc)
        #a=re.sub(re.compile('<br>'),'\n',r.text)
        answer_favor_list=re.findall(pattern_answer,r.text)
        pat_sub=re.compile('<br>')
        with open('./'+title[0]+'.txt','w',encoding='utf-8') as f:
            try:
                
                f.write('问题：'+title[0]+'\n\n')
                f.write('描述：'+desc[0]+'\n\n')
                i=0
                for answer in answer_favor_list:
                    i+=1
                    #print('answer[0]--->'+answer[0])

                    if(self.getInt(answer[0])>favor_data):
                        f.write('\n-------------------''答案'+str(i)+'(赞同：'+answer[0]+')''---------------------\n')
                        f.write('\n答案'+str(i)+'(赞同：'+answer[0]+')-->'+re.sub(pat_sub,'\n',answer[1]))
                        f.write('\n++++++++++++++++++++++++this answer is over++++++++++++++++++++++++++++++')
                        f.write('\n\n')
            except Exception as e:
                print('可能在文件读写的时候出了一点问题。。。')
                traceback.print_exc()
    def get(self,url):
        return _session.get(url,headers=header_data,verify=True)
    def getInt(self ,s):
        if 'K' in s:
            return int(s.replace('K','000'))
        return int(s)
    def do_first(self):
        global _session
        _session=requests.session()
        if os.path.exists('cookiefile'):
            #print('have cookies')
            self.read_cookies()
            #self.get_text(question_url)
        else:
            self.login()
        
