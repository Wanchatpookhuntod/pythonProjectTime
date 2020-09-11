from win10toast import ToastNotifier
import time

toaster = ToastNotifier()
# toaster.show_toast("Hello World!!!",
#                    "Python is 10 seconds awsm!",
#                    icon_path="custom.ico",
#                    duration=2)

x = toaster.show_toast("Example two",
                   "This notification is in it's own thread!\n"
                   "This notification is in it's own thread!\n"
                   "This notification is in it's own thread!\n"
                   "This notification is in it's own thread!\n"
                   "This notification is in it's own thread!",
                   icon_path=None,
                   duration=5,
                   threaded=True)
print(x)
# Wait for threaded notification to finish
