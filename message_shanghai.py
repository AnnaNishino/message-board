#!/usr/bin/env python
# coding: utf-8

# In[102]:


import requests as rq
from datetime import datetime, timedelta
import time
import pandas as pd
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.select import Select


# In[4]:


options = Options()
options.add_argument('--headless')
d = DesiredCapabilities.CHROME
d['goog:loggingPrefs'] = { 'performance': 'ALL' }
driver = webdriver.Chrome(options=options, desired_capabilities=d)


# In[94]:


#from webdriver_manager.chrome import ChromeDriverManager
#d = DesiredCapabilities.CHROME
#d['goog:loggingPrefs'] = { 'performance': 'ALL' }
#driver = webdriver.Chrome(ChromeDriverManager().install(), desired_capabilities=d)


# In[95]:


url = "https://liuyan.people.com.cn/threads/searchIndex?keywords=%E4%B8%8A%E6%B5%B7"


# In[96]:


driver.get(url)


# In[97]:


dropdown = driver.find_element_by_id('timeRange')
select = Select(dropdown)
select.select_by_visible_text('6 个月內')


# In[98]:


driver.find_element_by_css_selector("input[value='搜索']").click()


# In[99]:


next_page = driver.find_element_by_id("show_more")
    
while next_page:
    driver.implicitly_wait(5) 
    try:
        next_page.click()
        next_page = driver.find_element_by_id("show_more")
    except:
        break


# In[100]:


netLog = driver.get_log("performance")


# In[103]:


json_address = []
request_id = []

for entry_json in netLog:
    entry = json.loads(entry_json['message'])
    try:
        u = entry['message']['params']['request']['url']
        r = entry['message']['params']['requestId']
        if 'https://liuyan.people.com.cn/threads/search?lastItem' in u:
            json_address.append(u)
            request_id.append(r)
    except:
        pass


# In[111]:


df = pd.DataFrame()

for i in request_id:
    j = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId':i})
    a  = json.loads(j['body'])
    df = pd.concat([df,pd.DataFrame(a['responseData']['rows'])])


# In[113]:


df = df.drop_duplicates()


# In[114]:


df['subject'] = df['subject'].replace("<label style='color:red'>",'',regex=True).replace("</label>",'',regex=True)
df['content'] = df['content'].replace("<label style='color:red'>",'',regex=True).replace("</label>",'',regex=True)


# In[115]:


df['date'] = pd.to_datetime([datetime.fromtimestamp(i).strftime('%Y-%m-%d') for i in df['dateline']])


# In[35]:


df.to_csv('data/'+datetime.today().strftime('%Y%m%d')+'_shanghai.csv', encoding='utf_8_sig')





