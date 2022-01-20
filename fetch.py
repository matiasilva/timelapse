#!/usr/bin/env python

# fetches data from the sunrise-sunset API once a day

import yaml
import requests

API_ENDPOINT = "https://api.sunrise-sunset.org/json?lat={}&lng={}&formatted=0"


def main():
    # get coords
    with open("config.yaml", "r") as f:
        try:
            config = yaml.safe_load(f)
        except yaml.YAMLError as exc:
            print(exc)
    lat = config.get("latitude")
    long = config.get("longitude")

    # make request
    endpoint = API_ENDPOINT.format(lat, long)
    data = requests.get(endpoint)
    is_valid = data.status_code == requests.codes.ok
    data_json = data.json()

    # save data
    if data_json.get("status") == "OK" and is_valid:
        results = data_json.get("results")
        to_write = {"sunset": results.get(
            "sunset"),  "sunrise": results.get("sunrise")}
        with open("db.yaml", "w") as f:
            try:
                yaml.dump(to_write, f)
            except yaml.YAMLError as exc:
                print(exc)
    return None


if __name__ == "__main__":
    main()
