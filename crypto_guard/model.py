
from pyspark.sql import SparkSession
from pyspark.sql import DataFrame
from pyspark.ml import Pipeline
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml.tuning import ParamGridBuilder, CrossValidator

def create_dataframe_from_dataset(csv_path: str) -> DataFrame:
    spark = SparkSession.builder.appName("crypto_guard").getOrCreate()
    df = spark.read.csv(csv_path, header=True, inferSchema=True)
    return df

def get_model():
    """
    This function returns spark ML Pipeline consisting of:

    - Feature transformers from dataframe in order to prepare data for model from transaction dataframe
    - Model that predicts if transaction is malicious or not based on features
    - model validation pipeline that evaluates model performance using cross validation
    """
    feature_columns = ['value', 'time', 'block_height', 'spent', 'ver', 'vin_sz', 'vout_sz', 'size', 'weight', 'fee', 'lock_time', 'tx_index', 'double_spend', 'block_index']
    assembler = VectorAssembler(inputCols=feature_columns, outputCol="features")
    rf = RandomForestClassifier(labelCol="is_scam", featuresCol="features")
    pipeline = Pipeline(stages=[assembler, rf])
    paramGrid = ParamGridBuilder().addGrid(rf.numTrees, [10, 100]).build()
    evaluator = BinaryClassificationEvaluator(labelCol="is_scam")
    cv = CrossValidator(estimator=pipeline, estimatorParamMaps=paramGrid, evaluator=evaluator, numFolds=5)
    return (pipeline, evaluator, cv)