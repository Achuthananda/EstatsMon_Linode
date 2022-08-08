docker stop prometheus
docker rm prometheus
docker stop grafana
docker rm grafana
docker run -d --name prometheus -p 9090:9090 -v prometheus.yml:/etc/prometheus/prometheus.yml prom/prometheus --config.file=/etc/prometheus/prometheus.yml
docker run -d --name grafana -p 3000:3000 grafana/grafana
python3 exporter.py

