import sys
import logging
import time
import pytz
import os
from datetime import datetime, timezone
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import threading

meetingCount = 0
load_dotenv()
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
ist = pytz.timezone("Asia/Kolkata")

meeting_link = ""
session_endTime = ""

if len(sys.argv) > 3:
    meeting_link = sys.argv[1]
    session_endTime = sys.argv[2]
    mentorName = sys.argv[3]
    print(f"Joining meeting: {meeting_link}")
else:
    print("No meeting link provided!")
    sys.exit(1)

print("Session End Time -------->",datetime.strptime(session_endTime, '%Y-%m-%dT%H:%M:%SZ'))
session_endTime = datetime.strptime(session_endTime, '%Y-%m-%dT%H:%M:%SZ')
session_endTime = pytz.utc.localize(session_endTime)

class ProPeersGoogleMeetBoat:
    def __init__(self, email, password, meet_link):
        self.email = email
        self.password = password
        self.meet_link = meet_link
        self.driver = None
        self.wait = None
        self.actions = None

    def setup_driver(self):
        logger.info("Setting up the WebDriver...")
        options = webdriver.ChromeOptions()
        options.add_argument("--use-fake-ui-for-media-stream")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-notifications")
        # options.add_argument("user-data-dir=C:/Users/propeers/AppData/Local/Google/Chrome/User Data")  # Path to your Chrome user data directory
        self.driver = webdriver.Chrome(options=options)
        self.actions = ActionChains(self.driver)
        self.wait = WebDriverWait(self.driver, 5)
        logger.info("WebDriver setup complete.")

    def login(self):
        logger.info("Logging into Google account...")
        self.driver.get("https://accounts.google.com/signin")
        
        # Enter email
        email_field = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="email"]')))
        email_field.send_keys(self.email)
        self.driver.find_element(By.ID, "identifierNext").click()
        time.sleep(2)

        # Enter password
        password_field = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="password"]')))
        password_field.send_keys(self.password)
        self.driver.find_element(By.ID, "passwordNext").click()
        time.sleep(2)
        logger.info("Successfully logged in.")

    def join_meeting(self):
        logger.info("Navigating to Google Meet...")
        self.driver.get(self.meet_link)
        time.sleep(2)

        # Handle the "Got it" button if it appears
        try:
            got_it_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Got it')]"))
            )
            got_it_button.click()
            logger.info("Clicked 'Got it' button.")
        except:
            logger.info("'Got it' button not found, skipping.")

        # Mute the camera
        try:
            camera_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[aria-label="Turn off camera"]'))
            )
            camera_button.click()
            logger.info("Camera turned off.")
        except:
            logger.warning("Camera button not found or already turned off.")

        # Mute the microphone
        try:
            mic_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[aria-label="Turn off microphone"]'))
            )
            mic_button.click()
            logger.info("Microphone turned off.")
        except:
            logger.warning("Microphone button not found or already turned off.")

        # Attempt to find and click the join button
        join_button_selectors = [
            'button[jsname="Qx7uuf"] span',
            'button[jscontroller="O626Fe"] span',
            '.UywwFc-vQzf8d',
            '.VfPpkd-dgl2Hf-ppHlrf-sM5MNb button span'
        ]

        for selector in join_button_selectors:
            try:
                join_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                join_button.click()
                logger.info("Successfully joined the meeting.")
                break
            except:
                continue

        logger.info("Successfully joined the meeting.")
        
    def admit_all_members(self):
        global meetingCount
        logger.info("Try to Admitting all members...")
        admit_All_button_selector = '//span[text()="Admit all"]/ancestor::button[@jsname="ykjzed"][@jscontroller="soHxf"]'

        self.click_on_people()
        time.sleep(1)

        # try:
        #     admit_all = self.wait.until(EC.element_to_be_clickable((By.XPATH, admit_All_button_selector)))
        #     admit_all.click()
        #     logger.info("Successfully clicked on 'Admit all' button...")
        # except Exception as e:
        #     logger.error(f"Error clicking 'Admit all' button: {e}")

        # try:
        #     logger.info("Waiting 5 seconds before searching for the 'Admit' button...")
        #     time.sleep(5)

        #     logger.info("Waiting for the 'Admit' button to be clickable...")
        #     admit_button = self.wait.until(EC.presence_of_element_located((By.XPATH, '//span[text()="Admit"]')))

        #     logger.info("Attempting to click using JavaScript...")
        #     self.driver.execute_script("arguments[0].click();", admit_button)

        #     logger.info("Successfully clicked the 'Admit' button in the modal, admitting all people.")

        #     meetingCount += 1
        #     logger.info(f"Meeting count incremented to {meetingCount}")

        # except Exception as e:
        #     logger.error(f"Failed to click the 'Admit' button: {e}")
        
        try:
            # Click on 'Admit all' button
            admit_all = self.wait.until(EC.element_to_be_clickable((By.XPATH, admit_All_button_selector)))
            admit_all.click()
            logger.info("Successfully clicked on 'Admit all' button.")
            logger.info(f"Meeting count incremented to {meetingCount}")

            # Close modal by clicking outside
            time.sleep(2)
            self.driver.find_element(By.TAG_NAME, "body").click()
            logger.info("Clicked outside to close the modal.")

        except Exception as e:
            logger.error(f"Error clicking 'Admit all' button: {e}")

        try:
            # If 'Admit all' button is not found, try admitting individuals
            logger.info("Waiting 5 seconds before searching for the 'Admit' button...")
            time.sleep(3)

            admit_button = self.wait.until(EC.presence_of_element_located((By.XPATH, '//span[text()="Admit"]')))
            logger.info("Attempting to click 'Admit' button using JavaScript...")
            self.driver.execute_script("arguments[0].click();", admit_button)
            logger.info("Successfully clicked the 'Admit' button.")

            meetingCount += 1
            logger.info(f"Meeting count incremented to {meetingCount}")

            # Close modal by pressing ESC
            time.sleep(2)
            self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
            logger.info("Pressed ESC to close the modal.")

        except Exception as e:
            logger.error(f"Failed to click the 'Admit' button: {e}")


    def open_more_options(self):
        logger.info("Opening 'More options'...")
        more_options_button = self.wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR, 
                'button[jscontroller="PIVayb"][jsname="NakZHc"][aria-label="More options"]'
            ))
        )
        more_options_button.click()
        logger.info("Successfully opened 'More options'.")
    def click_manage_recording(self):
        logger.info("Clicking on 'Manage recording' option...")
        first_menu_item = self.wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//ul[@role='menu']//li[1]"
            ))
        )
        first_menu_item.click()
        logger.info("Successfully clicked 'Manage recording'.")

    def start_recording(self):
        logger.info("Entering into the start_recording function...")
        start_recording_button = self.wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR, 
                'button[jsname="A0ONe"][aria-label="Start recording"]'
            ))
        )
        start_recording_button.click()
        logger.info("Successfully started recording.")
        
    def confirm_start(self):
        logger.info("Confirming recording start...")
        start_button = self.wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR, 
                'button[jscontroller="O626Fe"][data-mdc-dialog-action="A9Emjd"] span[jsname="V67aGc"].mUIrbf-vQzf8d'
            ))
        )
        start_button.click()
        logger.info("Recording confirmed and started.")
        
    def all_about_start_recording(self):
        self.open_more_options()
        time.sleep(1)
        self.click_manage_recording()
        time.sleep(1)
        self.start_recording()
        time.sleep(1)
        self.confirm_start()
        time.sleep(1)
    def click_on_people(self):
        logger.info("Attempting to click on the 'People' button...")
        people_button_selector = '[jsname="A5il2e"][aria-label="People"]'
        try:
            people_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, people_button_selector)))
            logger.info('"People" button found.')
            people_button.click()
            logger.info('Successfully clicked the "People" button.')
        except TimeoutException:
            logger.error('Failed to find the "People" button.')
    
    def make_mentor_host_more_btn(self, mentor_name):
        logger.info(f"Attempting to make {mentor_name} a co-host via the 'More actions' button.")
        parent_div_selector = f'div[role="listitem"][aria-label="{mentor_name}"]'
        more_actions_button_selector = f'{parent_div_selector} div[jscontroller="tu7lyc"] button[aria-label="More actions"]'
        cohost_button_selector = f'ul[role="menu"] li[aria-label="Add {mentor_name} as co-host"]'
        modal_button_selector = 'button.VfPpkd-LgbsSe[data-mdc-dialog-action="ok"][jscontroller="soHxf"]'
        self.click_on_people()
        time.sleep(3)

        try:
            # Wait for the "More actions" button within the parent div for mentor to make co-host
            more_actions_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, more_actions_button_selector)))
            logger.info(f'"Trying" {mentor_name} "More actions" button Click For Making co-host')
            more_actions_button.click()
            time.sleep(3)

            # Wait for the "Add as co-host" button
            cohost_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, cohost_button_selector)))
            logger.info(f'"Add as co-host" of {mentor_name} button found. Clicking it...')
            cohost_button.click()
            logger.info(f'Successfully Click on the BTN {mentor_name} made for co-host')

            time.sleep(3)

            try:
                modal_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, modal_button_selector)))
                logger.info('"Add co-host" button in modal found. Clicking it...')
                modal_button.click()
                logger.info(f'Successfully made {mentor_name} a co-host.')
            except TimeoutException:
                logger.warning(f"Modal did not appear. Assuming {mentor_name} is already a co-host or action succeeded.")
            
            return

        except TimeoutException as e:
            logger.error(f"Timeout while trying to make {mentor_name} a co-host: {e}")
        except NoSuchElementException as e:
            logger.error(f"Element not found while trying to make {mentor_name} a co-host: {e}")
        except Exception as e:
            logger.error(f"An error occurred: {e}")

    def close_driver(self):
        logging.info("Closing the WebDriver.")
        if self.driver:
            self.driver.quit()

def main(bot,host_name):
    global meetingCount
    logger.info(f"Starting main function. Initial meetingCount: {meetingCount}")
    print("Function is running...")

    # while meetingCount < 2:
    #     bot.admit_all_members()
    #     logger.info(f"Again calling admit_all_members. Current meetingCount: {meetingCount}")

    # bot.make_mentor_host_more_btn(host_name)
    time.sleep(2)
    bot.all_about_start_recording()
    print("Stopping recursive calls as meetingCount reached 2 and calling all_about_start_recording")

# if _name_ == "_main_":
#     email = "parikh@propeers.in"
#     password = "parikh1996pP!"
#     meeting_url = "https://meet.google.com/jjm-jwnk-fie"
#     host_name = "Prince Singh"

#     bot = ProPeersGoogleMeetBoat(email, password, meeting_url)
#     bot.setup_driver()
#     try:
#         bot.login()
#         time.sleep(1)
#         bot.join_meeting()
#         recursive_function(bot)
#         # time.sleep(5)
#         # bot.admit_all_members()
#         # time.sleep(1)
#         # bot.make_mentor_host_more_btn(host_name)
#         # time.sleep(1)
#         # bot.all_about_start_recording()
        
#     finally:
#         # bot.close_driver()
#         logger.info("Browser will remain open. You can manually close it.")
#         time.sleep(10000)  

if __name__ == "__main__":
    email = os.getenv("email")
    password = os.getenv("password")
    meeting_url = meeting_link
    print("herrrrreee")
    # meeting_url = "https://meet.google.com/jjm-jwnk-fie"
    # host_name = "Prince Singh"
    host_name = mentorName
    print(email, password, meeting_url)
    bot = ProPeersGoogleMeetBoat(email, password, meeting_url)
    bot.setup_driver()
    try:
        bot.login()
        time.sleep(1)
        bot.join_meeting()
        main(bot,host_name)
        
    except Exception as e:
        print(f"Error in main: {e}")

while True:
    current_time = datetime.now()

    current_time_formatted = current_time.strftime("%Y-%m-%d %H:%M:%S")
    session_endTime_formatted = session_endTime.strftime("%Y-%m-%d %H:%M:%S")

    logger.info(f"Current time -------> {current_time_formatted}")
    logger.info(f"Session end time -------> {session_endTime_formatted}")

    if current_time_formatted >= session_endTime_formatted:
        print("Meeting time ended! Closing the session.")
        break

    # Wait for 1 second before checking again
    time.sleep(1)