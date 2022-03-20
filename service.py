# import schedule
#
# import config
# from supertrend import run_bot
#
#
# def start_bot(request):
#     data = request.get_json()
#
#     if "passphrase" not in data or data["passphrase"] != config.PASSPHRASE:
#         return {
#             "code": "error",
#             "message": "You are unauthorized."
#         }
#     else:
#         if data["action"] == "start":
#             schedule.every(60).seconds.do(run_bot)