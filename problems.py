#! /usr/bin/python
from dynatrace import Dynatrace
# import csv
import os
import pandas as pd
from dotenv import load_dotenv
import pytz
# from flask import Flask, redirect
from datetime import datetime, time, timedelta
# from apscheduler.schedulers.background import BackgroundScheduler
import email, smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from telegram import Update, Bot
from telegram.ext import Application
import asyncio

# Set these via
# export DT_BASE_URL="http://[YOUR-TENANT].live.dynatrace.com"
# export DT_API_TOKEN="[YOUR-TOKEN]"

load_dotenv()

dt = Dynatrace(
    os.getenv("DT_BASE_URL"),
    os.getenv("DT_API_TOKEN")
)

email_sender = os.getenv("EMAIL")
password_sender = os.getenv("PASSWORD")
telegram_token = os.getenv("TELEGRAM_TOKEN")
# id_chat = os.getenv("ID_CHAT")
# id_chat = "-4207697327"
id_chat = "-4254531883"
timezone = 'Asia/Jakarta'

def format_date(the_date):
  if the_date:
    local_timezone = pytz.timezone(timezone)
    local_time = the_date.replace(tzinfo=pytz.utc).astimezone(local_timezone)
    return local_time.strftime("%m/%d/%Y %H:%M:%S")
  else:
    return ""
  
# def wib_converter(time):
#   jakarta_timezone = pytz.timezone(timezone)
#   dt_parse = jakarta_timezone.localize(datetime.strptime(time, "%Y-%m-%dT%H:%M:%S"))
#   time_utc = dt_parse.astimezone(pytz.utc)
#   return time_utc.strftime("%Y-%m-%dT%H:%M:%S")

def convert_csv(csv_name, excel_name):
    df_csv = pd.read_csv(csv_name, sep='|', header=0)
    with pd.ExcelWriter(excel_name, engine='xlsxwriter') as writer:
        df_csv.to_excel(writer, index=False, sheet_name='Sheet1')
        workbook = writer.book
        worksheet = writer.sheets['Sheet1']

        wrap_format = workbook.add_format({'text_wrap': True, 'align': 'center', 'valign': 'vcenter'})
        for column in df_csv.columns:
            col_idx = df_csv.columns.get_loc(column)
            worksheet.set_column(col_idx, col_idx, 20, wrap_format)
  
def send_email():
  subject = "Problem Report"
  body = "This is a problem report send to you."
  sender_email = email_sender
  receiver_email = "****@gmail.com"
  sender_password = password_sender

  message = MIMEMultipart()
  message['Subject'] = subject
  message['From'] = sender_email
  message['To'] = receiver_email
  message.attach(MIMEText(body, 'plain'))
  
  filename = "problems.csv"

  with open(filename, "rb") as attachment:
      part = MIMEBase("application", "octet-stream")
      part.set_payload(attachment.read())
 
  encoders.encode_base64(part)

  part.add_header(
      "Content-Disposition",
      f"attachment; filename= {filename}",
  )

  message.attach(part)
  text = message.as_string()

  # Log in to server using secure context and send email
  context = ssl.create_default_context()
  # with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
  #     server.login(sender_email, sender_password)
  #     server.sendmail(sender_email, receiver_email, text)
  print("Attempting to connect to the SMTP server...")
  with smtplib.SMTP("smtp.gmail.com", 587) as server:
      server.ehlo()  # Can be omitted
      server.starttls(context=context)
      server.ehlo()  # Can be omitted
      server.login(sender_email, sender_password)
      server.sendmail(sender_email, receiver_email, text)
  print("Email sent successfully!")
  
   
async def run(): 
  # adjust as required
  # time_from = wib_converter("2024-07-01T00:00:00")
  # time_to = wib_converter("2024-07-02T23:59:59")
  wib = pytz.timezone('Asia/Jakarta')

  # Calculate the start and end time for yesterday in WIB
  now_wib = datetime.now(wib)
  yesterday_start = (now_wib - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
  yesterday_end = (now_wib - timedelta(days=1)).replace(hour=23, minute=59, second=59, microsecond=0)

  # Convert to ISO 8601 format with millisecond precision
  time_from = yesterday_start.isoformat(timespec='milliseconds')
  time_to = yesterday_end.isoformat(timespec='milliseconds')
  # problems = dt.problems.list(time_from="now-1d",problem_selector='status("closed")')
  # problems = dt.problems.list(time_from="now-1d")
  #problems = dt.problems.list(time_from="now-180d",problem_selector='status("closed"),managementZoneIds("mZId-1", "mzId-2")')
  #problems = dt.problems.list(time_from="now-30m") #,entity_selector='type("CUSTOM_DEVICE")')
  #problems = dt.problems.list(time_from="now-120d",time_to="now-60d",problem_selector='affectedEntityTypes("CUSTOM_DEVICE")')
  #problems = dt.problems.list(time_from="2021-01-25T00:00:00",time_to="2023-02-10T00:00:00",problem_selector='affectedEntityTypes("CUSTOM_DEVICE")')
  # problems = dt.problems.list(time_from="now-3d/d", time_to="now-2d",problem_selector='managementZones("BNIDIRECT")')
  problems = dt.problems.list(time_from=time_from, time_to=time_to, problem_selector='managementZones("BNIDIRECT")')
  # problems = dt.problems.list(time_from=time_from,time_to=time_to,problem_selector='managementZones("BNIDIRECT")')
  
  data = []

  if not problems:
    print("No problems found")
    quit()

  for problem in problems:
    pr=problem.json()
    print(pr)
    if 'recentComments' in pr:
        co = pr['recentComments']
        for c in co:
          com = co['totalCount']
    else:
          print('Skipping comments')
          com=0
    
    impacted_entity_names = [entity.name for entity in problem.impacted_entities]
    impacted_entity_names_join = ', '.join(impacted_entity_names)
    data.append({
      'problem': problem.display_id,
      'title': problem.title,
      'status': str(problem.status).partition(".")[2],
      'impact_level': str(problem.impact_level).partition(".")[2],
      'severity_level': str(problem.severity_level).partition(".")[2],
      'impacted_entities': impacted_entity_names_join,
      'start_time': format_date(problem.start_time),
      'end_time': format_date(problem.end_time)
    })
    
  df = pd.DataFrame(data)
  df.to_csv('problems.csv', sep='|', encoding="utf-8", index=False)
  file_csv = 'problems.csv'
  file_xlsx = 'problems.xlsx'
  convert_csv(file_csv, file_xlsx)
  # send_email()
  
async def send_document(bot: Bot, chat_id):
    max_retries = 5

    for attempt in range(max_retries+1):
        try:
            await bot.send_message(chat_id=chat_id, text="Please wait a few seconds")
            await run()
            await asyncio.sleep(5)
            with open("problems.xlsx", 'rb') as document:
                await bot.send_document(chat_id=chat_id, document=document)
            return
        except Exception as e:
            error_message = f"An unexpected error occurred: {str(e)}"
            await bot.send_message(chat_id=chat_id, text=error_message)
            if attempt < max_retries:
                await asyncio.sleep(5)
                await bot.send_message(chat_id=chat_id, text=f"Retrying Attempt {attempt + 1}/{max_retries}")
            else:
                return

def main():
    bot = Bot(token=telegram_token)
    application = Application.builder().token(telegram_token).connect_timeout(20).read_timeout(20).build()

    # interval = timedelta(minutes=2)
    # application.job_queue.run_repeating(lambda context: asyncio.create_task(send_document(bot, id_chat)), interval)
    
    target_time = time(8, 7, 0)
    local_timezone = pytz.timezone(timezone)
    now = datetime.now(local_timezone)
    target_time = local_timezone.localize(datetime.combine(now.date(), target_time))

    application.job_queue.run_daily(
        lambda context: asyncio.create_task(send_document(bot, id_chat)),
        time=target_time.timetz()
    )

    application.run_polling(allowed_updates=Update.ALL_TYPES)
    
if __name__ == "__main__":
  print("running...")
  main()

# Using Flask

# scheduler = BackgroundScheduler()
# app = Flask(__name__)

# @app.route("/")
# def index():
#     return redirect("/start")

# @app.route("/start")
# def start():
#   global scheduler
#   if not scheduler.running:
#     scheduler = BackgroundScheduler()
#     scheduler.add_job(func=run, trigger='interval', seconds=20)
#     scheduler.start()
#     return "Scheduler berhasil dijalankan"
#   else:
#     return "Scheduler sudah berjalan"

# @app.route("/stop")
# def stop():
#   global scheduler
#   if scheduler.running:
#     scheduler.shutdown()
#     return "Scheduler berhasil dihentikan"
#   else:
#     return "Scheduler sudah tidak berjalan"