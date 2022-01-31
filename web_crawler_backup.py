import os
import re
import time
import requests
from bs4 import BeautifulSoup
from datetime import date, timedelta, datetime
import logging
from requests_ip_rotator import ApiGateway, EXTRA_REGIONS
import json

# Start Logger configuration
today_as_day = date.today().strftime("%a")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger_formatter = logging.Formatter('[%(asctime)s][%(name)s][Line %(lineno)d][%(levelname)s]:%(message)s')

file_handler = logging.FileHandler('logs/Web_Crawler.logs', mode='w')

file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logger_formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logger_formatter)
stream_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

print("Please see logs/Web_Crawler.logs for execution information.")
# end logger configuration

def getDataFrom_usnews():
    logger.info("usnews data is pulling!!")
    startTime = datetime.now()
    domain = "https://www.usnews.com/"
    url = "https://health.usnews.com/doctors/radiologists/new-york"
    query_string = "radiologists"
    try:
        html_content = requests.get(url, headers={"User-Agent": "XY"}).text
        soup = BeautifulSoup(html_content, "lxml")
        pagination = soup.find('ol', attrs={'class': 'page-numbers__List-sc-138ov1k-2'})
        specialty = query_string.replace("-"," ")
        print(specialty)
        if pagination:
            FinalDataArray = []
            page_count_content = pagination.find_all('button', attrs={'class': 'page-numbers__Button-sc-138ov1k-4'})[
                -1].text
            for page in range(int(page_count_content) + 1):
                url_payload = {
                    "distance": "in -state",
                    "location": "New York",
                    "specialty": specialty,
                    "page_num": page
                }
                url = ("https://health.usnews.com/health-care/doctors/search-data?")
                html_content = requests.get(url, headers={"User-Agent": "XY"}, params=url_payload).text
                soup = BeautifulSoup(html_content, "lxml")

                doctor_data = soup.find('p').text
                if doctor_data.startswith("The"):
                    continue
                a = open("a.json", "w+")
                a.write(doctor_data)
                r = open("a.json", "r+")
                data1 = json.load(r)
                doctor_content = data1["doctor_search"]["results"]["doctors"]["matches"]
                for data in doctor_content:
                    doctor_title = data["name_prefix"]
                    doctor_first_name = data["first_name"]
                    doctor_last_name = data["last_name"]
                    doctor_qualification = data["title"]
                    doctor_specialties = data["specialty"]
                    doctor_address = ""
                    doctor_address_content = data["location"]
                    doctor_address_data = []
                    for key, value in doctor_address_content.items():
                        if key == "street_address":
                            doctor_address_data.append(value)
                        else:
                            doctor_address_data.append("")
                        if key == "city":
                            doctor_address_data.append(value)
                        else:
                            doctor_address_data.append("")
                        if key == "state":
                            doctor_address_data.append(value)
                        else:
                            doctor_address_data.append("")
                        if key == "zip_code":
                            doctor_address_data.append(value)
                        else:
                            doctor_address_data.append("")
                    doctor_address = doctor_address_data[3] + ',' + doctor_address_data[0] + ',' + doctor_address_data[
                        1] + ',' + doctor_address_data[2]
                    doctor_contact = ""
                    if data["appointment_booking"] == False:
                        doctor_contact = ""
                    else:
                        doctor_contact = data["appointment_booking"]["phone"] + ','
                    if data["phone"]:
                        doctor_contact += data["phone"]
                    hospital_name = data["affiliated_hospital"]
                    if hospital_name == None:
                        hospital_name = ""

                    x = {
                        "doctor_title": doctor_title.strip(),
                        "doctor_first_name": doctor_first_name.strip(),
                        "doctor_last_name": doctor_last_name.strip(),
                        "doctor_qualification": doctor_qualification.strip(),
                        "doctor_specialties": doctor_specialties.strip(),
                        "doctor_address": doctor_address.strip(),
                        "doctor_contact": doctor_contact.strip(),
                        "hospital_name": hospital_name.strip()
                    }
                    FinalDataArray.append(x)

            logger.debug(FinalDataArray)
            logger.info("usnews took time :" + str(datetime.now() - startTime))
            logger.info(f"usnews data pulled successfully!! got {len(FinalDataArray)} rows")
        else:
            logger.error("pagination not found")
    except Exception as e:
        logger.error(e)
        logger.error("usnews data pulling failed")

if __name__ == '__main__':
    getDataFrom_usnews()

