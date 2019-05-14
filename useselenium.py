import re
from time import sleep

from PIL import Image
from selenium import webdriver
from selenium.webdriver import ActionChains
import txyzm
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class WeiMengLogin():
    def __init__(self, username, password, executable_path, usernameinput='phone', passwordinput='pwd',
                 button='slide_bar_head', image='slideBkg'):
        d = DesiredCapabilities.CHROME
        d['loggingPrefs'] = {'performance': 'ALL'}
        self.webchrome = webdriver.Chrome(executable_path=executable_path, desired_capabilities=d)
        self.username = username
        self.password = password
        self.usernameinput = usernameinput  # 用户名输入框标签的id
        self.passwordinput = passwordinput  # 密码输入框标签id
        self.button = button  # 点击的滑块id
        self.image = image  # 验证码图片的id

    def input_name_password(self):
        """
        输入用户名和密码，选择输入框的元素用的是id
        """
        usename_element = self.webchrome.find_element_by_id(self.usernameinput)
        password_element = self.webchrome.find_element_by_id(self.passwordinput)
        for i in self.username:
            usename_element.send_keys(i)
            sleep(0.1)

        for i in self.password:
            password_element.send_keys(i)
            sleep(0.1)

    def slide_button(self, x_left):
        """
        点击滑块并滑动指定的距离，目前腾讯的验证码不检测滑动的轨迹
        """
        self.webchrome.switch_to.frame(self.webchrome.find_element_by_tag_name("iframe"))
        buttem = self.webchrome.find_element_by_id(self.button)
        ActionChains(self.webchrome).click_and_hold(buttem).perform()
        ActionChains(self.webchrome).move_by_offset(xoffset=x_left, yoffset=0).perform()
        sleep(1)
        ActionChains(self.webchrome).release().perform()
        self.webchrome.switch_to.default_content()
        sleep(1)

    def get_image(self):
        """
        对整个窗口进行截图后去确定验证码在图片中的位置并且截图后保存
        """
        self.slide_button(0)
        self.webchrome.get_screenshot_as_file('cap.png')  # 对整个页面进行截图保存
        iframe = self.webchrome.find_element_by_xpath('//iframe')  # 获取iframe标签对整个窗口的位置
        x = iframe.location['x']
        y = iframe.location['y']
        self.webchrome.switch_to.frame(self.webchrome.find_element_by_tag_name("iframe"))  # 切换到iframe标签
        # 获取验证码的图片标签，并计算对整个页面的位置就是验证码的相对iframe的位置加上iframe相对整个页面的位置
        image = self.webchrome.find_element_by_id(self.image)
        left = image.location['x'] + x
        top = image.location['y'] + y
        right = left + image.size['width']
        bottom = top + image.size['height']

        im = Image.open('cap.png')
        im = im.crop((left, top, right, bottom))
        im.save('newcap.png')
        self.webchrome.switch_to.default_content()

    def button_xleft(self, ditto=False):
        """
        获取需要滑动的距离，当参数为True的时候就刷新一下验证码去重新获取验证码图片
        """
        if ditto:
            self.slide_button(0)
            sleep(1)
            self.slide_button(0)  # 点击三次刷新图片,因为获取图片的时候已经点击了一次，所以这里只需要点击两次
            sleep(1)
            self.get_image()
        else:
            image = Image.open('newcap.png')
            image.convert("L")
            image = image.point(lambda x: 0 if x > 100 else 255)
            image = image.convert('1')
            return txyzm.GetGap(image).loop_find()  # 获取滑动的距离

    def get_token_cookies(self):
        """
        我开启了日志，在判断登陆成功了之后就查询日志中的请求头，取出用户token和查询表单必须要有的cookie并返回
        这个登陆到此就算完成了
        """
        Authorization = ''
        for i in self.webchrome.get_log('performance'):
            try:
                Authorization = re.findall(r'Authorization":"(.*?)",', str(i))[0]
                if Authorization[0:7] == 'Bearer ':
                    break
            except:
                pass
        cookie = self.webchrome.get_cookie('O2O-online_osessionid').get('value')
        return Authorization, cookie

    def wokening(self, number):
        # 这里不知道咋写，只能重复判断是否登陆成功三次还是不行就算了
        sleep(5)
        if self.webchrome.title == '微盟' or self.webchrome.title == '智慧餐厅 - 微盟':
            print('登陆成功')
            sleep(10)
            a = self.get_token_cookies()
            return a

        number += 1
        if number == 4:
            return

        self.get_image()
        x = self.button_xleft()

        if x is None:
            self.button_xleft(ditto=True)
        else:
            self.slide_button(x)

        return self.wokening(number)

    def woken(self):
        self.webchrome.get('https://account.weimob.com/login.html')
        self.input_name_password()
        self.webchrome.find_element_by_class_name('login-btn').click()  # 点击登录按键
        sleep(5)
        a = self.wokening(1)
        return a

    def __del__(self):
        self.webchrome.quit()


print(WeiMengLogin('账户', '密码', 'chromedriver地址').woken())


