
from pyspark.sql import SparkSession
from pyspark.sql.types import StringType, BooleanType


def analyze(spark, input_file):
    # Load the data
    data = spark.read.csv(input_file, header=True, inferSchema=True)

    # Print the schema
    print("Schema:")
    data.printSchema()

    # Show the first 5 rows
    print("First 5 rows:")
    data.show(5)

    # Summary statistics
    print("Summary statistics:")
    data.describe().show()

    # Count the number of rows
    print("Number of rows:", data.count())

    # calculate correlation between columns and is_scam
    for col in data.columns:
        if col != "is_scam" and not isinstance(data.schema[col].dataType, StringType) and not isinstance(data.schema[col].dataType, BooleanType):
            print("Correlation between", col, "and is_scam:", data.stat.corr(col, "is_scam"))
    
    # Group by is_scam and count
    print("Number of scams and non-scams:")
    data.groupBy("is_scam").count().show()

    # Group by is_scam and calculate average value
    print("Average value for scams and non-scams:")
    data.groupBy("is_scam").avg("value").show()

    # Group by is_scam and calculate average fee
    print("Average fee for scams and non-scams:")
    data.groupBy("is_scam").avg("fee").show()

    # address with biggest scam value 
    print("Address with biggest scam value:")
    data.filter(data.is_scam == 1).orderBy(data.value.desc()).show(1)

    # address with biggest fee
    print("Address with biggest fee:")
    data.orderBy(data.fee.desc()).show(1)



