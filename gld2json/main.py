import argparse
import pandas as pd


def main(args):
    df = pd.read_excel(args.input)
    print(df)


if __name__ == '__main__':
    parser = argparse.ArgumentParser('Create a CLDF dataset out of a GLD table')
    parser.add_argument('--input', type=str, help='Input .xls file')
    parser.add_argument('--output_dir', type=str, help='Where to save the result')

    args = parser.parse_args()
    main(args)
