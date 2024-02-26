from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import requests
from tempfile import mkdtemp
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, NoSuchElementException, ElementClickInterceptedException  # Import ElementClickInterceptedException
import time
#from webdriver_manager.chrome import ChromeDriverManager

def handler(event=None, context=None):
    options = webdriver.ChromeOptions()
    service = webdriver.ChromeService("/opt/chromedriver")

    options.binary_location = '/opt/chrome/chrome'
    options.add_argument("--headless")
    options.add_argument('--no-sandbox')
    #options.add_argument("--disable-gpu")
    #options.add_argument("--window-size=1280x1696")
    options.add_argument("--single-process")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.185 Safari/537.36")
    #options.add_argument("--disable-dev-tools")
    #options.add_argument("--no-zygote")
    # options.add_argument(f"--user-data-dir={mkdtemp()}")
    # options.add_argument(f"--data-path={mkdtemp()}")
    # options.add_argument(f"--disk-cache-dir={mkdtemp()}")
    options.add_argument("--remote-debugging-port=9222")

    # URL to scrape
    url = "https://stocktrack.ca/?s=ikea&search=artificial%20plants"

    # Initialize the Chrome WebDriver
    #driver = webdriver.Chrome()
    driver = webdriver.Chrome(options=options, service=service)
    #driver = webdriver.Chrome(service=Service('./chromedriver'), options=chrome_options)
    #driver.get(url)
    a='Iframe and content successfully loaded.'
    b ='Failed to load the iframe or content within the timeout.'
    c= 'noSuchElementException: Iframe or specific content within the iframe not found.'
    # Navigate to the provided URL
    try:
        driver.get(url)
        
        #Wait for and switch to the iframe
        WebDriverWait(driver, 50).until(
            EC.presence_of_element_located((By.TAG_NAME, 'iframe'))
        )
        iframe = driver.find_element(By.TAG_NAME, 'iframe')
        driver.switch_to.frame(iframe)
        all_elements = driver.find_elements(By.XPATH, "//*")
        # Iterate over all elements to collect their details
        elements_info = []
        for element in all_elements:
            element_info = {
                "tag_name": element.tag_name,
                "text": element.text
            }
            elements_info.append(element_info)

        # Log or return the elements' details
        print(elements_info)   
        # # Wait for the dhx_list_item elements to be visible
        # dhx_list_items = WebDriverWait(driver, 50).until(
        #     EC.visibility_of_all_elements_located((By.CLASS_NAME, "dhx_list_item"))
        # )
        
        # Proceed with actions on dhx_list_items
        # for item in dhx_list_items:
        #     # Your code here to interact with each item
        
        response = {
            'statusCode': 200,
            'body': elements_info
        }
    except Exception as e:
        # Handle exceptions or timeouts
        response = {
            'statusCode': 500,
            'body': b
        }
    finally:
        driver.quit()
        
    return response  
    #Wait for the iframe to load and switch to it
    # try:
    #     wait = WebDriverWait(driver, 50)  # Set a generous timeout for loading
    #     # Wait for the iframe to be present in the DOM
    #     iframe = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'iframe')))
    #     # Switch to the iframe to interact with its content
    #     driver.switch_to.frame(iframe)
        
    #     response = {
    #                 'statusCode': 200,
    #                 'body': a
    #             }
    # except TimeoutException:
    #     response = {
    #         'statusCode': 400,
    #         'body': b
    #     }
    # except NoSuchElementException:
    #     response = {
    #         'statusCode': 404,
    #         'body': c
    #     }
    # finally:
    #     driver.quit()
        
    # return response
    # start_dhx_f_id = 1
    # scraped_products = []
    # while True:
    #     try:
    #         # Wait for the products to load on the current page
    #         WebDriverWait(driver, 170).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "dhx_list_item")))
            
    # #         # Initialize a variable to track whether there are elements with dhx_f_id on the current page
    #         elements_found = False

    #         # Scrape the products on the current page
    #         for i in range(start_dhx_f_id, start_dhx_f_id + 5):
    #             div_xpath = f'//div[@dhx_f_id="{i}"]'

    #             for _ in range(5):
    #                 try:
    #                     div_to_click = driver.find_element(By.XPATH, div_xpath)
    #                     if div_to_click:
    #                         div_to_click.click()
    #                     else:
    #                         break
    #                     div_element = driver.find_element(By.XPATH, f'//div[@dhx_f_id="{i}"]')

    #                     # Extract product information from the div element
    #                     image = div_element.find_element(By.TAG_NAME, 'img').get_attribute('src')
    #                     product_name = div_element.find_element(By.TAG_NAME, 'a').text
    #                     product_link = div_element.find_element(By.TAG_NAME, 'a').get_attribute('href')

    #                     # Split the text by line breaks to extract individual pieces of information
    #                     # Extract the text content from the parent element
    #                     product_info = div_element.text

    #                     # Split the text into lines and extract the relevant information
    #                     lines = product_info.split('\n')

    #                     # Initialize variables to store extracted information
    #                     sku = None
    #                     size = None
    #                     price = None

    #                     # Iterate through the lines to find relevant information
    #                     for line in lines:
    #                         if line.startswith("SKU:"):
    #                             sku = line.replace("SKU:", "").strip()
    #                         elif "cm" in line:
    #                             size = line.strip()
    #                         elif line.startswith("Price:"):
    #                             price = line.replace("Price:", "").strip()
                                
    #                     # Split the price into old and new price if applicable
    #                     if " " in price:
    #                         prices = price.split()
    #                         old_price = prices[0]  # First part is old price
    #                         new_price = prices[1]  # Second part is new price
    #                     else:
    #                         old_price = price
    #                         new_price = 'N/A'                        
    #                     #Print the extracted information
    #                     print(i)
    #                     print("image:", image)
    #                     print("Product Name :", product_name)
    #                     print("Product Link :", product_link)
    #                     print("SKU:", sku)
    #                     print("Size:", size)
    #                     print("Old Price:", old_price)
    #                     print("New Price:", new_price)
    #                     try:

    #                         stock_number_element = WebDriverWait(driver, 30).until(
    #                         EC.presence_of_element_located((By.XPATH, "//td[contains(text(), 'Coquitlam')]/following-sibling::td[3]"))
    #                         )
    #                         stock_number_coq = stock_number_element.text
    #                         print("Coquitlam Store Stock Number:", stock_number_coq)                        
    #                         coq_prob_element = driver.find_element(By.XPATH, "//td[contains(text(), 'Coquitlam')]/following-sibling::td[2]")
    #                         stock_prob_coq = coq_prob_element.text
    #                         print("Coquitlam Store Stock Probability:", stock_prob_coq)
                                            
    #                         rich_element = driver.find_element(By.XPATH, "//td[contains(text(), 'Richmond')]/following-sibling::td[3]")
    #                         stock_number_rich = rich_element.text
    #                         print("Richmond Store Stock Number:", stock_number_rich)                       
    #                         rich_prob_element = driver.find_element(By.XPATH, "//td[contains(text(), 'Richmond')]/following-sibling::td[2]")
    #                         stock_prob_rich = rich_prob_element.text
    #                         print("Richmond Store Stock Probability:", stock_prob_rich)
                            
    #                         stock_element = driver.find_element(By.XPATH, "//td[contains(text(), '529')]/following-sibling::td[5]")
    #                         stock_number_halifax = stock_element.text
    #                         print("Halifax Store Stock Number:", stock_number_halifax)                       
    #                         prob_element = driver.find_element(By.XPATH, "//td[contains(text(), '529')]/following-sibling::td[4]")
    #                         stock_prob_halifax = prob_element.text
    #                         print("Halifax Store Stock Probability:", stock_prob_halifax)   
                            

    #                         stock_element = driver.find_element(By.XPATH, "//td[contains(text(), '559')]/following-sibling::td[5]")
    #                         stock_number_quebec = stock_element.text
    #                         print("Quebec Store Stock Number:", stock_number_quebec)                       
    #                         prob_element = driver.find_element(By.XPATH, "//td[contains(text(), '559')]/following-sibling::td[4]")
    #                         stock_prob_quebec = prob_element.text
    #                         print("Quebec Store Stock Probability:", stock_prob_quebec)                     

    #                         stock_element = driver.find_element(By.XPATH, "//td[contains(text(), '414')]/following-sibling::td[5]")
    #                         stock_number_bouch = stock_element.text
    #                         print("Boucherville Store Stock Number:", stock_number_bouch)                       
    #                         prob_element = driver.find_element(By.XPATH, "//td[contains(text(), '414')]/following-sibling::td[4]")
    #                         stock_prob_bouch = prob_element.text
    #                         print("Boucherville Store Stock Probability:", stock_prob_bouch)
                            
    #                         stock_element = driver.find_element(By.XPATH, "//td[contains(text(), '039')]/following-sibling::td[5]")
    #                         stock_number_montreal = stock_element.text
    #                         print("Montreal Store Stock Number:", stock_number_montreal)                       
    #                         prob_element = driver.find_element(By.XPATH, "//td[contains(text(), '039')]/following-sibling::td[4]")
    #                         stock_prob_montreal = prob_element.text
    #                         print("Montreal Store Stock Probability:", stock_prob_montreal)  

    #                         stock_element = driver.find_element(By.XPATH, "//td[contains(text(), '004')]/following-sibling::td[5]")
    #                         stock_number_ottawa = stock_element.text
    #                         print("Ottawa Store Stock Number:", stock_number_ottawa)                       
    #                         prob_element = driver.find_element(By.XPATH, "//td[contains(text(), '004')]/following-sibling::td[4]")
    #                         stock_prob_ottawa = prob_element.text
    #                         print("Ottawa Store Stock Probability:", stock_prob_ottawa)  

    #                         stock_element = driver.find_element(By.XPATH, "//td[contains(text(), '149')]/following-sibling::td[5]")
    #                         stock_number_nyork = stock_element.text
    #                         print("North York Store Stock Number:", stock_number_nyork)                       
    #                         prob_element = driver.find_element(By.XPATH, "//td[contains(text(), '149')]/following-sibling::td[4]")
    #                         stock_prob_nyork = prob_element.text
    #                         print("North York Store Stock Probability:", stock_prob_nyork)
                            
    #                         stock_element = driver.find_element(By.XPATH, "//td[contains(text(), '256')]/following-sibling::td[5]")
    #                         stock_number_etobicoke = stock_element.text
    #                         print("Etobicoke Store Stock Number:", stock_number_etobicoke)                       
    #                         prob_element = driver.find_element(By.XPATH, "//td[contains(text(), '256')]/following-sibling::td[4]")
    #                         stock_prob_etobicoke = prob_element.text
    #                         print("Etobicoke Store Stock Probability:", stock_prob_etobicoke)  

    #                         stock_element = driver.find_element(By.XPATH, "//td[contains(text(), '372')]/following-sibling::td[5]")
    #                         stock_number_vaughan = stock_element.text
    #                         print("Vaughan Store Stock Number:", stock_number_vaughan)                       
    #                         prob_element = driver.find_element(By.XPATH, "//td[contains(text(), '372')]/following-sibling::td[4]")
    #                         stock_prob_vaughan = prob_element.text
    #                         print("Vaughan Store Stock Probability:", stock_prob_vaughan)
                            
    #                         stock_element = driver.find_element(By.XPATH, "//td[contains(text(), '249')]/following-sibling::td[5]")
    #                         stock_number_winnipeg = stock_element.text
    #                         print("Winnipeg Store Stock Number:", stock_number_winnipeg)                       
    #                         prob_element = driver.find_element(By.XPATH, "//td[contains(text(), '249')]/following-sibling::td[4]")
    #                         stock_prob_winnipeg = prob_element.text
    #                         print("Winnipeg Store Stock Probability:", stock_prob_winnipeg)  

    #                         stock_element = driver.find_element(By.XPATH, "//td[contains(text(), '040')]/following-sibling::td[5]")
    #                         stock_number_burlington = stock_element.text
    #                         print("Burlington Store Stock Number:", stock_number_burlington)                       
    #                         prob_element = driver.find_element(By.XPATH, "//td[contains(text(), '040')]/following-sibling::td[4]")
    #                         stock_prob_burlington = prob_element.text
    #                         print("Burlington Store Stock Probability:", stock_prob_burlington)                          
                            
    #                         stock_element = driver.find_element(By.XPATH, "//td[contains(text(), '349')]/following-sibling::td[5]")
    #                         stock_number_edmonton = stock_element.text
    #                         print("Edmonton Store Stock Number:", stock_number_edmonton)                       
    #                         prob_element = driver.find_element(By.XPATH, "//td[contains(text(), '349')]/following-sibling::td[4]")
    #                         stock_prob_edmonton = prob_element.text
    #                         print("Edmonton Store Stock Probability:", stock_prob_edmonton)
                            
    #                         stock_element = driver.find_element(By.XPATH, "//td[contains(text(), '216')]/following-sibling::td[5]")
    #                         stock_number_calgary = stock_element.text
    #                         print("Calgary Store Stock Number:", stock_number_calgary)                       
    #                         prob_element = driver.find_element(By.XPATH, "//td[contains(text(), '216')]/following-sibling::td[4]")
    #                         stock_prob_calgary = prob_element.text
    #                         print("Calgary Store Stock Probability:", stock_prob_calgary) 
                            
                            
    #                     except TimeoutException:
    #                         print("Timed out waiting for the Coquitlam stock number to load")
    #                     except NoSuchElementException:
    #                         print("Coquitlam stock number element not found.")       
    #                     print()
    #                     product_data = {
    #                     'image_url': image,
    #                     'product_name': product_name,
    #                     'product_link': product_link,
    #                     'product_size' : size,
    #                     'product_sku': sku,
    #                     'product_price_old': old_price,
    #                     'product_price_new' : new_price,
    #                     'stock_probability_coquitlam' : stock_prob_coq,   
    #                     'stock_number_coquitlam' : stock_number_coq,
    #                     'stock_probability_richmond' : stock_prob_rich,
    #                     'stock_number_richmond' : stock_number_rich,
    #                     'stock_probability_halifax' : stock_prob_halifax,    
    #                     'stock_number_halifax' : stock_number_halifax,
    #                     'stock_probability_quebec' : stock_prob_quebec,
    #                     'stock_number_quebec' : stock_number_quebec,
    #                     'stock_probability_boucherville' : stock_prob_bouch,
    #                     'stock_number_boucherville' : stock_number_bouch,
    #                     'stock_probability_montreal' : stock_prob_montreal,
    #                     'stock_number_montreal' : stock_number_montreal,
    #                     'stock_probability_ottawa' : stock_prob_ottawa,
    #                     'stock_number_ottawa' : stock_number_ottawa,
    #                     'stock_probability_nyork' : stock_prob_nyork,
    #                     'stock_number_nyork' : stock_number_nyork,
    #                     'stock_probability_etobicoke' : stock_prob_etobicoke,
    #                     'stock_number_etobicoke' : stock_number_etobicoke,
    #                     'stock_probability_vaughan' : stock_prob_vaughan,
    #                     'stock_number_vaughan' : stock_number_vaughan,
    #                     'stock_probability_burlington' : stock_prob_burlington,
    #                     'stock_number_burlington' : stock_number_burlington,
    #                     'stock_probability_winnipeg' : stock_prob_winnipeg,
    #                     'stock_number_winnipeg' : stock_number_winnipeg,
    #                     'stock_probability_edmonton' : stock_prob_edmonton,
    #                     'stock_number_edmonton' : stock_number_edmonton,
    #                     'stock_probability_calgary' : stock_prob_calgary,
    #                     'stock_number_calgary' : stock_number_calgary

    #                     }
    #                     # Append the product data to the list
    #                     scraped_products.append(product_data)
    #                     # Set elements_found to True since elements with dhx_f_id were found
    #                     elements_found = True

    #                     break  # Exit the loop if the click is successful
    #                 except StaleElementReferenceException:
    #                     continue  # Retry if a StaleElementReferenceException occurs
    #                 except ElementClickInterceptedException:
    #                     print("Element click intercepted. Trying again.")
            
    #         # If no elements with dhx_f_id were found on the current page, break out of the loop
    #         if not elements_found:
    #             break
    #         print()
            
    #         # Check if the "Next" button is clickable
    #         next_page_link = driver.find_element(By.XPATH, "//div[@dhx_p_id='next']")
    #         if not next_page_link.is_enabled():
    #             break  # Break out of the loop if the "Next" button is not clickable

    #         # Move to the next page by clicking the 'next page' link
    #         ActionChains(driver).move_to_element(next_page_link).click(next_page_link).perform()
    #         start_dhx_f_id += 5
    #     except TimeoutException:
    #         print("Timed out waiting for products to load.")
        
    #     except NoSuchElementException:
    #             print(f"Element with dhx_f_id='{i}' not found. Exiting loop.")
    #             break  # Exit the loop if the element is not found

    #     time.sleep(10)


    