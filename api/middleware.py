import json
import time
import uuid

import redis
import settings


db = redis.Redis(host=settings.REDIS_IP,port=settings.REDIS_PORT,db=0)

def model_predict(image_name):
    """
    Receives an image name and queues the job into Redis.
    Will loop until getting the answer from our ML service.

    Parameters
    ----------
    image_name : str
        Name for the image uploaded by the user.

    Returns
    -------
    prediction, score : tuple(str, float)
        Model predicted class as a string and the corresponding confidence
        score as a number.
    """
    prediction = None
    score = None

    job_id = str(uuid.uuid4())

    job_data = {
        "id": job_id,
        "image_name": image_name
    }

    db.lpush(
        settings.REDIS_QUEUE,
        json.dumps(job_data)
    )

    # Loop until we received the response from our ML model
    while True:

        output = db.get(job_id)

        # Check if the text was correctly processed by our ML model
        # Don't modify the code below, it should work as expected
        if output is not None:
            output = json.loads(output.decode("utf-8"))
            prediction = output["prediction"]
            score = output["score"]

            db.delete(job_id)
            break

        # Sleep some time waiting for model results
        time.sleep(settings.API_SLEEP)

    return prediction, score
