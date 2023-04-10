"""Lambda function to get download count from GitHub API and save to S3"""

import io
import os
import requests
import boto3
import matplotlib.pyplot as plt
import pandas as pd

URL = os.environ["URL"]
S3_BUCKET = os.environ["S3_BUCKET"]
S3_KEY = os.environ["S3_KEY"]
PUBLIC_GRAPH = os.environ["GRAPH"]


def lambda_handler(event, context):
    """Main function"""
    cur_date, cur_downloads = get_downloads()

    if cur_date is None:
        print("Error parsing date from GitHub API")
        return

    if cur_downloads is None:
        print("Error parsing download count from GitHub API")
        return

    # Get data from S3
    dataframe = get_csv()

    prev_date, prev_downloads = get_date_count(dataframe)

    if prev_date is None:
        print("Error parsing date from S3 object")
        return

    if prev_downloads is None:
        print("Error parsing download count from S3 object")
        return

    # Check if date is the same
    if cur_date == prev_date:
        print(f"Date '{cur_date}' is the same")
        return

    dataframe = append_csv(cur_date, cur_downloads, dataframe)

    if dataframe is None:
        print("Error appending data to dataframe")
        return

    # Create graph
    graph_png = graph(dataframe)

    # Write to S3
    if s3_write(dataframe, graph_png):
        print(f"Data for {cur_date} written to S3")
    else:
        print("Error writing to S3")
        return


def get_downloads():
    """Get data from GitHub API, return date and download count"""
    try:
        data = requests.get(URL, timeout=5).json()
        try:
            # Sum up all download counts for each asset in eacah release
            download_count = sum(
                [
                    asset["download_count"]
                    for release in data
                    for asset in release["assets"]
                ]
            )
        except TypeError:
            print("Error parsing download count from server")
            return None

        try:
            date = data[0]["published_at"][:10]
        except TypeError:
            print("Error parsing date from server")
            return None

        print(f"Date: {date}, Downloads: {download_count}")
        return date, download_count
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        print("Error connecting to the server")
    except (IndexError, KeyError):
        print("Error parsing data from server")
    return None


def get_csv():
    """Read csv, return dataframe"""
    s3 = boto3.resource("s3")
    obj = s3.Object(S3_BUCKET, S3_KEY)
    body = obj.get()["Body"].read()
    dataframe = pd.read_csv(io.BytesIO(body))

    return dataframe


def get_date_count(csv):
    """Read csv, return last row"""
    df = csv.tail(1)

    if df.empty:
        print("CSV is empty")
        return "1970-01-01", 0
    else:
        date = df["date"].to_string(index=False)
        downloads = df["downloads"].to_string(index=False)
        return date, downloads


def append_csv(date, downloads, dataframe):
    """Add data from date and downloads to dataframe. Don't use append because it's no longer supported"""
    try:
        dataframe.loc[len(dataframe)] = [date, downloads]
    except Exception as e:
        print(f"Error appending data to dataframe: {e}")
        return None

    return dataframe


def s3_write(dataframe, graph):
    """Write to dataframe to S3 object"""
    s3 = boto3.resource("s3")
    csv_buffer = io.StringIO()
    dataframe.to_csv(csv_buffer, index=False)
    try:
        s3.Object(S3_BUCKET, S3_KEY).put(Body=csv_buffer.getvalue())
    except Exception as e:
        print(f"Error writing csv to S3: {e}")
        return False

    try:
        s3.Object(S3_BUCKET, PUBLIC_GRAPH).put(Body=graph.getvalue())
    except Exception as e:
        print(f"Error writing graph to S3: {e}")
        return False


def graph(dataframe):
    """Create graph from dataframe, return graph"""
    plt.plot(dataframe["date"], dataframe["downloads"])
    plt.gcf().autofmt_xdate()
    plt.title("Downloads")
    plt.xlabel("Date")
    plt.ylabel("Downloads")
    # Save graph
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)

    return buf


if __name__ == "__main__":
    lambda_handler(None, None)
