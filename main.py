import pandas as pd


def main():
    file_poznan = pd.read_csv("data/blood_donation_poznan.csv")
    file_warsaw = pd.read_csv("data/blood_donation_warsaw.csv")
    df_p = pd.DataFrame(file_poznan)
    df_w = pd.DataFrame(file_warsaw)


if __name__ == "__main__":
    main()
