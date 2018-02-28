dsn = "http://8d8598f5461949bdb8e113eab19344c9:f089949a985f472d87d9ac491bc6d8aa@120.79.48.216:9000//7"

from raven import Client

client = Client(dsn)

try:
    1 / 0
except ZeroDivisionError:
    client.captureException()