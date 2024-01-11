start_mosquitto:
	./mosquitto/mosquitto_linux -c ./mosquitto/mosquitto.conf

run-script:
	@CURRENT_ENV=$$(conda env list | grep '*' | awk '{print $$1}'); \
	if [ "$$CURRENT_ENV" = "iotplatform" ]; then \
		echo "Current environment is iotplatform. Running python wsgi.py..."; \
		python wsgi.py; \
	else \
		echo "Current environment is not 'iotplatform'. Skipping python wsgi.py."; \
	fi
