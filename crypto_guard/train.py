from pyspark.sql import SparkSession
from pyspark.sql import DataFrame
from crypto_guard.model import *
def train(spark, input: str, model_path: str):
    df = spark.read.csv(input, header=True, inferSchema=True)
    pipeline, evaluator, cv = get_model()
    model = cv.fit(df)
    print(f"Best model: {model.bestModel}")
    print(f"Best model params: {model.bestModel.stages[-1].extractParamMap()}")
    print(f"Best model evaluator: {model.avgMetrics}")
    model.save(model_path)