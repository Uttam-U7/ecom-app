import razorpay
import os

client = razorpay.Client(auth=(
    os.getenv("RAZORPAY_TEST_KEY_ID"),
    os.getenv("RAZORPAY_TEST_SECRET")
))