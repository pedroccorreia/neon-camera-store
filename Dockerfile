FROM python:3.9

# Expose port you want your app on
EXPOSE 8080

# streamlit apps need to run in a different file than the root
RUN mkdir app/

# Upgrade pip and install requirements
COPY requirements.txt app/requirements.txt
RUN pip3 install -U pip
RUN pip3 install -r app/requirements.txt



# Copy app code and set working directory
COPY images app/images
COPY pages app/pages
COPY data app/data
COPY Home.py app/Home.py
COPY constants.py app/constants.py
COPY embedding_prediction_client.py app/embedding_prediction_client.py
COPY gcs_helper.py app/gcs_helper.py
COPY state_management.py app/state_management.py
COPY ui_constants.py app/ui_constants.py
COPY utils.py app/utils.py
COPY vector_search.py app/vector_search.py
WORKDIR app/

# Run
ENTRYPOINT ["streamlit", "run", "Home.py", "--server.port=8080", "--server.address=0.0.0.0"]