# Ath

Ath, a distributed app for CSV ingestion of software development PR review/merge times data.



https://user-images.githubusercontent.com/46817915/222345848-af1a80e6-bff6-446f-b44e-76571f73b1ec.mp4



Services:

- [api](https://github.com/tiangolo/fastapi): fastpi app
- [minio](https://github.com/minio/minio): s3 compatible data store
- [tusd](https://github.com/tus/tusd): resumable file uploads
- [huey](https://github.com/coleifer/huey) task queue/worker: cpu bound tasks: csv parsing + summary stats + plots

Note: csv files are uploaded with [tuspy](https://github.com/tus/tus-py-client) client, see instructions below.

## Deps

- docker/docker-compose
- make

## Build images

    make build

## Run server

    make run

## Run migrations

    make alembic-upgrade-head

## OpenAPI

### json spec

    Check openapi schema at: <http://127.0.0.1:9000/api/openapi.json>

### api docs

    Check openapi generated docs at: <http://127.0.0.1:9000/api/docs>

## Upload csv

    make cli-upload-csv 'data/t1.csv'
    make cli-upload-csv 'data/t2.csv'
    make cli-upload-csv 'data/t3.csv'
    # etc

Pushes the csv file to the bucket. Check Makefile for details.
Once the file is uploaded, the csv parser is run in asynchronously (in a huey worker).

## Check sample summary statistics and visualization plots urls

Note that for this particular application the approach of recursively nesting all the resources was taken, but depending on the business requirements each nested resource could have been promoted and be exposed on its respective endpoints.

### Request

    GET "api/v1/samples?skip=0&limit=10"

### Response

```json
  {
    "sample_reads": [
      {
        "started_upload_at": "2023-03-02T01:37:50.773648+00:00",
        "finished_upload_at": null,
        "status": "done",
        "upload_id": "21cf0d7e-6972-4d62-a4fb-66916f308054",
        "file_name": "a98599563cef9886a310caedcf0e27b5",
        "parsing_error": null,
        "id": "31447fc1-fc28-49c4-9747-274aa9146bc1",
        "summary_statistics": {
          "report": {
            "total_num_observations": 96,
            "teams": [
              "Application",
              "Data Service",
              "Platform"
            ],
            "date_interval": {
              "begin": "2023-01-14T00:00:00",
              "end": "2023-02-14T00:00:00"
            },
            "stats": {
              "mean": {
                "review_time": 15486.1,
                "merge_time": 768.9,
                "total_time": 16254.9
              },
              "mode": {
                "review_time": 0,
                "merge_time": 0,
                "total_time": 0
              },
              "median": {
                "review_time": 139,
                "merge_time": 231,
                "total_time": 877.5
              },
              "count": 96
            },
            "per_team": {
              "Application": {
                "mean": {
                  "review_time": 30116.6,
                  "merge_time": 493.9,
                  "total_time": 30610.6
                },
                "mode": {
                  "review_time": 0,
                  "merge_time": 0,
                  "total_time": 0
                },
                "median": {
                  "review_time": 971,
                  "merge_time": 392,
                  "total_time": 1696
                },
                "count": 32
              },
              "Data Service": {
                "mean": {
                  "review_time": 2560.8,
                  "merge_time": 860.8,
                  "total_time": 3421.6
                },
                "mode": {
                  "review_time": 0,
                  "merge_time": 0,
                  "total_time": 0
                },
                "median": {
                  "review_time": 451,
                  "merge_time": 723.5,
                  "total_time": 2223.5
                },
                "count": 32
              },
              "Platform": {
                "mean": {
                  "review_time": 13780.8,
                  "merge_time": 951.9,
                  "total_time": 14732.7
                },
                "mode": {
                  "review_time": 0,
                  "merge_time": 0,
                  "total_time": 0
                },
                "median": {
                  "review_time": 0,
                  "merge_time": 0,
                  "total_time": 0
                },
                "count": 32
              }
            },
            "num_prs_without_review": 44,
            "num_prs_without_ci": 37,
            "num_missing_values": {
              "review_time": 0,
              "merge_time": 0,
              "date": 0,
              "team": 0
            }
          },
          "id": "9cecf07a-3f91-48a0-bb33-a06bcf3ed1b5"
        },
        "visualization": {
          "id": "fbf2d4f5-f717-49fa-99b6-55f1aee0981e",
          "plots": [
            {
              "file_name": "a98599563cef9886a310caedcf0e27b5/merge_time_distribution_no_outliers_violin_plot.png",
              "url": "http://127.0.0.1:53330/plots/a98599563cef9886a310caedcf0e27b5/merge_time_distribution_no_outliers_violin_plot.png",
              "id": "659b3238-cbec-4413-9996-b6ef2f885b55"
            },
            {
              "file_name": "a98599563cef9886a310caedcf0e27b5/review_time_distribution_no_outliers_violin_plot.png",
              "url": "http://127.0.0.1:53330/plots/a98599563cef9886a310caedcf0e27b5/review_time_distribution_no_outliers_violin_plot.png",
              "id": "4a225008-c78c-4c62-9c67-a1033a7821ff"
            },
            {
              "file_name": "a98599563cef9886a310caedcf0e27b5/merge_time_distribution_with_outliers_violin_plot.png",
              "url": "http://127.0.0.1:53330/plots/a98599563cef9886a310caedcf0e27b5/merge_time_distribution_with_outliers_violin_plot.png",
              "id": "602175ad-3824-4cc6-9ba5-dc35c65a80d8"
            },
            {
              "file_name": "a98599563cef9886a310caedcf0e27b5/review_time_distribution_with_outliers_violin_plot.png",
              "url": "http://127.0.0.1:53330/plots/a98599563cef9886a310caedcf0e27b5/review_time_distribution_with_outliers_violin_plot.png",
              "id": "b8758802-5c58-439b-a697-c1b54be4a79d"
            },
            {
              "file_name": "a98599563cef9886a310caedcf0e27b5/num_prs_by_team_no_outliers_pie_chart_plot.png",
              "url": "http://127.0.0.1:53330/plots/a98599563cef9886a310caedcf0e27b5/num_prs_by_team_no_outliers_pie_chart_plot.png",
              "id": "62df6ab9-b676-494c-8c8d-23d436f56a5b"
            },
            {
              "file_name": "a98599563cef9886a310caedcf0e27b5/num_prs_by_team_with_outliers_pie_chart_plot.png",
              "url": "http://127.0.0.1:53330/plots/a98599563cef9886a310caedcf0e27b5/num_prs_by_team_with_outliers_pie_chart_plot.png",
              "id": "c563926f-8cd8-41c0-b297-d0d3450874da"
            },
            {
              "file_name": "a98599563cef9886a310caedcf0e27b5/mean_time_no_outliers_stacked_bar_plot.png",
              "url": "http://127.0.0.1:53330/plots/a98599563cef9886a310caedcf0e27b5/mean_time_no_outliers_stacked_bar_plot.png",
              "id": "1f3a48c9-5239-4092-8861-1009b97242be"
            },
            {
              "file_name": "a98599563cef9886a310caedcf0e27b5/mean_time_with_outliers_stacked_bar_plot.png",
              "url": "http://127.0.0.1:53330/plots/a98599563cef9886a310caedcf0e27b5/mean_time_with_outliers_stacked_bar_plot.png",
              "id": "022d0482-01a9-4d90-b960-0ef5a1c4b118"
            }
          ]
        }
      },
      {
        "started_upload_at": "2023-03-02T01:31:39.599055+00:00",
        "finished_upload_at": null,
        "status": "failed",
        "upload_id": "bdbca1d5-649a-484a-a858-567d41cc8a49",
        "file_name": "77c210393825d1c694f4cde8cbb9cd67",
        "parsing_error": "In case of an error this field gets populated! And 'status' set with 'failed'",
        "id": "ac737a94-bed5-444e-a743-8d134fb75344",
        "summary_statistics": null,
        "visualization": null
      }
    ]
  }
```

## Navigate S3 csv and plots buckets

    Open browser at "http://127.0.0.1:53331/browser"
    Default user and password: `ath12345`

## Run tests

  make run-test

Note: at the moment only a couple of tests is implemented. These address authentication. The csv upload and processing flow tests should be implemented next.
