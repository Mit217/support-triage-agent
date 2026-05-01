import pandas as pd

def load_tickets(path="support_tickets/support_tickets.csv"):
    return pd.read_csv(path)