# Используем базовый образ quay.io/debezium/connect:latest
FROM quay.io/debezium/connect:latest

# Создаем директории для плагинов Kafka Connect и копируем jar и properties файлы
RUN mkdir -p /kafka/sink/plugins /kafka/sink
COPY build/clickhouse-kafka-connect-v1.0.17-confluent.jar /kafka/sink/plugins/
COPY build/clickhouse-sink.properties /kafka/sink/

# Добавляем путь к плагинам в файл connect-standalone.properties
RUN echo "plugin.path=kafka/plugins/" >> /kafka/config/connect-standalone.properties