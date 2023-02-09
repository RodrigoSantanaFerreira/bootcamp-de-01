from os.path import abspath
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

# setup da aplicação Spark
spark = SparkSession \
    .builder \
    .appName("job-1-spark") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")\
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")\
    .getOrCreate()

# definindo o método de logging da aplicação use INFO somente para DEV [INFO,ERROR]
spark.sparkContext.setLogLevel("ERROR")

def read_csv(bucket, path):
    # lendo os dados do Data Lake
    df = spark.read.format("csv")\
        .option("header", "True")\
        .option("inferSchema","True")\
        .csv(f"{bucket}/{path}")
    # imprime os dados lidos da raw
    print ("\nImprime os dados lidos da raw:")
    print (df.show(5))
    # imprime o schema do dataframe
    print ("\nImprime o schema do dataframe lido da raw:")
    print (df.printSchema())
    return df

def read_delta(bucket, path):
    df = spark.read.format("delta")\
        .load(f"{bucket}/{path}")
    return df

def write_processed(bucket, path, col_partition, data_format, mode):
    print ("\nEscrevendo os dados lidos da raw para delta na processing zone...")
    try:
        df.write.format(data_format)\
            .partitionBy(col_partition)\
            .mode(mode)\
            .save(f"{bucket}/{path}")
        print (f"Dados escritos na processed com sucesso!")
        return 0
    except Exception as err:
        print (f"Falha para escrever dados na processed: {err}")
        return 1

def write_curated(bucket, path, dataframe, data_format, mode):
    # converte os dados processados para parquet e escreve na curated zone
    print ("\nEscrevendo os dados na curated zone...")
    try:
        dataframe.write.format(data_format)\
                .mode(mode)\
                .save(f"{bucket}/{path}")
        print (f"Dados escritos na curated com sucesso!")
        return 0
    except Exception as err:
        print (f"Falha para escrever dados na processed: {err}")
        return 1

def write_redshift(url_jdbc, table_name, dataframe):
    try:
        dataframe.write.format("jdbc")\
                .options(url=url_jdbc,
                        driver='com.amazon.redshift.jdbc42.Driver',
                        user='awsuser',
                        password='U%SlC7*Y807n',
                        dbtable=table_name
                        )\
                .mode('overwrite')\
                .save()
        print (f"Dados escritos no Redshift com sucesso!")
        return 0
    except Exception as err:
        print (f"Falha para escrever dados no Redshift: {err}")
        return 1


def analytics_tables(bucket, dataframe, table_name, flag_write_redshift, url_jdbc):
    # cria uma view para trabalhar com sql
    dataframe.createOrReplaceTempView(table_name)
    # processa os dados conforme regra de negócio
    df_query1 = df.groupBy("name") \
                .agg(sum("circulating_supply").alias("circulating_supply")) \
                .sort(desc("circulating_supply")) \
                .limit(10)
    df_query2 = df.select(col('name'),col('symbol'),col('price'))\
                .sort(desc("price"))\
                .limit(10)
    # imprime o resultado do dataframe criado
    print ("\n Top 10 Cryptomoedas com maior fornecimento de circulação  no mercado\n")
    print (df_query1.show())
    print ("\n Top 10 Cryptomoedas com preços mais altos de 2022\n")
    print (df_query2.show())
    write_curated(f"{bucket}","coins_circulating_supply",df_query1,"delta","overwrite")
    write_curated(f"{bucket}","top10_prices_2022",df_query2,"delta","overwrite")

    if flag_write_redshift == True:
        write_redshift(url_jdbc, "coins_circulating_supply", df_query1)
        write_redshift(url_jdbc,"top10_prices_2022",df_query2)


# Ler dados da raw
df = read_csv('s3a://raw-stack-bootcampde','public/tb_coins/')

# Cria uma coluna de ano para particionar os dados
df = df.withColumn("year", year(df.data_added))

# Processa os dados e escreve na camada processed
write_processed("s3a://processed-stack-bootcampde","tb_coins","year","delta","overwrite")

# Lear dados da processed e escreve na camada curated.
df = read_delta("s3a://processed-stack-bootcampde","tb_coins")

flag_write_redshift = True
url_jdbc = "jdbc:redshift://redshift-cluster-1.cufcxu0ztur8.us-east-1.redshift.amazonaws.com:5439/dev"
analytics_tables("s3a://curated-stack-bootcampde",df,"tb_coins", flag_write_redshift, url_jdbc)

# para a aplicação
spark.stop()