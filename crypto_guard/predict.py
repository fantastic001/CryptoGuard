from pyspark.ml.tuning import CrossValidatorModel

def predict(spark, input_transaction: str, model_path: str):
    df = spark.read.csv(input_transaction, header=True, inferSchema=True)
    model = CrossValidatorModel.load(model_path)
    predictions = model.transform(df)
    predictions.show()