import shutil

def send_alert(im):
    shutil.copy(im, f"capture/{im[-6:]}")

