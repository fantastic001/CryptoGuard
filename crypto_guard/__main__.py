# import sparkml and spark graph and setup local cluster and run the application

from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.tuning import ParamGridBuilder, TrainValidationSplit
from pyspark.ml import Pipeline
from pyspark.ml.feature import StandardScaler
from pyspark.ml.feature import MinMaxScaler
from pyspark.ml.feature import MaxAbsScaler
from pyspark.ml.feature import Normalizer
from pyspark.ml.feature import StringIndexer
from pyspark.ml.feature import OneHotEncoder
from pyspark.ml.feature import VectorIndexer
from pyspark.ml.feature import Bucketizer
from pyspark.ml.feature import QuantileDiscretizer

import argparse 
from crypto_guard.scrape import *


# we have several subcommands:
# scrape - which scrapes bitcoin Scam Reports from chainabuse and saves them to a csv file
# train - which trains a model on the data
# predict - which predicts the likelihood of a transaction being a scam

# we will use argparse to parse the command line arguments
# we will use the subparser to add the subcommands

parser = argparse.ArgumentParser(description="CryptoGuard: A tool to detect crypto scams")
subparsers = parser.add_subparsers(dest="subcommand")

scrape_parser = subparsers.add_parser("scrape", help="Scrape bitcoin scam reports from chainabuse")
train_parser = subparsers.add_parser("train", help="Train a model on the data")
predict_parser = subparsers.add_parser("predict", help="Predict the likelihood of a transaction being a scam")

scrape_parser.add_argument("--output", help="Output file to save the data to", required=True)
scrape_parser.add_argument("--malicious-transactions-csv", help="CSV file containing malicious transactions", required=True)
scrape_parser.add_argument("-n", help="Number of transactions to scrapeafter each malicious transaction", type=int, default=1000)

train_parser.add_argument("--input", help="Input file to train the model on", required=True)
train_parser.add_argument("--output", help="Output file to save the model to", required=True)

predict_parser.add_argument("--input", help="Input file to predict the likelihood of a transaction being a scam", required=True)

# parse the arguments
args = parser.parse_args()


def main():
    spark = SparkSession.builder.appName("CryptoGuard").getOrCreate()
    sc = spark.sparkContext
    if args.subcommand == "scrape":
        print("Scraping data...")
        scrape(args.output, args.malicious_transactions_csv, args.n)
    elif args.subcommand == "train":
        from crypto_guard.train import train
        train(spark, args.input, args.output)
    elif args.subcommand == "predict":
        from crypto_guard.predict import predict
        predict(spark, args.input)

    spark.stop()

    
if __name__ == "__main__":
    main()