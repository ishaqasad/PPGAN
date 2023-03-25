from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time

driver = webdriver.Chrome()
driver.get("https://musescore.com/sheetmusic/piano-voice")
print("Logging In")
driver.get("https://musescore.com/user/login")
user = driver.find_element(by=By.NAME, value="username")
passw = driver.find_element(by=By.NAME, value="password")

log = driver.find_element(by=By.NAME, value="op")
user.send_keys("")
passw.send_keys("");
log.click()
print("Logged In")
count = 0
for i in range(3,4):
    print("Page ", i)
    driver.get("https://musescore.com/sheetmusic/piano-voice?page=" + str(i)) 
    links = driver.find_elements(By.TAG_NAME, "img")
    actions = ActionChains(driver)

    for i in range(0,len(links)):
        actions.key_down(Keys.COMMAND)
        actions.click(links[i])
        actions.perform()




    windows = driver.window_handles
    for i in range(1,len(windows)):
        driver.switch_to.window(windows[i])
        url = driver.current_url
        print(url)
        if("play.google" in url or "apps.apple" in url):
            print("here")
            driver.close()
            continue
        try:
            down = driver.find_element(by=By.NAME, value="download")
        except:
            driver.close()
            continue

        down.click()
        time.sleep(1)
        midi = driver.find_elements(by=By.CLASS_NAME , value = "q0JKL")
        index = 0
        for i in range(len(midi)):
            if(midi[i].text == "MIDI"):
                index = i
                break;
        print(midi[index].text)
        count += 1
        print("Current File Count " , count)
        time.sleep(2)
        driver.close()
        
    driver.switch_to.window(windows[0])



    
