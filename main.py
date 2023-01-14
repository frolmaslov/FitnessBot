from handlers import dp, scheduler, verify, send_message, executor


scheduler.add_job(verify, 'cron', day_of_week='mon-sun', hour=23, minute=45)
scheduler.add_job(send_message, 'cron', day_of_week='mon-sun', hour=12, minute=00, args=(dp,))


if __name__ == '__main__':
    scheduler.start()
    executor.start_polling(dp, skip_updates=True)
